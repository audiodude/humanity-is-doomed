#!/usr/bin/env bash
# Regenerates every research dataset: SVGs and decompile outcomes, the
# space / combat / progression / route metrics of the id maps and of every
# official set, the per-(game, flavor) summary and the reception correlations.
# Run from the repo root; see docs/metrics-data.md. About 20 minutes.
set -euo pipefail
cd "$(dirname "$0")/../.."
M=scripts/metrics
SETS=$(python3 -c "import sys; sys.path.insert(0, '$M'); import doomwad; print(' '.join(doomwad.SETS))")

python3 $M/map_svgs.py                      # first: writes data/metrics/decompile_status.csv
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
