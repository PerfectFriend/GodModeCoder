#!/bin/bash
# fix-smp-certs.sh - Regenerate SMP certs with 4096-bit RSA
# Run in WSL2: bash fix-smp-certs.sh

set -e

echo "=== Regenerating SMP Server Certificates (4096-bit RSA) ==="

CERT_DIR="$HOME/ParanoidX/docker/smp_configs/certificates"
mkdir -p "$CERT_DIR"

# Backup existing certs
if [ -f "$CERT_DIR/ParanoidX.local.crt" ]; then
    cp "$CERT_DIR/ParanoidX.local.crt" "$CERT_DIR/ParanoidX.local.crt.bak.$(date +%s)"
    cp "$CERT_DIR/ParanoidX.local.key" "$CERT_DIR/ParanoidX.local.key.bak.$(date +%s)"
fi

# Generate new 4096-bit RSA certificate
echo "Generating 4096-bit RSA certificate..."
openssl req -x509 -newkey rsa:4096 \
    -keyout "$CERT_DIR/ParanoidX.local.key" \
    -out "$CERT_DIR/ParanoidX.local.crt" \
    -days 365 -nodes \
    -subj '/CN=ParanoidX.local'

echo "Certificate generated:"
openssl x509 -in "$CERT_DIR/ParanoidX.local.crt" -text -noout | grep -A2 "Public-Key:"

# Verify key size
KEY_SIZE=$(openssl rsa -in "$CERT_DIR/ParanoidX.local.key" -text -noout 2>/dev/null | grep "Private-Key:" | grep -o '[0-9]*')
echo "Key size: $KEY_SIZE bits"

if [ "$KEY_SIZE" = "4096" ]; then
    echo "✓ 4096-bit certificate created successfully"
else
    echo "✗ Key size is $KEY_SIZE bits (expected 4096)"
    exit 1
fi

# Regenerate fingerprint by running server once with --init
echo "Regenerating fingerprint..."
TMP_DIR=$(mktemp -d)
docker run --rm -e ADDR=ParanoidX.local -v "$TMP_DIR:/etc/opt/simplex" simplexchat/smp-server:latest --init 2>&1 | tail -5

# Copy generated files
cp "$TMP_DIR/fingerprint" "$HOME/ParanoidX/docker/smp_configs/fingerprint"
cp "$TMP_DIR/ca.crt" "$HOME/ParanoidX/docker/smp_configs/ca.crt"
cp "$TMP_DIR/ca.key" "$HOME/ParanoidX/docker/smp_configs/ca.key"
cp "$TMP_DIR/server.crt" "$HOME/ParanoidX/docker/smp_configs/server.crt"
cp "$TMP_DIR/server.key" "$HOME/ParanoidX/docker/smp_configs/server.key"
sudo chown "$USER:$USER" "$HOME/ParanoidX/docker/smp_configs/ca.key" "$HOME/ParanoidX/docker/smp_configs/server.key" 2>/dev/null || true

echo "Fingerprint:"
cat "$HOME/ParanoidX/docker/smp_configs/fingerprint"

echo ""
echo "✓ SMP certificates and fingerprint regenerated"
echo "Now restart Docker compose:"
echo "  cd ~/ParanoidX/docker && docker compose down && docker compose up -d"