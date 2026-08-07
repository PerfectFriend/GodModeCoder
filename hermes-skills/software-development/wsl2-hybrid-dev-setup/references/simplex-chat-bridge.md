# SimpleX Chat Bridge — WebSocket Connection Guide

## Problem
The ParanoidX Go server expects a WebSocket connection at `ws://localhost:17225` to a `simplex-chat-island` CLI process. Without this, the bridge status shows "disconnected".

## Root Cause
The Go server's `internal/bridge/bridge.go` expects a native `simplex-chat-island` binary that runs a WebSocket server on port 17225. The standard `simplex-chat` CLI (v7.0.0.11) does NOT have a `--ws-url` flag, but it DOES have a `-p` / `--chat-server-port` flag to run a WebSocket server.

## Solution

### 1. Install simplex-chat CLI
```bash
mkdir -p ~/bin
cd /tmp
wget -q https://github.com/simplex-chat/simplex-chat/releases/latest/download/simplex-chat-ubuntu-24_04-x86_64 -O simplex-chat
chmod +x simplex-chat
mv simplex-chat ~/bin/
```

### 2. Create required symlink
```bash
ln -sf ~/bin/simplex-chat ~/bin/simplex-chat-island
```

### 3. Run CLI in background with WebSocket server on port 17225
```bash
mkdir -p ~/simplex-island-db
nohup ~/bin/simplex-chat-island -p 17225 --database ~/simplex-island-db/island.db > ~/simplex-island.log 2>&1 &
```

### 4. Verify bridge connection
```bash
# Check CLI is running
ps aux | grep simplex-chat

# Check WebSocket port
nc -z localhost 17225

# Check Go server logs for bridge connection
grep "bridge" ~/paranoidx.log
```

## Verification
Once running, the Go server should log:
```json
{"level":"INFO","msg":"[bridge] connected to simplex-chat CLI via WS"}
{"level":"INFO","msg":"bridge connected"}
```

And the bridge status in `/api/admin/info` will show:
```json
"bridge": {"healthy": true, "detail": "connected, 0 reconnects"}
```

## Notes
- The `simplex-chat-island` binary name is hardcoded in `internal/bridge/bridge.go`
- The bridge auto-reconnects with exponential backoff
- If the CLI crashes, the Go server will keep retrying
- The `-p 17225` flag is critical — it tells simplex-chat to run its WebSocket server on port 17225
- Database is created automatically at the specified path

## systemd Auto-Start (Optional)
Create `~/.config/systemd/user/simplex-island.service`:
```ini
[Unit]
Description=Simplex Chat Island Bridge
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/home/tomas/bin/simplex-chat-island -p 17225 --database /home/tomas/simplex-island-db/island.db
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

Enable:
```bash
systemctl --user daemon-reload
systemctl --user enable simplex-island.service
systemctl --user start simplex-island.service
```

## Version Compatibility
- simplex-chat v7.0.0+ required for WebSocket server support (`-p` flag)
- Go server expects `simplex-chat-island` binary name (symlink from `simplex-chat`)
- Database format: SQLite (created automatically)