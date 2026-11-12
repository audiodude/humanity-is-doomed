#!/usr/bin/env bash
# Regenerates every research dataset: SVGs and decompile outcomes, the
# space / combat / progression / route metrics of the id maps, of every
# official set and of the community releases, the per-(game, flavor) summary
# and the reception correlations. Run from the repo root; see
# docs/metrics-data.md. The id and official maps take about 20 minutes; the
# community releases (needs research/fetch_idgames.py's download) take hours.
#   scripts/metrics/run_all.sh                  # everything
#   scripts/metrics/run_all.sh --no-community   # id maps and official sets only
set -euo pipefail
cd "$(dirname "$0")/../.."
M=scripts/metrics
SETS=$(python3 -c "import sys; sys.path.insert(0, '$M'); import doomwad; print(' '.join(doomwad.SETS))")
if [ "${1:-}" != --no-community ] && [ -f research/sources/idgames/manifest.csv ]; then
    SETS="$SETS community"
fi

python3 $M/map_svgs.py doom doom2 $SETS     # first: writes data/metrics/decompile_status.csv
for target in "" $(printf -- "--set=%s " $SETS); do
    args=${target/=/ }
    python3 $M/space_metrics.py $args
    python3 $M/combat_metrics.py $args
    python3 $M/progression_metrics.py $args 2>/dev/null
    python3 $M/route_metrics.py $args 2>/dev/null
done
python3 $M/map_svgs.py --index              # INDEX.md with the fresh measurements
python3 $M/flavor_summary.py
if [ -f research/correlate.py ]; then   # local research tree only
    python3 research/correlate.py
fi
