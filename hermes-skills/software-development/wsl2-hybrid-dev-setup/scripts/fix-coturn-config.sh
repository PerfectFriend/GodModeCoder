#!/bin/bash
# fix-coturn-config.sh - Create coturn config and TLS certificates
# Run in WSL2: bash fix-coturn-config.sh

set -e

COTURN_DIR="$HOME/ParanoidX/docker/coturn"

echo "=== Creating coturn configuration and certificates ==="

mkdir -p "$COTURN_DIR"

# Remove directory artifacts if they exist
rm -rf "$COTURN_DIR/turnserver.conf"
rm -rf "$COTURN_DIR/turn_cert.pem"
rm -rf "$COTURN_DIR/turn_key.pem"

# Create turnserver.conf
cat > "$COTURN_DIR/turnserver.conf" << 'EOF'
# ParanoidX coturn configuration
# ICE/TURN server for WebRTC voice calls

listening-port=3478
tls-listening-port=5349
listening-ip=0.0.0.0

# Use external IP from host
external-ip=auto

# Realms
realm=paranoidx.local

# Authentication
use-auth-secret
static-auth-secret=paranoidx-turn-secret-2026

# TLS
cert=/etc/coturn/turn_cert.pem
pkey=/etc/coturn/turn_key.pem

# No UDP relay via Tor (only TCP)
no-udp
no-udp-relay

# Logging
log-file=stdout
verbose
EOF

# Generate TLS certificates
echo "Generating TLS certificates for coturn..."
openssl req -x509 -newkey rsa:2048 \
    -keyout "$COTURN_DIR/turn_key.pem" \
    -out "$COTURN_DIR/turn_cert.pem" \
    -days 365 -nodes \
    -subj '/CN=paranoidx.local'

# Set ownership for coturn container (UID 1000)
chown -R 1000:1000 "$COTURN_DIR"

echo "Created:"
ls -la "$COTURN_DIR/turnserver.conf" "$COTURN_DIR/turn_cert.pem" "$COTURN_DIR/turn_key.pem"

echo ""
echo "✓ coturn config and certificates created"
echo "Restart coturn container:"
echo "  cd ~/ParanoidX/docker && docker compose restart coturn"