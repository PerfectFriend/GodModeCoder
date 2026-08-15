#!/bin/bash
# /home/tomas/bin/fix-dashboard.sh
# Dashboard Recovery Script
# Restores dashboard.html from Windows source if corrupted

set -euo pipefail

SOURCE="/mnt/c/Users/tomas/ParanoidX-data/dashboard.html"
TARGET="/mnt/c/ParanoidX-data/dashboard.html"
BACKUP="/mnt/c/ParanoidX-data/dashboard.html.backup"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Check if target is corrupted (< 1000 bytes = likely truncated)
if [ -f "$TARGET" ]; then
    SIZE=$(wc -c < "$TARGET")
    if [ "$SIZE" -lt 1000 ]; then
        echo "WARNING: dashboard.html is only ${SIZE} bytes (likely corrupted)"
        CORRUPTED=1
    else
        echo "dashboard.html is ${SIZE} bytes (OK)"
        CORRUPTED=0
    fi
else
    echo "dashboard.html not found at $TARGET"
    CORRUPTED=1
fi

if [ "${CORRUPTED:-0}" -eq 1 ]; then
    echo "Attempting recovery from Windows source..."
    if [ -f "$SOURCE" ]; then
        SOURCE_SIZE=$(wc -c < "$SOURCE")
        if [ "$SOURCE_SIZE" -gt 1000 ]; then
            cp "$SOURCE" "$TARGET"
            echo "Restored dashboard.html from Windows (${SOURCE_SIZE} bytes)"
            
            # Also create backup
            cp "$SOURCE" "$BACKUP"
            echo "Created backup at $BACKUP"
        else
            echo "ERROR: Windows source also corrupted (${SOURCE_SIZE} bytes)"
            exit 1
        fi
    else
        echo "ERROR: Windows source not found at $SOURCE"
        exit 1
    fi
else
    echo "No recovery needed"
fi

# Verify
if [ -f "$TARGET" ]; then
    SIZE=$(wc -c < "$TARGET")
    if [ "$SIZE" -gt 1000 ]; then
        echo "SUCCESS: dashboard.html restored (${SIZE} bytes)"
        exit 0
    fi
fi

echo "FAILED: dashboard.html still corrupted"
exit 1