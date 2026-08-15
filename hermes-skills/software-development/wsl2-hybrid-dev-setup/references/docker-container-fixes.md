# Docker Container Fixes — ParanoidX Hybrid Setup

## SMP Server (simplexchat/smp-server)

### 4096-bit RSA Certificate Requirement
**Error**: `Error: unsupported HTTPS credentials, required 4096-bit RSA`

**Fix**: Regenerate certificate with 4096-bit key:
```bash
openssl req -x509 -newkey rsa:4096 -keyout certificates/ParanoidX.local.key -out certificates/ParanoidX.local.crt -days 365 -nodes -subj '/CN=ParanoidX.local'
```

### Fingerprint File Generation
The SMP server generates a fingerprint file at `/etc/opt/simplex/fingerprint` on first run with `--init`. To pre-generate and copy to mounted config:

```bash
# Run once to generate all files
docker run --rm -e ADDR=ParanoidX.local -v /tmp/smp_test:/etc/opt/simplex simplexchat/smp-server:latest --init

# Copy generated files to mounted config directory
cp /tmp/smp_test/fingerprint ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/ca.crt ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/ca.key ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/server.crt ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/server.key ~/ParanoidX/docker/smp_configs/
```

### Certificate Path in Config (smp-server.ini)
**Error**: `Error: no HTTPS credentials: /certificates/ParanoidX.local.crt`

**Root Cause**: Config file uses `cert = /certificates/...` but the Docker volume mounts at `/etc/opt/simplex/certificates/`

**Fix**: Update `smp-server.ini`:
```ini
cert = /etc/opt/simplex/certificates/ParanoidX.local.crt
key = /etc/opt/simplex/certificates/ParanoidX.local.key
```

## Tor Hidden Service

### Container Address for ICE/TURN
**Error**: `Unparseable address in hidden service port configuration`

**Root Cause**: Tor config used bare port `3478` instead of container DNS name `ParanoidX-coturn:3478`

**Fix**: Update `tor/torrc`:
```
HiddenServicePort 3478 ParanoidX-coturn:3478
HiddenServicePort 5349 ParanoidX-coturn:5349
```

### SocksPort Conflict with HiddenServiceNonAnonymousMode
**Error**: `HiddenServiceNonAnonymousMode is incompatible with using Tor as an anonymous client. Please set Socks/Trans/NATD/DNSPort to 0, or revert HiddenServiceNonAnonymousMode to 0.`

**Root Cause**: Tor's `HiddenServiceNonAnonymousMode 1` (used for faster hidden services) conflicts with running a SOCKS5 proxy (`SocksPort 9050`) on the same instance.

**Fix**: Remove `HiddenServiceNonAnonymousMode 1` and `HiddenServiceSingleHopMode 1` from `torrc` if you need the SOCKS5 proxy:
```torrc
# REMOVE these lines:
# HiddenServiceSingleHopMode 1
# HiddenServiceNonAnonymousMode 1

# Keep:
SocksPort 9050
ControlPort 9051
```
This allows Tor to act as both a hidden service provider AND a SOCKS5 proxy for the chain.

### Tor Ports Mapping in Docker Compose
**Issue**: Tor SOCKS5 port 9050 not accessible from host/WSL2

**Fix**: Explicitly map ports in docker-compose.yml:
```yaml
tor:
  ports:
    - "9050:9050"  # SOCKS5 proxy
    - "9051:9051"  # Control port
```

### Tor Dockerfile — Entrypoint for Permissions
The custom Tor Docker image uses an entrypoint that runs as root to fix bind mount permissions, then drops privileges. Ensure Dockerfile has:
```dockerfile
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["tor"]
```

## coturn (TURN/ICE Server)

### Missing Config Files (Directories Instead of Files)
**Problem**: `turnserver.conf`, `turn_cert.pem`, `turn_key.pem` were created as directories, not files

**Fix**: Remove directories and create proper files:

```bash
# Remove directory artifacts
rm -rf turnserver.conf turn_cert.pem turn_key.pem

# Create turnserver.conf
cat > turnserver.conf << 'EOF'
listening-port=3478
tls-listening-port=5349
listening-ip=0.0.0.0
external-ip=auto
realm=paranoidx.local
use-auth-secret
static-auth-secret=paranoidx-turn-secret-2026
cert=/etc/coturn/turn_cert.pem
pkey=/etc/coturn/turn_key.pem
no-udp
no-udp-relay
log-file=stdout
verbose
EOF

# Generate TLS certificates
openssl req -x509 -newkey rsa:2048 -keyout turn_key.pem -out turn_cert.pem -days 365 -nodes -subj '/CN=paranoidx.local'
```

