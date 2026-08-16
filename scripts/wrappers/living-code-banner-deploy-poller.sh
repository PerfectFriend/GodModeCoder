#!/bin/bash
# Banner Deploy Poller Wrapper
# Runs every 5 minutes to check for READY components and deploy banners

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ARTIFACTS_DIR="$PROJECT_ROOT/artifacts"

# Find latest filter report
LATEST_REPORT=$(ls -t "$ARTIFACTS_DIR"/filter_report_cycle_*.json 2>/dev/null | head -1)

if [[ -z "$LATEST_REPORT" ]]; then
    echo "No filter report found"
    exit 0
fi

# Extract cycle number from filename
CYCLE=$(basename "$LATEST_REPORT" | sed -E 's/filter_report_cycle_([0-9]+)\.json/\1/')

echo "[$(date)] Banner Deploy Poller - Cycle $CYCLE"

# Check if there are READY components
READY_COUNT=$(python3 -c "
import json
with open('$LATEST_REPORT') as f:
    data = json.load(f)
ready = [a for a in data.get('analyses', []) if a.get('classification') == 'READY']
print(len(ready))
")

if [[ "$READY_COUNT" -eq 0 ]]; then
    echo "No READY components found"
    exit 0
fi

echo "Found $READY_COUNT READY component(s), deploying banners..."

# Deploy banners for all READY components
cd "$PROJECT_ROOT/scripts"
python3 banner_deploy.py \
    --style brand \
    --auto \
    --cycle "$CYCLE" \
    --langs ru,en,zh \
    --readme \
    --create-repos

echo "[$(date)] Banner deployment complete"