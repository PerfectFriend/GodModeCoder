# Tor Hidden Service Configuration for ParanoidX (2026-08-06)

## The Problem
Configuring Tor hidden services in Docker containers to reach services on the WSL2 host requires understanding the IP address mapping:

- **Docker gateway IP**: `172.18.0.1` — Docker's internal gateway for the `paranoidx_default` network
- **WSL host IP**: `172.25.101.187` — The WSL2 VM's IP on the Windows host (changes on reboot)
- **Container IPs**: `172.18.0.x` — Individual containers (e.g., coturn at `172.18.0.5`)

## HiddenServicePort Syntax

Tor's `HiddenServicePort` directive format:
```
HiddenServicePort VIRTUAL_PORT TARGET_ADDRESS:TARGET_PORT
```

Where:
- `VIRTUAL_PORT` — port clients connect to on the .onion (e.g., 80 for HTTP)
- `TARGET_ADDRESS:TARGET_PORT` — where Tor forwards the connection

## Critical Rules

### 1. SocksPort Must Be 0 with HiddenServiceNonAnonymousMode
```torrc
HiddenServiceNonAnonymousMode 1
HiddenServiceSingleHopMode 1
SocksPort 0  # REQUIRED — non-anonymous mode incompatible with client SOCKS
```

If `SocksPort 9050` is set with `HiddenServiceNonAnonymousMode 1`, Tor fails with:
```
HiddenServiceNonAnonymousMode is incompatible with using Tor as an anonymous client.
Please set Socks/Trans/NATD/DNSPort to 0, or revert HiddenServiceNonAnonymousMode to 0.
```

### 2. Target Address Must Be Reachable FROM the Tor Container
The Tor container runs in the `paranoidx_default` Docker network. It can reach:
- Other containers by service name: `ParanoidX-smp-server:5223`
- Docker gateway: `172.18.0.1:PORT` (for host services)
- **NOT** `host.docker.internal` (not available in this Docker setup)
- **NOT** WSL host IP directly (unless explicitly added to container's /etc/hosts)

### 3. Working Configuration for ParanoidX Services

```torrc
# Dashboard (Go server on WSL host - use Docker gateway)
HiddenServiceDir /var/lib/tor/dashboard
HiddenServicePort 80 172.18.0.1:8080

# SMP (messaging relay - container in same network)
HiddenServiceDir /var/lib/tor/smp
HiddenServicePort 5223 ParanoidX-smp-server:5223

# XFTP (file & media relay - container in same network)
HiddenServiceDir /var/lib/tor/xftp
HiddenServicePort 443 ParanoidX-xftp-server:443

# ICE / TURN server (coturn container IP)
HiddenServiceDir /var/lib/tor/ice
HiddenServicePort 3478 172.18.0.5:3478
HiddenServicePort 5349 172.18.0.5:5349

# Auditor Dashboard (same as main dashboard)
HiddenServiceDir /var/lib/tor/auditor
HiddenServicePort 80 172.18.0.1:8080
```

## Verification Commands

```bash
# Check Tor container status
docker ps --filter "name=ParanoidX-tor" --format "{{.Status}}"

# Read .onion hostname (persisted on host)
cat /mnt/c/ParanoidX/docker/tor/hidden_services/dashboard/hostname

# Test .onion from WSL (requires Tor SOCKS proxy on 9050)
# Note: Tor container runs with SocksPort 0, so use host Tor or separate client
curl --socks5-hostname 127.0.0.1:9050 http://<hostname>.onion/api/version

# Verify Tor logs for config errors
docker logs ParanoidX-tor --tail 50
```

## Common Failure Patterns

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Unparseable address in hidden service port configuration` | Invalid target format | Use `IP:PORT` or `hostname:PORT` |
| `HiddenServiceNonAnonymousMode is incompatible...` | SocksPort != 0 | Set `SocksPort 0` |
| Container restarting | Config validation fails | Check `docker logs ParanoidX-tor` |
| Connection refused | Wrong IP for target | Use Docker gateway (172.18.0.1) for host services |

## IP Address Discovery

```bash
# Docker gateway (from WSL host)
docker network inspect paranoidx_default | grep Gateway

# WSL host IP (from inside WSL)
ip addr show eth0 | grep inet

# Container IPs
docker inspect ParanoidX-coturn --format "{{.NetworkSettings.Networks.paranoidx_default.IPAddress}}"
```

## Important Notes

1. **WSL host IP changes on reboot** — The `172.25.101.187` is dynamic. The Docker gateway `172.18.0.1` is stable within the Docker network.

2. **Dashboard on host via Docker gateway** — The Go server listens on `0.0.0.0:8080` in WSL. The Tor container reaches it via Docker's gateway IP `172.18.0.1:8080`.

3. **Persistent keys** — Hidden service keys stored in `/mnt/c/ParanoidX/docker/tor/hidden_services/<name>/` survive container restarts.

4. **SOCKS proxy for testing** — The Tor container runs `SocksPort 0` (no client proxy). To test .onion from WSL, run a separate Tor client with `SocksPort 9050` or use the host Windows Tor if installed.