#!/usr/bin/env python3
"""
Full deployment verification for ParanoidX.
Run after deployment to verify all systems operational.
"""

import sys
import json
import subprocess

def curl(url, cookie=None, method="GET", data=None, form_data=None):
    cmd = ["curl", "-k", "-s"]
    if cookie:
        cmd += ["-H", f"Cookie: dashboard_token={cookie}"]
    cmd += ["-X", method, url]
    if form_data:
        form_str = "&".join([f"{k}={v}" for k, v in form_data.items()])
        cmd += ["--data", form_str]
        cmd += ["-H", "Content-Type: application/x-www-form-urlencoded"]
    elif data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(data)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1

def main():
    base = "https://127.0.0.1:8080"
    passed = 0
    failed = 0

    def check(name, condition, details=""):
        nonlocal passed, failed
        if condition:
            print(f"  ✅ {name}")
            passed += 1
        else:
            print(f"  ❌ {name} {details}")
            failed += 1

    print("=" * 60)
    print("PARANOIDX DEPLOYMENT VERIFICATION")
    print("=" * 60)

    # 1. Register page
    print("\n1. Register page...")
    out, _ = curl(f"{base}/register.html")
    check("Register page loads", "UNIVERSAL-UNLIMITED" in out)
    check("Restore tab present", "Restore from Seed" in out)

    # 2. Login page
    print("\n2. Login page...")
    out, _ = curl(f"{base}/login.html")
    check("Login page loads", "Saint Mary Liberty Island" in out)
    check("Version badge A06", "A06" in out)
    check("Username field", 'type="text"' in out)

    # 3-8. Auth flow
    print("\n3-8. Auth flow (register → login → me → restore → new login → old rejected)...")
    out, _ = curl(f"{base}/api/auth/register-with-invite", method="POST", data={
        "username": "verify_user", "password": "TestPass123!", "invite": "UNIVERSAL-UNLIMITED"
    })
    try:
        data = json.loads(out)
        mnemonic = data.get("mnemonic", "")
        check("Register 24-word mnemonic", len(mnemonic.split()) == 24)
        check("Register returns pubkey", len(data.get("pubkey", "")) == 64)
    except Exception as e:
        check("Register JSON", False, f"→ {e}: {out[:80]}")
        mnemonic = ""

    out, _ = curl(f"{base}/login", method="POST", form_data={
        "username": "verify_user", "password": "TestPass123!"
    })
    try:
        data = json.loads(out)
        token = data.get("token", "")
        check("Login returns token", data.get("status") == "ok" and token)
    except Exception as e:
        check("Login JSON", False, f"→ {e}: {out[:80]}")
        token = ""

    out, _ = curl(f"{base}/api/auth/me", cookie=token)
    try:
        data = json.loads(out)
        check("Me endpoint", data.get("username") == "verify_user")
    except Exception as e:
        check("Me endpoint", False, f"→ {e}: {out[:80]}")

    out, _ = curl(f"{base}/api/auth/restore", method="POST", data={
        "username": "verify_user", "mnemonic": mnemonic, "password": "NewPass456!"
    })
    try:
        data = json.loads(out)
        check("Restore", data.get("status") == "restored")
    except Exception as e:
        check("Restore", False, f"→ {e}: {out[:80]}")

    out, _ = curl(f"{base}/login", method="POST", form_data={
        "username": "verify_user", "password": "NewPass456!"
    })
    try:
        data = json.loads(out)
        token2 = data.get("token", "")
        check("New password works", data.get("status") == "ok")
    except Exception as e:
        check("New login", False, f"→ {e}: {out[:80]}")
        token2 = ""

    out, _ = curl(f"{base}/login", method="POST", form_data={
        "username": "verify_user", "password": "TestPass123!"
    })
    check("Old password rejected", "invalid" in out.lower() or "error" in out.lower())

    # 9. Dashboard
    print("\n9. Dashboard...")
    out, _ = curl(f"{base}/", cookie=token2)
    check("Dashboard accessible", "A0" in out)
    check("Version badge A06", "A06" in out)

    # 10-19. All 10 API tabs
    print("\n10-19. API tabs...")
    if not token2:
        print("  ⚠️ Skipping API checks (no token)")
    else:
        endpoints = [
            ("Wallet", f"{base}/api/wallet/state", lambda d: len(d.get("denominations", [])) == 8 and len(d.get("nfts", [])) == 8),
            ("VPN", f"{base}/api/vpn/configs", lambda d: isinstance(d, list) and len(d) >= 10),
            ("Treasury", f"{base}/api/treasury/state", lambda d: "banknotes" in d),
            ("Exchange", f"{base}/api/wallet/exchange/quote?from=TL&to=NT", lambda d: d.get("fee_pct") == "2.28%"),
            ("Radio", f"{base}/api/radio", lambda d: len(d.get("stations", [])) == 5),
            ("Marketplace", f"{base}/api/marketplace", lambda d: d.get("ok") == True),
            ("Bridge", f"{base}/api/bridge/status", lambda d: d.get("ok") == True),
            ("Citizens", f"{base}/api/citizens", lambda d: isinstance(d, list) and len(d) > 0),
            ("Vault", f"{base}/api/vault/list", lambda d: d.get("quota_mb") == 16384),
            ("Status", f"{base}/api/status", lambda d: d.get("status") == "running"),
        ]
        for name, url, fn in endpoints:
            out, _ = curl(url, cookie=token2)
            try:
                data = json.loads(out)
                check(name, fn(data))
            except Exception as e:
                check(name, False, f"→ {e}: {out[:80]}")

    # 20. Subscription
    print("\n20. Subscription...")
    out, _ = curl(f"{base}/api/auth/register-with-invite", method="POST", data={
        "username": "sub_test", "password": "TestPass123!", "invite": "UNIVERSAL-UNLIMITED"
    })
    try:
        pubkey = json.loads(out).get("pubkey", "")
        out, _ = curl(f"{base}/api/subscription?pubkey={pubkey}", cookie=token2)
        data = json.loads(out)
        check("Subscription tier", data.get("tier") == "colonist")
    except Exception as e:
        check("Subscription", False, f"→ {e}: {out[:80]}")

    # 21. WSL2 interfaces
    print("\n21. WSL2 interfaces (HTTPS)...")
    for ip in ["127.0.0.1", "172.25.101.187", "10.255.255.254"]:
        out, _ = curl(f"https://{ip}:8080/login.html")
        check(f"HTTPS on {ip}", "Saint Mary Liberty Island" in out)

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())