#!/usr/bin/env python3
"""
HTTPS Verification Script for Go Services with Auto-TLS

Usage:
    python3 verify_https.py [--base URL] [--username USER] [--password PASS]

Environment variables:
    BASE_URL - Base URL (default: https://127.0.0.1:8080)
    USERNAME - Test username (default: verify_<timestamp>)
    PASSWORD - Test password (default: TestPass123!)
"""

import sys
import json
import subprocess
import argparse
import time
from typing import Tuple, Optional

def curl(url: str, cookie: Optional[str] = None, method: str = "GET", 
         data: Optional[dict] = None, form_data: Optional[dict] = None,
         headers: Optional[dict] = None, insecure: bool = True) -> Tuple[str, int]:
    """Execute curl and return (stdout, returncode)."""
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
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 124
    except Exception as e:
        return str(e), 1

def check(name: str, condition: bool, details: str = "") -> bool:
    """Print check result and return condition."""
    if condition:
        print(f"  ✅ {name}")
        return True
    else:
        print(f"  ❌ {name} {details}")
        return False

def run_verification(base_url: str, username: str, password: str) -> int:
    """Run full HTTPS verification suite."""
    passed = 0
    failed = 0
    token = ""
    mnemonic = ""
    pubkey = ""

    print("=" * 60)
    print("GO HTTPS AUTO-CONFIG VERIFICATION")
    print("=" * 60)

    # 1. Register
    print("\n1. Register with UNIVERSAL-UNLIMITED invite...")
    out, code = curl(f"{base_url}/api/auth/register-with-invite", method="POST", data={
        "username": username, "password": password, "invite": "UNIVERSAL-UNLIMITED"
    })
    try:
        data = json.loads(out)
        if check("Registration succeeds", data.get("status") == "created"):
            passed += 1
        else:
            failed += 1
        mnemonic = data.get("mnemonic", "")
        pubkey = data.get("pubkey", "")
        if check("24-word mnemonic", len(mnemonic.split()) == 24):
            passed += 1
        else:
            failed += 1
        if check("Ed25519 pubkey (64 hex)", len(pubkey) == 64):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"  ❌ Registration JSON parse: {e}: {out[:80]}")
        failed += 3

    # 2. Login
    print("\n2. Login with username/password...")
    out, code = curl(f"{base_url}/login", method="POST", form_data={
        "username": username, "password": password
    })
    try:
        data = json.loads(out)
        if check("Login succeeds", data.get("status") == "ok"):
            passed += 1
        else:
            failed += 1
        token = data.get("token", "")
        if check("Returns token", bool(token)):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"  ❌ Login JSON parse: {e}: {out[:80]}")
        failed += 2

    # 3. Dashboard
    print("\n3. Dashboard with version badge...")
    out, code = curl(f"{base_url}/", cookie=token)
    if check("Dashboard accessible", "A0" in out):
        passed += 1
    else:
        failed += 1
    if check("Version badge present", "A0" in out):
        passed += 1
    else:
        failed += 1

    # 4. Wallet API
    print("\n4. Wallet API (8 denominations, 8 NFTs, 16GB vault)...")
    out, code = curl(f"{base_url}/api/wallet/state", cookie=token)
    try:
        data = json.loads(out)
        if check("Wallet state works", "denominations" in data):
            passed += 1
        else:
            failed += 1
        if check("8 denominations", len(data.get("denominations", [])) == 8):
            passed += 1
        else:
            failed += 1
        if check("8 NFT slots", len(data.get("nfts", [])) == 8):
            passed += 1
        else:
            failed += 1
        if check("16GB vault", data.get("vault", {}).get("tl_minted") == 1435000000000):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"  ❌ Wallet JSON: {e}")
        failed += 4

    # 5. VPN Configs
    print("\n5. VPN Configs (10 protocols)...")
    out, code = curl(f"{base_url}/api/vpn/configs", cookie=token)
    try:
        data = json.loads(out)
        if check("VPN configs array", isinstance(data, list)):
            passed += 1
        else:
            failed += 1
        if check("10+ configs", len(data) >= 10):
            passed += 1
        else:
            failed += 1
        types = {c.get("type") for c in data}
        expected = {"vmess", "vless", "trojan", "shadowsocks", "wireguard", 
                    "openvpn", "socks5", "ssh", "tor", "vless_reality"}
        if check("All 10 protocol types", expected.issubset(types)):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"  ❌ VPN JSON: {e}")
        failed += 3

    # 6. Radio
    print("\n6. Radio (5 stations EN/RU/ES)...")
    out, code = curl(f"{base_url}/api/radio", cookie=token)
    try:
        data = json.loads(out)
        if check("Radio API works", "stations" in data):
            passed += 1
        else:
            failed += 1
        if check("5 stations", len(data.get("stations", [])) == 5):
            passed += 1
        else:
            failed += 1
        langs = {s.get("lang") for s in data.get("stations", [])}
        if check("EN/RU/ES", langs == {"en", "ru", "es"}):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"  ❌ Radio JSON: {e}")
        failed += 3

    # 7. Core APIs
    print("\n7. Core APIs...")
    api_checks = [
        ("Treasury", f"{base_url}/api/treasury/state", lambda d: "banknotes" in d),
        ("Exchange", f"{base_url}/api/wallet/exchange/quote?from=TL&to=NT", 
         lambda d: d.get("fee_pct") == "2.28%"),
        ("Marketplace", f"{base_url}/api/marketplace", lambda d: d.get("ok") is True),
        ("Bridge", f"{base_url}/api/bridge/status", lambda d: d.get("ok") is True),
        ("Citizens", f"{base_url}/api/citizens", 
         lambda d: isinstance(d, list) and len(d) > 0),
        ("Vault", f"{base_url}/api/vault/list", lambda d: d.get("quota_mb") == 16384),
        ("Status", f"{base_url}/api/status", lambda d: d.get("status") == "running"),
    ]
    for name, url, check_fn in api_checks:
        out, code = curl(url, cookie=token)
        try:
            data = json.loads(out)
            if check(name, check_fn(data)):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {name} JSON: {e}")
            failed += 1

    # 8. Subscription
    print("\n8. Subscription tier...")
    out, code = curl(f"{base_url}/api/subscription?pubkey={pubkey}", cookie=token)
    try:
        data = json.loads(out)
        if check("Subscription works", data.get("tier") == "colonist"):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"  ❌ Subscription JSON: {e}")
        failed += 1

    # 9. UI Pages
    print("\n9. UI Pages (HTTPS)...")
    for name, url, check_str in [
        ("Login page A06", f"{base_url}/login.html", "A06"),
        ("Register UNIVERSAL", f"{base_url}/register.html", "UNIVERSAL-UNLIMITED"),
        ("Restore tab", f"{base_url}/register.html", "Restore from Seed"),
    ]:
        out, code = curl(url)
        if check(name, check_str in out):
            passed += 1
        else:
            failed += 1

    # 10. Restore flow
    print("\n10. Restore flow (seed phrase recovery)...")
    out, code = curl(f"{base_url}/api/auth/register-with-invite", method="POST", data={
        "username": f"{username}_restore", "password": password, "invite": "UNIVERSAL-UNLIMITED"
    })
    try:
        restore_mnemonic = json.loads(out).get("mnemonic", "")
        out, code = curl(f"{base_url}/api/auth/restore", method="POST", data={
            "username": f"{username}_restore", "mnemonic": restore_mnemonic, "password": "NewPass456!"
        })
        if check("Restore succeeds", json.loads(out).get("status") == "restored"):
            passed += 1
        else:
            failed += 1

        out, code = curl(f"{base_url}/login", method="POST", form_data={
            "username": f"{username}_restore", "password": "NewPass456!"
        })
        if check("New password works", json.loads(out).get("status") == "ok"):
            passed += 1
        else:
            failed += 1

        out, code = curl(f"{base_url}/login", method="POST", form_data={
            "username": f"{username}_restore", "password": password
        })
        if check("Old password rejected", "invalid" in out.lower() or "error" in out.lower()):
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"  ❌ Restore flow: {e}")
        failed += 3

    # 11. WSL2 Interfaces
    print("\n11. WSL2 Interfaces (HTTPS)...")
    ips = ["127.0.0.1", "172.25.101.187", "10.255.255.254"]
    for ip in ips:
        out, code = curl(f"https://{ip}:8080/login.html")
        if check(f"HTTPS on {ip}", "Saint Mary Liberty Island" in out):
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULT: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1

def main():
    parser = argparse.ArgumentParser(description="Verify Go HTTPS auto-config")
    parser.add_argument("--base", default="https://127.0.0.1:8080", help="Base URL")
    parser.add_argument("--username", default=f"verify_{int(time.time())}", help="Test username")
    parser.add_argument("--password", default="TestPass123!", help="Test password")
    args = parser.parse_args()

    sys.exit(run_verification(args.base, args.username, args.password))

if __name__ == "__main__":
    main()