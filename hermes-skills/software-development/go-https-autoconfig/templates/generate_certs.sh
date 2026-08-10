#!/bin/bash
# generate_certs.sh - Generate self-signed certificates for Go HTTPS auto-config
# Usage: ./generate_certs.sh [data_dir] [extra_ips...]

set -euo pipefail

DATA_DIR="${1:-/mnt/c/ParanoidX-data}"
CERTS_DIR="$DATA_DIR/certs"
EXTRA_IPS="${@:2}"

# Default IPs for WSL2
DEFAULT_IPS="127.0.0.1,172.25.101.187,10.255.255.254"
ALL_IPS="$DEFAULT_IPS"

if [ -n "$EXTRA_IPS" ]; then
    ALL_IPS="$DEFAULT_IPS,$EXTRA_IPS"
fi

echo "Generating certificates in $CERTS_DIR"
echo "SAN IPs: $ALL_IPS"

mkdir -p "$CERTS_DIR"
cd "$CERTS_DIR"

openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem \
  -days 365 -nodes \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:$ALL_IPS"

echo "Certificate generated:"
openssl x509 -in cert.pem -text -noout | grep -A1 "Subject Alternative Name"

echo ""
echo "Files created:"
ls -la cert.pem key.pem
echo ""
echo "To trust in Windows:"
echo "  1. Run certmgr.msc"
echo "  2. Trusted Root Certification Authorities -> Certificates -> Right-click -> All Tasks -> Import"
echo "  3. Select $CERTS_DIR/cert.pem"
echo "  4. Place in 'Trusted Root Certification Authorities'"
echo ""
echo "For Windows port forwarding (run as Admin):"
echo "  netsh interface portproxy add v4tov4 listenport=8080 listenaddress=127.0.0.1 connectport=8080 connectaddress=172.25.101.187"