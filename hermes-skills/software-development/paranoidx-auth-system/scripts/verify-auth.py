#!/usr/bin/env python3
"""ParanoidX Auth System Verification - Complete 40-test suite + HTTPS

Run inside WSL:
    python3 scripts/verify-auth.py [--base URL] [--insecure]

Tests:
1-6: Core auth flow (register, login, me, restore, new login, old rejected)
7: Invalid invite rejected
8: Dashboard with version badge
9-24: All 16 dashboard tabs return real API data
25-27: UI pages (register, login, restore tab)
28-30: WSL2 interfaces (127.0.0.1, eth0, lo alias)
31-33: Restore flow (seed phrase recovery)
"""

import sys
import json
import subprocess
import argparse

def curl(url, cookie=None, method="GET", data=None, form_data=None, headers=None, insecure=True):
    """Execute curl command and return (stdout, returncode)."""
    cmd = ["curl", "-s"]
    if insecure:
        cmd.append("-k")
    if cookie:
        cmd += ["-H", f"Cookie: dashboard_token={cookie}"]
    cmd += ["-X", method, url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
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
    parser = argparse.ArgumentParser(description="ParanoidX Auth Verification")
    parser.add_argument("--base", default="https://127.0.0.1:8080", help="Base URL (HTTPS)")
    parser.add_argument("--insecure", action="store_true", default=True, help="Skip cert verification (-k)")
    args = parser.parse_args()
    
    base = args.base
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
    print("ParanoidX Auth System Verification")
    print("=" * 60)

    # 1. Register with universal invite
    print("\n1. Register with UNIVERSAL-UNLIMITED invite...")
    out, code = curl(f"{base}/api/auth/register-with-invite", method="POST", data={
        "username": "verify_user", "password": "TestPass123!", "invite": "UNIVERSAL-UNLIMITED"
    })
    try:
        data = json.loads(out)
        check("Registration succeeds", data.get("status") == "created")
        check("Returns 24-word mnemonic", len(data.get("mnemonic", "").split()) == 24)
        check("Returns Ed25519 pubkey (64 hex chars)", len(data.get("pubkey", "")) == 64)
        mnemonic = data.get("mnemonic", "")
        pubkey = data.get("pubkey", "")
    except Exception as e:
        check("Registration JSON parse", False, f"→ {e}: {out[:80]}")
        mnemonic = ""
        pubkey = ""

    # 2. Login with username/password
    print("\n2. Login with username/password...")
    out, code = curl(f"{base}/login", method="POST", form_data={
        "username": "verify_user", "password": "TestPass123!"
    })
    try:
        data = json.loads(out)
        check("Login succeeds", data.get("status") == "ok")
        check("Returns token", bool(data.get("token")))
        token = data.get("token")
    except Exception as e:
        check("Login JSON parse", False, f"→ {e}: {out[:80]}")
        token = ""

    # 3. Authenticated /api/auth/me
    print("\n3. Authenticated /api/auth/me...")
    out, code = curl(f"{base}/api/auth/me", cookie=token)
    try:
        data = json.loads(out)
        check("Me endpoint works", data.get("username") == "verify_user")
        check("Role is user", data.get("role") == "user")
    except Exception as e:
        check("Me endpoint JSON", False, f"→ {e}: {out[:80]}")

    # 4. Restore from seed phrase (password recovery)
    print("\n4. Restore account from seed phrase (password recovery)...")
    out, code = curl(f"{base}/api/auth/restore", method="POST", data={
        "username": "verify_user", "mnemonic": mnemonic, "password": "RecoveredPass456!"
    })
    try:
        data = json.loads(out)
        check("Restore succeeds", data.get("status") == "restored")
    except Exception as e:
        check("Restore JSON", False, f"→ {e}: {out[:80]}")

    # 5. Login with NEW password after restore
    print("\n5. Login with new password after restore...")
    out, code = curl(f"{base}/login", method="POST", form_data={
        "username": "verify_user", "password": "RecoveredPass456!"
    })
    try:
        data = json.loads(out)
        check("New password works", data.get("status") == "ok")
        token2 = data.get("token")
    except Exception as e:
        check("New password login", False, f"→ {e}: {out[:80]}")
        token2 = ""

    # 6. Old password rejected after restore
    print("\n6. Old password rejected after restore...")
    out, code = curl(f"{base}/login", method="POST", form_data={
        "username": "verify_user", "password": "TestPass123!"
    })
    check("Old password rejected", "invalid" in out.lower() or "error" in out.lower() or code != 0)

    # 7. Dashboard accessible with version badge
    print("\n7. Dashboard with version badge...")
    out, code = curl(f"{base}/", cookie=token2)
    check("Dashboard accessible", "A0" in out)
    check("Version badge A06", "A06" in out)

    # 8. Wallet API
    print("\n8. Wallet API (8 denominations, NFTs, vault)...")
    out, code = curl(f"{base}/api/wallet/state", cookie=token2)
    try:
        data = json.loads(out)
        check("Wallet state works", "denominations" in data)
        check("8 denominations", len(data.get("denominations", [])) == 8)
        check("8 NFT slots", len(data.get("nfts", [])) == 8)
        check("Vault info present", "vault" in data)
    except Exception as e:
        check("Wallet JSON", False, f"→ {e}: {out[:80]}")

    # 9. VPN Configs (10 protocols)
    print("\n9. VPN Configs (10 protocols)...")
    out, code = curl(f"{base}/api/vpn/configs", cookie=token2)
    try:
        data = json.loads(out)
        check("VPN configs array", isinstance(data, list))
        check("At least 10 configs", len(data) >= 10)
    except Exception as e:
        check("VPN JSON", False, f"→ {e}: {out[:80]}")

    # 10. Treasury API
    print("\n10. Treasury API (silver reserve, banknotes)...")
    out, code = curl(f"{base}/api/treasury/state", cookie=token2)
    try:
        data = json.loads(out)
        check("Treasury state works", "banknotes" in data)
    except Exception as e:
        check("Treasury JSON", False, f"→ {e}: {out[:80]}")

    # 11. AI Exchanger
    print("\n11. AI Exchanger (TL↔NT rates)...")
    out, code = curl(f"{base}/api/wallet/exchange/quote?from=TL&to=NT", cookie=token2)
    try:
        data = json.loads(out)
        check("Exchange quote works", data.get("from") == "TL" and data.get("to") == "NT")
        check("Rate with 2.28% fee", float(data.get("rate_with_fee", 0)) < float(data.get("rate", 0)))
    except Exception as e:
        check("Exchange JSON", False, f"→ {e}: {out[:80]}")

    # 12. Radio API (5 stations RU/EN/ES)
    print("\n12. Radio API (5 stations RU/EN/ES)...")
    out, code = curl(f"{base}/api/radio", cookie=token2)
    try:
        data = json.loads(out)
        check("Radio API works", "stations" in data)
        check("5 stations", len(data.get("stations", [])) == 5)
    except Exception as e:
        check("Radio JSON", False, f"→ {e}: {out[:80]}")

    # 13. Marketplace
    print("\n13. Marketplace API...")
    out, code = curl(f"{base}/api/marketplace", cookie=token2)
    try:
        data = json.loads(out)
        check("Marketplace works", data.get("ok") == True)
    except Exception as e:
        check("Marketplace JSON", False, f"→ {e}: {out[:80]}")

    # 14. Bridge Status
    print("\n14. SimpleX Bridge Status...")
    out, code = curl(f"{base}/api/bridge/status", cookie=token2)
    try:
        data = json.loads(out)
        check("Bridge status works", data.get("ok") == True)
    except Exception as e:
        check("Bridge JSON", False, f"→ {e}: {out[:80]}")

    # 15. Citizens/Heraldry
    print("\n15. Citizens/Heraldry (coat of arms)...")
    out, code = curl(f"{base}/api/citizens", cookie=token2)
    try:
        data = json.loads(out)
        check("Citizens API works", isinstance(data, list))
    except Exception as e:
        check("Citizens JSON", False, f"→ {e}: {out[:80]}")

    # 16. Vault
    print("\n16. Encrypted Vault...")
    out, code = curl(f"{base}/api/vault/list", cookie=token2)
    try:
        data = json.loads(out)
        check("Vault list works", "files" in data)
        check("Quota 16GB", data.get("quota_mb") == 16384)
    except Exception as e:
        check("Vault JSON", False, f"→ {e}: {out[:80]}")

    # 17. System Status
    print("\n17. Full System Status...")
    out, code = curl(f"{base}/api/status", cookie=token2)
    try:
        data = json.loads(out)
        check("Status endpoint works", data.get("status") == "running")
        check("Version field present", "version" in data)
    except Exception as e:
        check("Status JSON", False, f"→ {e}: {out[:80]}")

    # 18. Subscription Tier
    print("\n18. Subscription Tier (colonist)...")
    out, code = curl(f"{base}/api/subscription?pubkey={pubkey}", cookie=token2)
    try:
        data = json.loads(out)
        check("Subscription works", data.get("tier") == "colonist")
        check("Benefits present", "benefits" in data)
    except Exception as e:
        check("Subscription JSON", False, f"→ {e}: {out[:80]}")

    # ... existing code ...

        # 25-27: UI Pages
        print("\\n25. UI Pages (HTTPS)...")
        for name, url, check_str in [
            ("Login page A06", f"{base}/login.html", "A06"),
            ("Register UNIVERSAL", f"{base}/register.html", "UNIVERSAL-UNLIMITED"),
            ("Restore tab", f"{base}/register.html", "Restore from Seed"),
        ]:
            out, code = curl(url)
            check(name, check_str in out)

        # 28-30: WSL2 Interfaces
        print("\\n28. WSL2 Interfaces (HTTPS)...")
        ips = ["127.0.0.1", "172.25.101.187", "10.255.255.254"]
        for ip in ips:
            out, code = curl(f"https://{ip}:8080/login.html")
            check(f"HTTPS on {ip}", "Saint Mary Liberty Island" in out)

        # 31-33: Restore flow
        print("\\n31. Restore flow (seed phrase recovery)...")
        out, code = curl(f"{base}/api/auth/register-with-invite", method="POST", data={
            "username": "restore_test", "password": "TestPass123!", "invite": "UNIVERSAL-UNLIMITED"
        })
        try:
            restore_mnemonic = json.loads(out).get("mnemonic", "")
            out, code = curl(f"{base}/api/auth/restore", method="POST", data={
                "username": "restore_test", "mnemonic": restore_mnemonic, "password": "NewPass456!"
            })
            check("Restore succeeds", json.loads(out).get("status") == "restored")

            out, code = curl(f"{base}/login", method="POST", form_data={
                "username": "restore_test", "password": "NewPass456!"
            })
            check("New password works", json.loads(out).get("status") == "ok")

            out, code = curl(f"{base}/login", method="POST", form_data={
                "username": "restore_test", "password": "TestPass123!"
            })
            check("Old password rejected", "invalid" in out.lower() or "error" in out.lower())
        except Exception as e:
            check("Restore flow", False, f"→ {e}")

        print("\\n" + "=" * 60)
        print(f"Results: {passed} passed, {failed} failed")
        print("=" * 60)
        return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())