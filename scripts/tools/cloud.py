"""cloud.py: run explorer checks on one AWS Spot instance instead of this machine.

    python3 scripts/tools/cloud.py run NAME --commit C [--commit C2] [--idmaps] [--nukage]
                                   [--rescore] [--plays FOLDER,...] [--jobs FILE] [--hours 2.5]
    python3 scripts/tools/cloud.py resume NAME    # after this machine lost power or the run was killed
    python3 scripts/tools/cloud.py report NAME    # exits per commit, side by side
    python3 scripts/tools/cloud.py cleanup NAME   # terminate the instance, delete its key pair and security group

`run` launches a 96-vCPU Spot instance (the first of TYPES with capacity),
uploads the repo (a git bundle, checked out at each commit), the IWADs from
.env and the blind plays (~/.local/share/playtest/plays), runs the
jobs about 90 at a time, fetches the results, and deletes the instance, its
key pair and its security group. The instance also shuts itself down (which
terminates a Spot instance) after --hours, whatever happens here. State is kept
in ~/.cache/playtest/cloud/NAME/, so `resume` picks a run up after a power cut.

Job sets, for each --commit:
  --idmaps   the explorer on every id map whose exit isn't a boss death, seeds 1-3
  --nukage   the six NUKAGE maps without a boss gate, seeds 1-3
  --rescore  compare.py on every blind play not spoiled; the compare-<commit>/
             folders (and a first score, for a play that had none) are copied
             back into the local plays folder
  --plays    the explorer, seeds 1-3, on the map of each named play folder
  --jobs     extra lines: NAME<TAB>COMMIT<TAB>COMMAND, run with bash in a scratch
             folder; $PY (uv run with vizdoom), $TREE (the commit's files),
             $PLAYS, $DOOM_WAD and $DOOM2_WAD are set; output goes to NAME.txt

Results land in ~/.cache/playtest/cloud/NAME/results/: one text file per job,
named SET-COMMIT-.... Needs the AWS CLI
signed in (`aws login`), ssh, and git. About $1 an hour of instance time.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYS = os.path.expanduser("~/.local/share/playtest/plays")
HOME = os.path.expanduser("~/.cache/playtest/cloud")
TYPES = ["c6i.24xlarge", "c6a.24xlarge", "c7i.24xlarge", "c7a.24xlarge"]
PARALLEL = 90
ID_MAPS = [f"E{e}M{m}" for e in range(1, 5) for m in range(1, 10)] + [f"MAP{m:02d}" for m in range(1, 33)]
BOSS_EXITS = {"E1M8", "E2M8", "E3M8", "E4M6", "E4M8", "MAP07", "MAP30"}
NUKAGE = ["outskirts", "crossing", "tower", "undercurrent", "drain", "lockdown"]
SEEDS = (1, 2, 3)

REMOTE = r"""#!/bin/bash
# On the instance: check out each commit (a git checkout, so compare.py names
# its folders compare-<commit>), unpack the plays, then run jobs.tsv, PARALLEL at a time.
cd ~/batch
curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1
export PATH=$HOME/.local/bin:$PATH
mkdir -p trees results run ~/.local/share/playtest
for c in $(cat commits.txt); do git clone -q repo.bundle trees/$c && git -C trees/$c checkout -q $c
  printf 'DOOM_WAD=%s\nDOOM2_WAD=%s\n' ~/batch/DOOM.WAD ~/batch/DOOM2.WAD > trees/$c/.env; done