### File Ownership
Ensure coturn config files are owned by the user matching container UID (1000):
```bash
chown -R 1000:1000 coturn/
```

### UDP Relay via Tor
**Issue**: coturn UDP not working through Tor hidden service

**Fix**: Disable UDP in coturn config (TCP only via Tor):
```conf
no-udp
no-udp-relay
```

### Port Mapping for coturn
Map both TCP and UDP ports for TURN/ICE:
```yaml
coturn:
  ports:
    - "3478:3478/tcp"
    - "3478:3478/udp"
    - "5349:5349/tcp"
    - "5349:5349/udp"
```

## V2Ray/Xray (Native & Docker)

### Docker V2Ray — Command Syntax
**Error**: `exec: "run": executable file not found in $PATH`

**Root Cause**: `teddysun/xray` image uses `xray` binary, not `run` as command.

**Fix**: Use explicit command array in docker-compose.yml:
```yaml
v2ray:
  image: teddysun/xray:latest
  command: ["xray", "run", "-c", "/etc/v2ray/config.json"]
```

### Native Xray VMess (Port 10812)
**Issue**: Health check expects native xray VMess on port 10812 for `checkXRay()`

**Fix**: Install native xray and run VMess server:
```bash
mkdir -p ~/bin/v2ray
cd ~/bin/v2ray
wget -q https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip -O xray.zip
unzip -o xray.zip xray
chmod +x xray

cat > ~/bin/v2ray/config.json << 'EOF'
{
  "log": { "loglevel": "warning" },
  "inbounds": [
    {
      "port": 10812,
      "protocol": "vmess",
      "settings": {
        "clients": [
          {
            "id": "b831381d-6324-4d53-ad4f-8cda48b30811",
            "alterId": 0
          }
        ]
      },
      "streamSettings": {
        "network": "tcp",
        "security": "none"
      }
    }
  ],
  "outbounds": [
    { "protocol": "freedom", "tag": "direct" }
  ]
}
EOF

nohup ~/bin/v2ray/xray run -c ~/bin/v2ray/config.json > ~/xray.log 2>&1 &
```

**Verification**: `nc -z localhost 10812 && echo '10812 OPEN'`

### Docker V2Ray Config
The Docker V2Ray config (`docker/v2ray/config.json`) should include both inbound SOCKS5/HTTP and VMess outbound for the proxy chain:
```json
{
  "inbounds": [
    {"port": 10808, "protocol": "socks", "settings": {"auth": "noauth", "udp": true}},
    {"port": 10809, "protocol": "http"}
  ],
  "outbounds": [
    {"protocol": "freedom", "tag": "direct"},
    {
      "protocol": "vmess",
      "tag": "proxy",
      "settings": {
        "vnext": [{"address": "your-vmess-server.com", "port": 443, "users": [{"id": "your-uuid", "alterId": 0, "security": "aes-128-gcm"}]}],
      "streamSettings": {"network": "ws", "security": "tls"}
    }
  ]
}
```

## SMP Server

### 4096-bit RSA Certificate Requirement
**Error**: `Error: unsupported HTTPS credentials, required 4096-bit RSA`

**Fix**: Regenerate certificate with 4096-bit key:
```bash
openssl req -x509 -newkey rsa:4096 -keyout certificates/ParanoidX.local.key -out certificates/ParanoidX.local.crt -days 365 -nodes -subj '/CN=ParanoidX.local'
```

### Fingerprint File Generation
The SMP server generates a fingerprint file at `/etc/opt/simplex/fingerprint` on first run with `--init`. To pre-generate and copy to mounted config:

```bash
# Run once to generate all files
docker run --rm -e ADDR=ParanoidX.local -v /tmp/smp_test:/etc/opt/simplex simplexchat/smp-server:latest --init

# Copy generated files to mounted config directory
cp /tmp/smp_test/fingerprint ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/ca.crt ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/ca.key ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/server.crt ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/server.key ~/ParanoidX/docker/smp_configs/
```

