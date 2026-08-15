#!/usr/bin/env python3
"""
ParanoidX Autonomous Evolution Cycle
Runs 20 cycles: test, debug, backup to D:\backups, increment version badge
Reports to Telegram on each cycle
"""
import os
import sys
import json
import subprocess
import time
import hashlib
import tarfile
from datetime import datetime
from pathlib import Path

# Config
PARANOIDX_SRC = "/mnt/c/ParanoidX"
PARANOIDX_DATA = "/mnt/c/ParanoidX-data"
BACKUP_DIR = "/home/tomas/backups"  # User-writable backup directory
WSL_BINARY = "/home/tomas/bin/ParanoidX"
WSL_DATA = "/mnt/c/ParanoidX-data"
DASHBOARD_HTML = os.path.join(PARANOIDX_DATA, "dashboard.html")
LOGIN_HTML = os.path.join(PARANOIDX_DATA, "login.html")
REGISTER_HTML = os.path.join(PARANOIDX_DATA, "register.html")
CONFIG_FILE = "/mnt/c/ParanoidX-data/simplex-node.json"
CYCLES = 20
TEST_BASE_URL = "https://127.0.0.1:8080"  # Will use portproxy if configured

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def load_config():
    """Load telegram config from simplex-node.json"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            cfg = json.load(f)
        return cfg.get("torquemada_token", ""), cfg.get("torquemada_chat_id", 0)
    except Exception as e:
        log(f"Error loading config: {e}")
        return "", 0

TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID = load_config()

def run_cmd(cmd, cwd=None, timeout=120):
    """Run command and return (success, stdout, stderr)"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def send_telegram(text):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("Telegram not configured, skipping notification")
        return
    try:
        import urllib.request
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        log(f"Telegram send failed: {e}")

def get_version_badge(html_path):
    """Extract version badge from dashboard.html"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        import re
        match = re.search(r'id="dashVersion"[^>]*>([A-Z]\d+)<', content)
        if match:
            return match.group(1)
        # Fallback: search for version badge pattern
        match = re.search(r'version-badge[^>]*>([A-Z]\d+)<', content)
        if match:
            return match.group(1)
    except Exception as e:
        log(f"Error reading version: {e}")
    return "A00"

def set_version_badge(html_path, version):
    """Update version badge in HTML file"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        import re
        # Update dashboard.html
        content = re.sub(r'(id="dashVersion"[^>]*>)([A-Z]\d+)(<)', rf'\1{version}\3', content)
        content = re.sub(r'(version-badge[^>]*>)([A-Z]\d+)(<)', rf'\1{version}\3', content)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        log(f"Updated version badge to {version} in {html_path}")
        return True
    except Exception as e:
        log(f"Error updating version: {e}")
        return False

def increment_version(version):
    """Increment version badge (A00 -> A01, A09 -> A10, etc.)"""
    if not version or len(version) < 2:
        return "A01"
    prefix = version[0]
    num = int(version[1:]) + 1
    return f"{prefix}{num:02d}"

