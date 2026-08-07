#!/usr/bin/env bash
# verify-auth.sh — ad-hoc verification for ParanoidX auth package.
# Usage: bash verify-auth.sh   (run from WSL or git-bash; requires WSL Ubuntu-24.04)
# Verifies: build, vet, and the auth deadlock/force-change flow via a temp test file.
set -uo pipefail

WSL="wsl -d Ubuntu-24.04"
CODEBASE=/mnt/c/Users/tomas/ParanoidX-backup/codebase

echo "==> go build ./cmd/ParanoidX/"
$WSL -- bash -lc "cd $CODEBASE && go build -o /tmp/hermes-verify-px ./cmd/ParanoidX/ 2>&1" || { echo "BUILD FAILED"; exit 1; }
echo "BUILD OK"

echo "==> go vet ./cmd/ParanoidX/ ./internal/auth/"
$WSL -- bash -lc "cd $CODEBASE && go vet ./cmd/ParanoidX/ ./internal/auth/ 2>&1" || { echo "VET FAILED"; exit 1; }
echo "VET OK"

# Write the temp test INSIDE WSL (heredoc quoting survives because it's a real bash here-doc)
$WSL -- bash -lc "cd $CODEBASE && cat > internal/auth/auth_verify_test.go << 'GOEOF'
package auth_test

import (
	\"os\"
	\"testing\"

	\"ParanoidX/internal/auth\"
)

func TestAdminCreatedWithForcedChange(t *testing.T) {
	dir, _ := os.MkdirTemp(\"\", \"px-auth-\")
	defer os.RemoveAll(dir)
	am := auth.NewAuthManager(dir)
	u, err := am.Authenticate(\"admin\", \"12345678\")
	if err != nil {
		t.Fatalf(\"admin login failed: %v\", err)
	}
	if !u.ForcePasswordChange {
		t.Fatal(\"admin must have ForcePasswordChange=true on first login\")
	}
	if u.Role != \"admin\" {
		t.Fatalf(\"role=%s want admin\", u.Role)
	}
}

func TestForceChangeClearsFlag(t *testing.T) {
	dir, _ := os.MkdirTemp(\"\", \"px-auth-\")
	defer os.RemoveAll(dir)
	am := auth.NewAuthManager(dir)
	if err := am.ChangePassword(\"admin\", \"12345678\", \"NewPass#2026\"); err != nil {
		t.Fatalf(\"change failed: %v\", err)
	}
	u, err := am.Authenticate(\"admin\", \"NewPass#2026\")
	if err != nil {
		t.Fatalf(\"login with new pass failed: %v\", err)
	}
	if u.ForcePasswordChange {
		t.Fatal(\"ForcePasswordChange must clear after change\")
	}
	if _, err := am.Authenticate(\"admin\", \"12345678\"); err == nil {
		t.Fatal(\"old password must be rejected\")
	}
}
GOEOF
echo test-written"

echo "==> go test ./internal/auth/ (deadlock + force-change flow)"
$WSL -- bash -lc "cd $CODEBASE && go test ./internal/auth/ -v -timeout 120s 2>&1; rc=\$?; rm -f internal/auth/auth_verify_test.go; exit \$rc"
rc=$?
if [ $rc -ne 0 ]; then echo "AUTH TESTS FAILED (rc=$rc) — a hang >100s means RW-mutex deadlock in saveUsersLocked pattern"; exit $rc; fi
echo "AUTH TESTS OK"

rm -f /tmp/hermes-verify-px 2>/dev/null
echo "ALL VERIFICATIONS PASSED"