### Certificate Path in Config (smp-server.ini)
**Error**: `Error: no HTTPS credentials: /certificates/ParanoidX.local.crt`

**Root Cause**: Config file uses `cert = /certificates/...` but the Docker volume mounts at `/etc/opt/simplex/certificates/`

**Fix**: Update `smp-server.ini`:
```ini
cert = /etc/opt/simplex/certificates/ParanoidX.local.crt
key = /etc/opt/simplex/certificates/ParanoidX.local.key
```

## Tor Hidden Service

### Container Address for ICE/TURN
**Error**: `Unparseable address in hidden service port configuration`

**Root Cause**: Tor config used bare port `3478` instead of container DNS name `ParanoidX-coturn:3478`

**Fix**: Update `tor/torrc`:
```
HiddenServicePort 3478 ParanoidX-coturn:3478
HiddenServicePort 5349 ParanoidX-coturn:5349
```

### SocksPort Conflict with HiddenServiceNonAnonymousMode
**Error**: `HiddenServiceNonAnonymousMode is incompatible with using Tor as an anonymous client. Please set Socks/Trans/NATD/DNSPort to 0, or revert HiddenServiceNonAnonymousMode to 0.`

**Root Cause**: Tor's `HiddenServiceNonAnonymousMode 1` (used for faster hidden services) conflicts with running a SOCKS5 proxy (`SocksPort 9050`) on the same instance.

**Fix**: Remove `HiddenServiceNonAnonymousMode 1` and `HiddenServiceSingleHopMode 1` from `torrc` if you need the SOCKS5 proxy:
```torrc
# REMOVE these lines:
# HiddenServiceSingleHopMode 1
# HiddenServiceNonAnonymousMode 1

# Keep:
SocksPort 9050
ControlPort 9051
```
This allows Tor to act as both a hidden service provider AND a SOCKS5 proxy for the chain.

### Tor Ports Mapping in Docker Compose
**Issue**: Tor SOCKS5 port 9050 not accessible from host/WSL2

**Fix**: Explicitly map ports in docker-compose.yml:
```yaml
tor:
  ports:
    - "9050:9050"  # SOCKS5 proxy
    - "9051:9051"  # Control port
```

### Tor Dockerfile — Entrypoint for Permissions
The custom Tor Docker image uses an entrypoint that runs as root to fix bind mount permissions, then drops privileges. Ensure Dockerfile has:
```dockerfile
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["tor"]
```

## coturn (TURN/ICE Server)

### Missing Config Files (Directories Instead of Files)
**Problem**: `turnserver.conf`, `turn_cert.pem`, `turn_key.pem` were created as directories, not files

**Fix**: Remove directories and create proper files:

```bash
# Remove directory artifacts
rm -rf turnserver.conf turn_cert.pem turn_key.pem

# Create turnserver.conf
cat > turnserver.conf << 'EOF'
listening-port=3478
tls-listening-port=5349
listening-ip=0.0.0.0
external-ip=auto
realm=paranoidx.local
use-auth-secret
static-auth-secret=paranoidx-turn-secret-2026
cert=/etc/coturn/turn_cert.pem
pkey=/etc/coturn/turn_key.pem
no-udp
no-udp-relay
log-file=stdout
verbose
EOF

# Generate TLS certificates
openssl req -x509 -newkey rsa:2048 -keyout turn_key.pem -out turn_cert.pem -days 365 -nodes -subj '/CN=paranoidx.local'
```

### File Ownership
Ensure coturn config files are owned by the user matching container UID (1000):
```bash
chown -R 1000:1000 coturn/
```

### UDP Relay via Tor
**Issue**: coturn UDP not working through Tor hidden service

**Fix**: Disable UDP in coturn config (TCP only via Tor):
```conf
no-udp
no-udp-relay
```

### Port Mapping for coturn
Map both TCP and UDP ports for TURN/ICE:
```yaml
coturn:
  ports:
    - "3478:3478/tcp"
    - "3478:3478/udp"
    - "5349:5349/tcp"
    - "5349:5349/udp"
```

## Docker Compose Volume Mounts
All configs should be mounted as read-only where possible:

```yaml
volumes:
  - ./tor/torrc:/etc/tor/torrc:ro
  - ./tor/hidden_services/smp:/var/lib/tor/smp
  - ./tor/hidden_services/xftp:/var/lib/tor/xftp
  - ./tor/hidden_services/ice:/var/lib/tor/ice
  - ./coturn/turnserver.conf:/etc/coturn/turnserver.conf:ro
  - ./coturn/turn_cert.pem:/etc/coturn/turn_cert.pem:ro
  - ./coturn/turn_key.pem:/etc/coturn/turn_key.pem:ro
```

