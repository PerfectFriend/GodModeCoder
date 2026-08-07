#!/usr/bin/env python3
"""
TrashClean - Auto-delete spam in Telegram groups via Bot API.
"""

import os
import re
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# Load .env from Hermes home
HERMES_HOME = Path(os.environ.get('HERMES_HOME', Path.home() / 'AppData' / 'Local' / 'hermes'))
ENV_FILE = HERMES_HOME / '.env'

def load_env():
    """Load environment variables from .env file."""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                env[key.strip()] = val.strip().strip('"\'')
    return env

ENV = load_env()

BOT_TOKEN = ENV.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = ENV.get('TELEGRAM_CLEANUP_CHAT_ID')
PATTERNS_RAW = ENV.get('TELEGRAM_CLEANUP_PATTERNS', '')
MAX_AGE = int(ENV.get('TELEGRAM_CLEANUP_MAX_AGE', '300'))
DRY_RUN = ENV.get('TELEGRAM_CLEANUP_DRY_RUN', 'false').lower() == 'true'

STATE_DIR = HERMES_HOME / 'state'
STATE_FILE = STATE_DIR / 'last_update_id.txt'

# Default spam patterns
DEFAULT_PATTERNS = [
    r'(.)\1{4,}',                    # Repeated characters (5+)
    r'[A-ZА-Я]{10,}',                # All caps (10+ chars)
    r'https?://\S+',                 # URLs
    r'(купи|продам|заработ|крипт|биткоин|казино|ставки|лотерея|выигрыш|бонус|промокод|скидка|акция).{0,3}\d',
    r'^\s*[💰💵💎🚀🔥⚡️✨🎁💸🤑]{3,}\s*$',  # Emoji spam
]

def compile_patterns():
    """Compile regex patterns from env or defaults."""
    patterns = []
    if PATTERNS_RAW:
        for p in PATTERNS_RAW.split('|'):
            p = p.strip()
            if p:
                try:
                    patterns.append(re.compile(p, re.IGNORECASE))
                except re.error as e:
                    print(f"[WARN] Invalid regex pattern '{p}': {e}")
    else:
        for p in DEFAULT_PATTERNS:
            patterns.append(re.compile(p, re.IGNORECASE))
    return patterns

PATTERNS = compile_patterns()

def load_state():
    """Load last processed update_id."""
    if STATE_FILE.exists():
        try:
            return int(STATE_FILE.read_text().strip())
        except ValueError:
            pass
    return 0

def save_state(update_id):
    """Save last processed update_id."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(str(update_id))

def api_call(method, params=None):
    """Call Telegram Bot API."""
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = None
    if params:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            if not result.get('ok'):
                raise RuntimeError(f"API error: {result.get('description')}")
            return result.get('result')
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e}")

def is_spam(text):
    """Check if message text matches spam patterns."""
    if not text:
        return False
    for pattern in PATTERNS:
        if pattern.search(text):
            return True
    return False

def main():
    print(f"[TrashClean] Starting... dry_run={DRY_RUN}, chat_id={CHAT_ID}, max_age={MAX_AGE}s")
    print(f"[TrashClean] Patterns loaded: {len(PATTERNS)}")
    
    if not BOT_TOKEN or not CHAT_ID:
        print("[ERROR] TELEGRAM_BOT_TOKEN and TELEGRAM_CLEANUP_CHAT_ID required in .env")
        return 1
    
    last_update_id = load_state()
    print(f"[TrashClean] Last update_id: {last_update_id}")
    
    try:
        updates = api_call('getUpdates', {'offset': last_update_id + 1, 'timeout': 5, 'limit': 100})
    except RuntimeError as e:
        if "409" in str(e) or "Conflict" in str(e):
            print("[TrashClean] Conflict: another getUpdates instance is running (likely Hermes gateway). Skipping this run.")
            return 0
        raise
    if not updates:
        print("[TrashClean] No new updates")
        return 0
    
    deleted = 0
    checked = 0
    now = time.time()
    
    for update in updates:
        update_id = update['update_id']
        last_update_id = max(last_update_id, update_id)
        
        msg = update.get('message') or update.get('edited_message')
        if not msg:
            continue
        
        if str(msg.get('chat', {}).get('id')) != str(CHAT_ID):
            continue
        
        msg_date = msg.get('date', 0)
        if now - msg_date > MAX_AGE:
            continue
        
        text = msg.get('text') or msg.get('caption') or ''
        checked += 1
        
        if is_spam(text):
            msg_id = msg['message_id']
            print(f"[SPAM] msg_id={msg_id} text={text[:80]!r}")
            if not DRY_RUN:
                try:
                    api_call('deleteMessage', {'chat_id': CHAT_ID, 'message_id': msg_id})
                    print(f"[DELETED] msg_id={msg_id}")
                    deleted += 1
                except Exception as e:
                    print(f"[ERROR] Failed to delete msg_id={msg_id}: {e}")
            else:
                print(f"[DRY-RUN] Would delete msg_id={msg_id}")
                deleted += 1
    
    save_state(last_update_id)
    print(f"[TrashClean] Done. checked={checked}, deleted={deleted}, last_update_id={last_update_id}")
    return 0

if __name__ == '__main__':
    exit(main())