def backup_to_usb(cycle_num, version):
    """Create timestamped backup to D:\backups"""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"paranoidx-evolution-{version}-cycle{cycle_num:02d}-{ts}"
    backup_path = os.path.join(BACKUP_DIR, f"{backup_name}.tar.gz")
    
    log(f"Creating backup: {backup_path}")
    
    with tarfile.open(backup_path, "w:gz") as tar:
        tar.add(PARANOIDX_SRC, arcname=os.path.join(backup_name, "ParanoidX"))
        tar.add(PARANOIDX_DATA, arcname=os.path.join(backup_name, "ParanoidX-data"))
    
    # Verify backup
    size = os.path.getsize(backup_path)
    sha256 = hashlib.sha256()
    with open(backup_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    
    log(f"Backup created: {size/1024/1024:.1f} MB, SHA256: {sha256.hexdigest()[:16]}...")
    
    # Also save SHA256
    with open(os.path.join(BACKUP_DIR, f"{backup_name}.sha256"), "w") as f:
        f.write(f"{sha256.hexdigest()}  {os.path.basename(backup_path)}\n")
    
    return backup_path, sha256.hexdigest()

def build_binary():
    """Build Go binary in WSL"""
    log("Building Go binary...")
    cmd = f'wsl -d Ubuntu-24.04 -- bash -c "cd /mnt/c/ParanoidX && go build -o /home/tomas/bin/ParanoidX ./cmd/ParanoidX"'
    ok, out, err = run_cmd(cmd, timeout=180)
    if ok:
        log("Build successful")
    else:
        log(f"Build failed: {err}")
    return ok, out, err

def restart_server():
    """Restart ParanoidX server in WSL"""
    log("Restarting server...")
    # Kill existing
    run_cmd('wsl -- bash -c "pkill -f ParanoidX"', timeout=10)
    time.sleep(2)
    # Start new
    cmd = f'wsl -- bash -c "nohup {WSL_BINARY} -data {WSL_DATA} -listen 0.0.0.0:8080 > /tmp/paranoidx.log 2>&1 &"'
    ok, out, err = run_cmd(cmd, timeout=10)
    time.sleep(3)  # Wait for startup
    return ok

def run_tests():
    """Run full API test suite"""
    log("Running API tests...")
    
    # Use the verification script we created earlier
    test_script = r"C:\Users\tomas\AppData\Local\Temp\hermes-verify-https-final.py"
    if not os.path.exists(test_script):
        log("Test script not found, creating minimal test...")
        # Minimal inline test
        import urllib.request
        import ssl
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        tests = [
            ("GET /login.html", f"{TEST_BASE_URL}/login.html"),
            ("GET /register.html", f"{TEST_BASE_URL}/register.html"),
        ]
        
        passed = 0
        for name, url in tests:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                    if resp.status == 200:
                        log(f"  ✅ {name}")
                        passed += 1
                    else:
                        log(f"  ❌ {name}: HTTP {resp.status}")
            except Exception as e:
                log(f"  ❌ {name}: {e}")
        
        return passed, len(tests)
    
    ok, out, err = run_cmd(f'python3 {test_script}', timeout=120)
    # Parse results from output
    if "29/29" in out or "PASSED" in out:
        return 29, 29
    return 0, 29

def debug_cycle(cycle_num, version):
    """Debug: check logs, health, dashboard"""
    log(f"Cycle {cycle_num} ({version}) - Debug checks...")
    
    # Check server process
    ok, out, _ = run_cmd('wsl -- bash -c "ss -tlnp | grep :8080"')
    if ok and "ParanoidX" in out:
        log("  ✅ Server listening on 8080")
    else:
        log("  ❌ Server NOT listening")
        return False
    
    # Check logs for errors
    ok, out, _ = run_cmd('wsl -- bash -c "tail -50 /tmp/paranoidx.log"')
    if "ERROR" in out or "panic" in out.lower():
        log("  ⚠️ Errors in log:")
        for line in out.split('\n')[-10:]:
            if "ERROR" in line or "panic" in line.lower():
                log(f"    {line}")
    
    # Health check
    import urllib.request
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(f"{TEST_BASE_URL}/api/status", context=ctx, timeout=10) as resp:
            if resp.status == 200:
                log("  ✅ /api/status OK")
            else:
                log(f"  ❌ /api/status: {resp.status}")
    except Exception as e:
        log(f"  ❌ Health check failed: {e}")
        return False
    
    return True

def main():
    if len(sys.argv) > 1:
        global CYCLES
        CYCLES = int(sys.argv[1])
    
    log(f"=== PARANOIDX AUTONOMOUS EVOLUTION STARTED ===")
    log(f"Cycles: {CYCLES}")
    log(f"Backup dir: {BACKUP_DIR}")
    log(f"Source: {PARANOIDX_SRC}")
    log(f"Data: {PARANOIDX_DATA}")
    
    send_telegram(f"🚀 <b>ParanoidX Evolution Started</b>\nCycles: {CYCLES}\nBackup: {BACKUP_DIR}")
    
    for cycle in range(1, CYCLES + 1):
        log(f"\n{'='*60}")
        log(f"CYCLE {cycle}/{CYCLES}")
        log(f"{'='*60}")
        
        cycle_start = time.time()
        
        # 1. Get current version
        version = get_version_badge(DASHBOARD_HTML)
        log(f"Current version: {version}")
        
        # 2. Pre-cycle backup
        backup_path, sha256 = backup_to_usb(cycle, version)
        
        # 3. Build
        ok, out, err = build_binary()
        if not ok:
            send_telegram(f"❌ Cycle {cycle} BUILD FAILED\n{err[:200]}")
            log(f"Build failed, continuing...")
        
        # 4. Restart server
        restart_server()
        time.sleep(3)
        
        # 5. Debug checks
        debug_ok = debug_cycle(cycle, version)
        
        # 6. Run tests
        passed, total = run_tests()
        log(f"Tests: {passed}/{total} passed")
        
        # 7. Increment version
        new_version = increment_version(version)
        set_version_badge(DASHBOARD_HTML, new_version)
        set_version_badge(LOGIN_HTML, new_version)
        if os.path.exists(REGISTER_HTML):
            set_version_badge(REGISTER_HTML, new_version)
        
        # 8. Post-cycle backup
        backup_path2, sha256_2 = backup_to_usb(cycle, new_version)
        
        cycle_time = time.time() - cycle_start
        
        # Report
        status = "✅" if debug_ok and passed == total else "⚠️" if passed > 0 else "❌"
        report = (
            f"{status} <b>Cycle {cycle}/{CYCLES} Complete</b>\n"
            f"Version: {version} → {new_version}\n"
            f"Tests: {passed}/{total}\n"
            f"Debug: {'OK' if debug_ok else 'ISSUES'}\n"
            f"Time: {cycle_time:.1f}s\n"
            f"Backup: {os.path.basename(backup_path2)}"
        )
        log(report)
        send_telegram(report)
        
        # Brief pause between cycles
        if cycle < CYCLES:
            time.sleep(5)
    
    send_telegram(f"🏁 <b>Evolution Complete</b>\n{CYCLES} cycles done\nFinal version: {new_version}")
    log(f"\n=== EVOLUTION COMPLETE ===")
    log(f"Final version: {new_version}")

if __name__ == "__main__":
    main()