## Health Checks
Ensure health checks use valid commands:

```yaml
healthcheck:
  test: ["CMD", "tor", "--version"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 20s
```

For coturn:
```yaml
healthcheck:
  test: ["CMD-SHELL", "test -f /proc/1/cmdline && cat /proc/1/cmdline | tr '\\0' ' ' | grep -q turnserver"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 10s
```

## V2Ray/Xray — Command Syntax in Docker
**Error**: `exec: "run": executable file not found in $PATH`

**Root Cause**: `teddysun/xray` image uses `xray` binary, not `run` as command.

**Fix**: Use explicit command array in docker-compose.yml:
```yaml
v2ray:
  image: teddysun/xray:latest
  command: ["xray", "run", "-c", "/etc/v2ray/config.json"]
```

## Docker Compose — Tor Ports Mapping
**Issue**: Tor SOCKS5 port 9050 not accessible from host/WSL2

**Fix**: Explicitly map ports in docker-compose.yml:
```yaml
tor:
  ports:
    - "9050:9050"  # SOCKS5 proxy
    - "9051:9051"  # Control port
```

## coturn — UDP Relay via Tor
**Issue**: coturn UDP not working through Tor hidden service

**Fix**: Disable UDP in coturn config (TCP only via Tor):
```conf
no-udp
no-udp-relay
```

## SMP Server

### 4096-bit RSA Certificate Requirement
**Error**: `Error: unsupported HTTPS credentials, required 4096-bit RSA`

**Fix**: Regenerate certificate with 4096-bit key:
```bash
openssl req -x509 -newkey rsa:4096 -keyout certificates/ParanoidX.local.key -out certificates/ParanoidX.local.crt -days 365 -nodes -subj '/CN=ParanoidX.local'
```

### Fingerprint File Generation
The SMP server generates a fingerprint file at `/etc/opt/simplex/fingerprint` on first run with `--init`. To pre-generate and copy to mounted config:

```bash
# Run once to generate all files
docker run --rm -e ADDR=ParanoidX.local -v /tmp/smp_test:/etc/opt/simplex simplexchat/smp-server:latest --init

# Copy generated files to mounted config directory
cp /tmp/smp_test/fingerprint ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/ca.crt ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/ca.key ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/server.crt ~/ParanoidX/docker/smp_configs/
cp /tmp/smp_test/server.key ~/ParanoidX/docker/smp_configs/
```

### Certificate Path in Config (smp-server.ini)
**Error**: `Error: no HTTPS credentials: /certificates/ParanoidX.local.crt`

**Root Cause**: Config file uses `cert = /certificates/...` but the Docker volume mounts at `/etc/opt/simplex/certificates/`

**Fix**: Update `smp-server.ini`:
```ini
cert = /etc/opt/simplex/certificates/ParanoidX.local.crt
key = /etc/opt/simplex/certificates/ParanoidX.local.key
```

## Tor Hidden Service

### Container Address for ICE/TURN
**Error**: `Unparseable address in hidden service port configuration`

**Root Cause**: Tor config used bare port `3478` instead of container DNS name `ParanoidX-coturn:3478`

**Fix**: Update `tor/torrc`:
```
HiddenServicePort 3478 ParanoidX-coturn:3478
HiddenServicePort 5349 ParanoidX-coturn:5349
```

### SocksPort Conflict with HiddenServiceNonAnonymousMode
**Error**: `HiddenServiceNonAnonymousMode is incompatible with using Tor as an anonymous client. Please set Socks/Trans/NATD/DNSPort to 0, or revert HiddenServiceNonAnonymousMode to 0.`

**Root Cause**: Tor's `HiddenServiceNonAnonymousMode 1` (used for faster hidden services) conflicts with running a SOCKS5 proxy (`SocksPort 9050`) on the same instance.

**Fix**: Remove `HiddenServiceNonAnonymousMode 1` and `HiddenServiceSingleHopMode 1` from `torrc` if you need the SOCKS5 proxy:
```torrc
# REMOVE these lines:
# HiddenServiceSingleHopMode 1
# HiddenServiceNonAnonymousMode 1

# Keep:
SocksPort 9050
ControlPort 9051
```
This allows Tor to act as both a hidden service provider AND a SOCKS5 proxy for the chain.