[ -f plays.tar ] && tar -xf plays.tar -C ~/.local/share/playtest
first=$(ls -d trees/* | head -1); (cd run && uv run -q --project ~/batch/$first --with vizdoom python3 -c "import vizdoom")
job() { name=$1; c=$2; shift 2
  mkdir -p ~/batch/run/$name && cd ~/batch/run/$name
  TREE=~/batch/trees/$c PLAYS=~/.local/share/playtest/plays DOOM_WAD=~/batch/DOOM.WAD DOOM2_WAD=~/batch/DOOM2.WAD \
  PY="uv run -q --project $HOME/batch/trees/$c --with vizdoom" \
    timeout 3600 bash -c "$*" > ~/batch/results/$name.txt.part 2>&1
  mv ~/batch/results/$name.txt.part ~/batch/results/$name.txt; }
export -f job
tr '\t' '\n' < jobs.tsv | xargs -d '\n' -n 3 -P PARALLEL bash -c 'job "$@"' _
tar -czf out.tgz results -C ~/.local/share/playtest \
  $(cd ~/.local/share/playtest && for c in $(cat ~/batch/commits.txt); do ls -d plays/*/compare-$c; done 2>/dev/null) \
  $(cd ~/.local/share/playtest && ls plays/*/meta.json 2>/dev/null)
touch DONE
"""


def sh(*cmd, check=True, capture=True, timeout=None):
    r = subprocess.run(cmd, capture_output=capture, text=True, check=False, timeout=timeout)
    if check and r.returncode:
        raise SystemExit(f"failed: {' '.join(cmd)}\n{r.stderr.strip()}")
    return r.stdout.strip() if capture else ""


def aws(*a, check=True):
    return sh("aws", *a, "--output", "text", check=check)


def env_iwads():
    vals = {}
    with open(os.path.join(ROOT, ".env")) as f:
        for line in f:
            m = re.match(r"\s*(DOOM_WAD|DOOM2_WAD)\s*=\s*(.+?)\s*$", line)
            if m:
                vals[m[1]] = os.path.expanduser(m[2].strip("\"'"))
    return vals["DOOM_WAD"], vals["DOOM2_WAD"]


def pool_plays():
    out = []
    for path in sorted(glob.glob(os.path.join(PLAYS, "*", "meta.json"))):
        with open(path) as f:
            meta = json.load(f)
        if "pool" in meta and not meta.get("spoiled"):
            out.append((os.path.basename(os.path.dirname(path)), meta))
    return out


def jobs(args):
    """Job lines (name, commit, command) for the sets asked for."""
    out = []
    for c in args.commit:
        if args.rescore:   # the longest jobs first
            out += [(f"rescore-{c}-{f}", c, f"$PY $TREE/scripts/tools/compare.py $PLAYS/{f}") for f, _m in pool_plays()]
        for f in args.plays:
            with open(os.path.join(PLAYS, f, "meta.json")) as fh:
                meta = json.load(fh)
            wads = " ".join(f"$PLAYS/{f}/{w}" for w in meta["wads"])
            out += [(f"plays-{c}-{f}-{s}", c, f"$PY $TREE/scripts/tools/playtest.py {wads} {meta['map']} --explore "
                     f"--skill {meta['skill']} --seed {s}") for s in SEEDS]
        if args.idmaps:
            for m in ID_MAPS:
                if m in BOSS_EXITS:
                    continue
                iw = "$DOOM_WAD" if m.startswith("E") else "$DOOM2_WAD"
                out += [(f"idmaps-{c}-{m}-{s}", c, f"$PY $TREE/scripts/tools/playtest.py {iw} {m} --iwad {iw} "
                         f"--explore --seed {s}") for s in SEEDS]
        if args.nukage:
            out += [(f"nukage-{c}-{m}-{s}", c, f"$PY $TREE/scripts/tools/playtest.py nukage_{m} --explore --seed {s}")
                    for m in NUKAGE for s in SEEDS]
    if args.jobs:
        with open(args.jobs) as f:
            out += [tuple(line.rstrip("\n").split("\t", 2)) for line in f if line.strip()]
    return out


def save(d, state):
    with open(os.path.join(d, "state.json"), "w") as f:
        json.dump(state, f, indent=1)


def ssh_args(d, state):
    return ["-i", os.path.join(d, "key.pem"), "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=accept-new", "-o", f"UserKnownHostsFile={os.path.join(d, 'known_hosts')}"]


def remote(d, state, cmd, timeout=600, check=True):
    return sh("ssh", *ssh_args(d, state), f"ubuntu@{state['host']}", cmd, check=check, timeout=timeout)


def launch(d, state, hours):
    name = f"explorer-{state['name']}"
    with open(os.path.join(d, "key.pem"), "w") as f:
        f.write(aws("ec2", "create-key-pair", "--key-name", name, "--query", "KeyMaterial"))
    os.chmod(os.path.join(d, "key.pem"), 0o600)
    state["key"] = name
    save(d, state)
    vpc = aws("ec2", "describe-vpcs", "--filters", "Name=is-default,Values=true", "--query", "Vpcs[0].VpcId")
    state["sg"] = aws("ec2", "create-security-group", "--group-name", name, "--vpc-id", vpc, "--query", "GroupId",
                      "--description", "temporary explorer batch - ssh from one IP")
    save(d, state)
    ip = urllib.request.urlopen("https://checkip.amazonaws.com", timeout=10).read().decode().strip()
    aws("ec2", "authorize-security-group-ingress", "--group-id", state["sg"], "--protocol", "tcp", "--port", "22",
        "--cidr", f"{ip}/32")
    ami = aws("ssm", "get-parameter", "--name",
              "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id",
              "--query", "Parameter.Value")
    for itype in TYPES:
        r = subprocess.run(["aws", "ec2", "run-instances", "--image-id", ami, "--instance-type", itype,
                            "--key-name", name, "--security-group-ids", state["sg"],
                            "--instance-market-options",
                            "MarketType=spot,SpotOptions={SpotInstanceType=one-time,"
                            "InstanceInterruptionBehavior=terminate}",
                            "--metadata-options", "HttpTokens=required",
                            "--block-device-mappings",
                            "DeviceName=/dev/sda1,Ebs={VolumeSize=30,VolumeType=gp3,DeleteOnTermination=true}",
                            "--tag-specifications", f"ResourceType=instance,Tags=[{{Key=Name,Value={name}}}]",
                            "--query", "Instances[0].InstanceId", "--output", "text"],
                           capture_output=True, text=True, check=False)
        if r.returncode == 0:
            state["id"], state["type"] = r.stdout.strip(), itype
            break
        print(f"  {itype}: {r.stderr.strip().splitlines()[-1][:120]}")
    else:
        raise SystemExit("no instance type had Spot capacity")
    save(d, state)
    aws("ec2", "wait", "instance-running", "--instance-ids", state["id"])
    state["host"] = aws("ec2", "describe-instances", "--instance-ids", state["id"],
                        "--query", "Reservations[0].Instances[0].PublicIpAddress")
    save(d, state)
    print(f"instance {state['id']} ({state['type']}) at {state['host']}", flush=True)
    for _ in range(60):
        if subprocess.run(["ssh", *ssh_args(d, state), f"ubuntu@{state['host']}", "true"],
                          capture_output=True, check=False).returncode == 0:
            break
        time.sleep(5)
    # A Spot instance terminates when it shuts down: this is the backstop.
    remote(d, state, f"sudo shutdown -h +{int(hours * 60)} >/dev/null 2>&1; mkdir -p ~/batch")


def upload(d, state, args):
    up = os.path.join(d, "upload")
    os.makedirs(up, exist_ok=True)
    subprocess.run(["git", "-C", ROOT, "bundle", "create", "-q", os.path.join(up, "repo.bundle"), "--all"], check=True)
    with open(os.path.join(up, "commits.txt"), "w") as f:
        f.write("\n".join(args.commit) + "\n")
    doom, doom2 = env_iwads()
    shutil.copy(doom, os.path.join(up, "DOOM.WAD"))
    shutil.copy(doom2, os.path.join(up, "DOOM2.WAD"))
    if args.rescore or args.plays:
        with tarfile.open(os.path.join(up, "plays.tar"), "w") as t:
            t.add(PLAYS, arcname="plays")
    with open(os.path.join(up, "jobs.tsv"), "w") as f:
        f.writelines("\t".join(j) + "\n" for j in state["jobs"])
    with open(os.path.join(up, "run.sh"), "w") as f:
        f.write(REMOTE.replace("PARALLEL", str(PARALLEL)))
    sh("scp", "-q", *ssh_args(d, state), *glob.glob(os.path.join(up, "*")), f"ubuntu@{state['host']}:batch/",
       timeout=1800)
    remote(d, state, "sudo apt-get -qq update >/dev/null 2>&1; "
                     "sudo apt-get -qq install -y libsdl2-2.0-0 libgl1 >/dev/null 2>&1; "
                     "cd ~/batch && chmod +x run.sh && (setsid nohup ./run.sh > run.log 2>&1 < /dev/null &)",
           timeout=900)
    shutil.rmtree(up)


def wait_and_fetch(d, state):
    total = len(state["jobs"])
    last = -1
    while True:
        r = subprocess.run(["ssh", *ssh_args(d, state), f"ubuntu@{state['host']}",
                            "test -f ~/batch/DONE && echo DONE; ls ~/batch/results/*.txt 2>/dev/null | wc -l"],
                           capture_output=True, text=True, check=False, timeout=60)
        if r.returncode == 255:
            print("instance unreachable (gone?)", flush=True)
            break
        lines = r.stdout.split()
        if "DONE" in lines:
            break
        n = int(lines[-1]) if lines else 0
        if n != last:
            print(f"  {time.strftime('%H:%M')} {n}/{total} jobs done", flush=True)
            last = n
        time.sleep(30)
    else:
        return
    if "DONE" not in r.stdout:
        return
    sh("scp", "-q", *ssh_args(d, state), f"ubuntu@{state['host']}:batch/out.tgz", os.path.join(d, "out.tgz"),
       timeout=1800)
    res = os.path.join(d, "results")   # the archive holds results/ and plays/
    shutil.rmtree(res, ignore_errors=True)
    with tarfile.open(os.path.join(d, "out.tgz")) as t:
        t.extractall(d, filter="data")
    os.remove(os.path.join(d, "out.tgz"))
    merge_plays(d)
    state["fetched"] = True
    save(d, state)
    print(f"results in {res}", flush=True)


def merge_plays(d):
    """Copy the instance's compare-<commit>/ folders into the local plays, and
    a first score into a play's meta.json that had none."""
    for folder in glob.glob(os.path.join(d, "plays", "*")):
        name = os.path.basename(folder)
        here = os.path.join(PLAYS, name)
        if not os.path.isdir(here):
            continue
        for cmp_dir in glob.glob(os.path.join(folder, "compare-*")):
            dst = os.path.join(here, os.path.basename(cmp_dir))
            if os.path.exists(os.path.join(cmp_dir, "scores.json")):
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(cmp_dir, dst)
        with open(os.path.join(folder, "meta.json")) as f:
            theirs = json.load(f)
        with open(os.path.join(here, "meta.json")) as f:
            ours = json.load(f)
        if "first" in theirs and "first" not in ours:
            ours["first"] = theirs["first"]
            with open(os.path.join(here, "meta.json"), "w") as f:
                json.dump(ours, f, indent=1)
    shutil.rmtree(os.path.join(d, "plays"), ignore_errors=True)


def cleanup(d, state):
    if state.get("id"):
        aws("ec2", "terminate-instances", "--instance-ids", state["id"], check=False)
        aws("ec2", "wait", "instance-terminated", "--instance-ids", state["id"], check=False)
    if state.get("sg"):
        aws("ec2", "delete-security-group", "--group-id", state["sg"], check=False)
    if state.get("key"):
        aws("ec2", "delete-key-pair", "--key-name", state["key"], check=False)
    for f in ("key.pem", "known_hosts"):
        if os.path.exists(os.path.join(d, f)):
            os.remove(os.path.join(d, f))
    state["cleaned"] = True
    save(d, state)
    print("instance, key pair and security group deleted", flush=True)


def report(d):
    res = os.path.join(d, "results")
    runs = {}
    for f in glob.glob(os.path.join(res, "*.txt")):
        name = os.path.basename(f)[:-4]
        kind, commit, rest = name.split("-", 2)
        if kind == "rescore":
            continue
        what, seed = rest.rsplit("-", 1)
        with open(f) as fh:
            text = fh.read()
        m = re.search(r"^EXITED at (\d+):(\d+)", text, re.M)
        runs.setdefault((kind, what), {}).setdefault(commit, {})[int(seed)] = \
            int(m[1]) * 60 + int(m[2]) if m else None
    commits = sorted({c for v in runs.values() for c in v})
    clock = lambda t: "-" if t is None else f"{t // 60}:{t % 60:02d}"   # noqa: E731
    for kind in sorted({k for k, _w in runs}):
        print(f"\n{kind}: exits on seeds {'/'.join(map(str, SEEDS))}")
        totals = {c: [0, 0] for c in commits}
        for (k, what), by in sorted(runs.items()):
            if k != kind:
                continue
            cells = []
            for c in commits:
                ts = [by.get(c, {}).get(s) for s in SEEDS]
                totals[c][0] += all(t is not None for t in ts)
                totals[c][1] += ts[0] is not None
                cells.append(f"{'/'.join(clock(t) for t in ts):<20}")
            print(f"  {what:<34}" + "".join(cells))
        print(f"  {'all three seeds / seed 1':<34}" + "".join(f"{f'{a} / {b}':<20}" for a, b in totals.values()))
    if commits:
        print("\ncolumns: " + ", ".join(commits))


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("action", choices=["run", "resume", "report", "cleanup"])
    p.add_argument("name")
    p.add_argument("--commit", action="append", default=[])
    p.add_argument("--idmaps", action="store_true")
    p.add_argument("--nukage", action="store_true")
    p.add_argument("--rescore", action="store_true")
    p.add_argument("--plays", type=lambda s: [x for x in s.split(",") if x], default=[])
    p.add_argument("--jobs")
    p.add_argument("--hours", type=float, default=2.5, help="the instance shuts itself down after this (default 2.5)")
    args = p.parse_args()
    d = os.path.join(HOME, args.name)
    if args.action == "report":
        return report(d)
    if args.action == "run":
        if os.path.exists(os.path.join(d, "state.json")):
            raise SystemExit(f"{d} exists: use resume, cleanup, or another name")
        if not args.commit:
            p.error("give --commit")
        args.commit = [sh("git", "-C", ROOT, "rev-parse", "--short", c) for c in args.commit]
        os.makedirs(d, exist_ok=True)
        state = dict(name=args.name, commits=args.commit, jobs=jobs(args), started=time.strftime("%F %T"))
        if not state["jobs"]:
            p.error("no jobs: give --idmaps, --nukage, --rescore, --plays or --jobs")
        save(d, state)
        print(f"{len(state['jobs'])} jobs at {', '.join(args.commit)}", flush=True)
    else:
        with open(os.path.join(d, "state.json")) as f:
            state = json.load(f)
    try:
        if args.action == "run":
            launch(d, state, args.hours)
            upload(d, state, args)
        if args.action in ("run", "resume") and not state.get("fetched") and state.get("host"):
            wait_and_fetch(d, state)
    finally:
        if args.action != "resume" or state.get("fetched") or args.action == "cleanup":
            cleanup(d, state)
    if state.get("fetched"):
        report(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
