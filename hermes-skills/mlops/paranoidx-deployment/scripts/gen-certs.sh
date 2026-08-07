#!/bin/bash
# Generate self-signed certificate with SAN for ParanoidX

set -e

DATA_DIR="/mnt/c/ParanoidX-data"
CERTS_DIR="$DATA_DIR/certs"

mkdir -p "$CERTS_DIR"
cd "$CERTS_DIR"

# Get current WSL2 eth0 IP
WSL_IP=$(ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
echo "Detected WSL2 eth0 IP: $WSL_IP"

# Build SAN list
SAN="DNS:localhost,IP:127.0.0.1,IP:10.255.255.254"
if [ -n "$WSL_IP" ]; then
    SAN="$SAN,IP:$WSL_IP"
fi

echo "Generating certificate with SAN: $SAN"

openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 365 -nodes -subj "/CN=localhost" \
  -addext "subjectAltName=$SAN"

echo "Certificate generated:"
echo "  cert.pem: $(wc -l < cert.pem) lines"
echo "  key.pem:  $(wc -l < key.pem) lines"
echo ""
echo "SAN: $SAN"
echo ""
echo "To import to Windows Trusted Root CA (run as Admin):"
echo "  certutil -addstore -f ROOT $(pwd)/cert.pem"
echo ""
echo "Then rebuild and restart ParanoidX:"
echo "  cd /mnt/c/ParanoidX && go build -o ParanoidX ./cmd/ParanoidX"
echo "  cp ParanoidX /home/tomas/bin/ParanoidX"
echo "  pkill -9 -f ParanoidX; sleep 2"
echo "  /home/tomas/bin/ParanoidX -data /mnt/c/ParanoidX-data -listen 0.0.0.0:8080 &"