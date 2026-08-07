#!/bin/bash
# /home/tomas/bin/sync-v2ray-configs.sh
# V2Ray Config Auto-Sync Script
# Runs via cron to sync V2Ray configs from v2rayNG or git repo

set -euo pipefail

V2RAY_DIR="$HOME/bin/v2ray"
LOG_FILE="$HOME/sync-v2ray.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

cd "$V2RAY_DIR" || {
    log "ERROR: V2Ray directory not found: $V2RAY_DIR"
    exit 1
}

# Option 1: Git repo (if configs in git)
if [ -d .git ]; then
    log "Syncing V2Ray configs from git..."
    if git pull origin main 2>&1 | tee -a "$LOG_FILE"; then
        log "Git pull successful"
        CHANGED=1
    else
        log "Git pull failed or no changes"
    fi
fi

# Option 2: Direct from v2rayNG repo (fallback)
if [ -z "${CHANGED:-}" ]; then
    log "Fetching from v2rayNG repo..."
    if wget -q https://raw.githubusercontent.com/2dust/v2rayNG/master/config.json -O config.json.new 2>&1 | tee -a "$LOG_FILE"; then
        if [ -f config.json.new ] && [ -s config.json.new ]; then
            mv config.json.new config.json
            log "Downloaded config from v2rayNG"
            CHANGED=1
        else
            log "Downloaded config empty or invalid"
        fi
    else
        log "Failed to download from v2rayNG"
    fi
fi

# Restart xray if config changed
if [ -n "${CHANGED:-}" ]; then
    log "Config changed, restarting xray..."
    pkill -f "xray run" 2>/dev/null || true
    sleep 1
    nohup ~/bin/v2ray/xray run -c ~/bin/v2ray/config.json > ~/xray.log 2>&1 &
    log "Xray restarted"
else
    log "No config changes, skipping restart"
fi

log "Sync complete"