### Tor Ports Mapping in Docker Compose
**Issue**: Tor SOCKS5 port 9050 not accessible from host/WSL2

**Fix**: Explicitly map ports in docker-compose.yml:
```yaml
tor:
  ports:
    - "9050:9050"  # SOCKS5 proxy
    - "9051:9051"  # Control port
```

### Tor Dockerfile — Entrypoint for Permissions
The custom Tor Docker image uses an entrypoint that runs as root to fix bind mount permissions, then drops privileges. Ensure Dockerfile has:
```dockerfile
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["tor"]
```

## coturn (TURN/ICE Server)

### Missing Config Files (Directories Instead of Files)
**Problem**: `turnserver.conf`, `turn_cert.pem`, `turn_key.pem` were created as directories, not files

**Fix**: Remove directories and create proper files:

```bash
# Remove directory artifacts
rm -rf turnserver.conf turn_cert.pem turn_key.pem

# Create turnserver.conf
cat > turnserver.conf << 'EOF'
listening-port=3478
tls-listening-port=5349
listening-ip=0.0.0.0
external-ip=auto
realm=paranoidx.local
use-auth-secret
static-auth-secret=paranoidx-turn-secret-2026
cert=/etc/coturn/turn_cert.pem
pkey=/etc/coturn/turn_key.pem
no-udp
no-udp-relay
log-file=stdout
verbose
EOF

# Generate TLS certificates
openssl req -x509 -newkey rsa:2048 -keyout turn_key.pem -out turn_cert.pem -days 365 -nodes -subj '/CN=paranoidx.local'
```

### File Ownership
Ensure coturn config files are owned by the user matching container UID (1000):
```bash
chown -R 1000:1000 coturn/
```

### UDP Relay via Tor
**Issue**: coturn UDP not working through Tor hidden service

**Fix**: Disable UDP in coturn config (TCP only via Tor):
```conf
no-udp
no-udp-relay
```

### Port Mapping for coturn
Map both TCP and UDP ports for TURN/ICE:
```yaml
coturn:
  ports:
    - "3478:3478/tcp"
    - "3478:3478/udp"
    - "5349:5349/tcp"
    - "5349:5349/udp"
```

## Docker Compose Volume Mounts
All configs should be mounted as read-only where possible:

```yaml
volumes:
  - ./tor/torrc:/etc/tor/torrc:ro
  - ./tor/hidden_services/smp:/var/lib/tor/smp
  - ./tor/hidden_services/xftp:/var/lib/tor/xftp
  - ./tor/hidden_services/ice:/var/lib/tor/ice
  - ./coturn/turnserver.conf:/etc/coturn/turnserver.conf:ro
  - ./coturn/turn_cert.pem:/etc/coturn/turn_cert.pem:ro
  - ./coturn/turn_key.pem:/etc/coturn/turn_key.pem:ro
```

## Health Checks
Ensure health checks use valid commands:

```yaml
healthcheck:
  test: ["CMD", "tor", "--version"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 20s
```

For coturn:
```yaml
healthcheck:
  test: ["CMD-SHELL", "test -f /proc/1/cmdline && cat /proc/1/cmdline | tr '\\0' ' ' | grep -q turnserver"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 10s
```

## V2Ray/Xray — Command Syntax in Docker
**Error**: `exec: "run": executable file not found in $PATH`

**Root Cause**: `teddysun/xray` image uses `xray` binary, not `run` as command.

**Fix**: Use explicit command array in docker-compose.yml:
```yaml
v2ray:
  image: teddysun/xray:latest
  command: ["xray", "run", "-c", "/etc/v2ray/config.json"]
```

## Docker Compose — Tor Ports Mapping
**Issue**: Tor SOCKS5 port 9050 not accessible from host/WSL2

**Fix**: Explicitly map ports in docker-compose.yml:
```yaml
tor:
  ports:
    - "9050:9050"  # SOCKS5 proxy
    - "9051:9051"  # Control port
```

## coturn — UDP Relay via Tor
**Issue**: coturn UDP not working through Tor hidden service

**Fix**: Disable UDP in coturn config (TCP only via Tor):
```conf
no-udp
no-udp-relay
```