#!/bin/bash
# fix-torrc-ice.sh - Update torrc with container addresses for ICE/TURN
# Run in WSL2: bash fix-torrc-ice.sh

set -e

TORRC="$HOME/ParanoidX/docker/tor/torrc"

echo "=== Updating torrc for ICE/TURN hidden services ==="

if [ ! -f "$TORRC" ]; then
    echo "ERROR: torrc not found at $TORRC"
    exit 1
fi

# Backup
cp "$TORRC" "$TORRC.bak.$(date +%s)"

# Fix ICE hidden service ports to use container DNS
sed -i 's|^HiddenServicePort 3478 .*|HiddenServicePort 3478 ParanoidX-coturn:3478|' "$TORRC"
sed -i 's|^HiddenServicePort 5349 .*|HiddenServicePort 5349 ParanoidX-coturn:5349|' "$TORRC"

echo "Updated torrc:"
grep "HiddenServicePort" "$TORRC"

echo ""
echo "✓ torrc updated for ICE/TURN"
echo "Restart Tor container:"
echo "  cd ~/ParanoidX/docker && docker compose restart tor"