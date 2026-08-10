# V2Ray Config Auto-Sync — Implementation Guide

## Goal
Automatically sync V2Ray configs from v2rayNG or similar repositories to keep the proxy chain updated with fresh servers.

## Implementation Options

### Option 1: Git Repository Sync (Recommended if you have a config repo)
```bash
#!/bin/bash
# /home/tomas/bin/sync-v2ray-configs.sh
set -euo pipefail

cd ~/bin/v2ray

# Option A: Git repository with configs
if [ -d .git ]; then
    git pull origin main 2>&1 | logger -t v2ray-sync
    systemctl --user restart xray 2>&1 | logger -t v2ray-sync
    exit 0
fi

# Option B: Direct from v2rayNG repo (fallback)
wget -q https://raw.githubusercontent.com/2dust/v2rayNG/master/config.json -O config.json.new
if [ -s config.json.new ]; then
    mv config.json.new config.json
    systemctl --user restart xray 2>&1 | logger -t v2ray-sync
fi
```

### Add to crontab
```bash
# Every 6 hours
0 */6 * * * /home/tomas/bin/sync-v2ray-configs.sh >> /home/tomas/logs/v2ray-sync.log 2>&1
```

### systemd user service alternative (preferred over cron)
```ini
# ~/.config/systemd/user/v2ray-sync.service
[Unit]
Description=V2Ray Config Auto-Sync
After=network-online.target

[Service]
Type=oneshot
ExecStart=/home/tomas/bin/sync-v2ray-configs.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

```ini
# ~/.config/systemd/user/v2ray-sync.timer
[Unit]
Description=Run V2Ray config sync every 6 hours

[Timer]
OnBootSec=5min
OnUnitActiveSec=6h
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now v2ray-sync.timer
```

## v2rayNG Config Format Notes

The v2rayNG config.json uses a specific format:
```json
{
  "log": {"loglevel": "warning"},
  "inbounds": [
    {
      "port": 10808,
      "protocol": "socks",
      "settings": {"auth": "noauth", "udp": true}
    }
  ],
  "outbounds": [
    {"protocol": "freedom", "tag": "direct"},
    {
      "protocol": "vmess",
      "tag": "proxy",
      "settings": {
        "vnext": [
          {
            "address": "server.example.com",
            "port": 443,
            "users": [{"id": "uuid", "alterId": 0, "security": "aes-128-gcm"}]
          }
        ]
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "wsSettings": {"path": "/", "headers": {"Host": "server.example.com"}}
      }
    }
  ]
}
```

## Alternative Sources
- v2rayNG: `https://raw.githubusercontent.com/2dust/v2rayNG/master/config.json`
- Custom repo: `https://raw.githubusercontent.com/YOUR/REPO/main/config.json`
- Subscription URL: Many providers offer base64-encoded subscription URLs

## Validation Before Apply
```bash
# Validate JSON syntax
jq . config.json.new > /dev/null || exit 1

# Check required fields
jq -e '.inbounds[0].port' config.json.new > /dev/null || exit 1
jq -e '.outbounds[] | select(.protocol=="vmess")' config.json.new > /dev/null || exit 1

# Then apply
mv config.json.new config.json
systemctl --user restart xray
```