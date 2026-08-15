#!/usr/bin/env python3
"""
TrashClean — Auto-delete spam/flood messages in Telegram group via Bot API.
Reads config from .env, polls getUpdates, deletes matching messages.
"""

import os
import re
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

# ---------- Config ----------
def get_hermes_home() -> Path:
    # Windows: %LOCALAPPDATA%\hermes
    # Linux/macOS: ~/.hermes
    if os.name == 'nt':
        return Path(os.environ.get('LOCALAPPDATA', '')) / 'hermes'
    return Path.home() / '.hermes'

HERMES_HOME = get_hermes_home()
ENV_FILE = HERMES_HOME / '.env'
STATE_DIR = HERMES_HOME / 'state'
STATE_FILE = STATE_DIR / 'last_update_id.txt'

def load_env():
    """Load .env into os.environ (simple parser)."""
    if not ENV_FILE.exists():
        return
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

load_env()

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CLEANUP_CHAT_ID')
PATTERNS_RAW = os.environ.get('TELEGRAM_CLEANUP_PATTERNS', '')
MAX_AGE = int(os.environ.get('TELEGRAM_CLEANUP_MAX_AGE', '300'))
DRY_RUN = os.environ.get('TELEGRAM_CLEANUP_DRY_RUN', 'false').lower() == 'true'

if not BOT_TOKEN or not CHAT_ID:
    print("ERROR: TELEGRAM_BOT_TOKEN and TELEGRAM_CLEANUP_CHAT_ID must be set in .env")
    exit(1)

# Compile patterns
DEFAULT_PATTERNS = [
    (r'(.)\1{4,}', True),              # repeated char 5+ times (case-insensitive)
    (r'[A-ZА-Я]{10,}', False),         # ALL CAPS 10+ consecutive chars (CASE-SENSITIVE)
    (r'https?://\S+', True),           # bare links (case-insensitive)
    (r'(купи|продам|заработ|крипт|биткоин|казино|ставки|лотерея|выигрыш|бонус|промокод|скидка|акция).{0,3}\d', True),  # spam keywords + number
    (r'^\s*[💰💵💎🚀🔥⚡️✨🎁💸🤑]{3,}\s*$', True),  # emoji spam
]
if PATTERNS_RAW:
    # Parse custom patterns: format "pattern1|pattern2|..." all case-insensitive
    patterns_list = [(p.strip(), True) for p in PATTERNS_RAW.split('|') if p.strip()]
else:
    patterns_list = DEFAULT_PATTERNS

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE if flags else 0) for p, flags in patterns_list]

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ---------- State ----------
STATE_DIR.mkdir(parents=True, exist_ok=True)

def load_last_update_id() -> int:
    if STATE_FILE.exists():
        try:
            return int(STATE_FILE.read_text().strip())
        except:
            return 0
    return 0

def save_last_update_id(update_id: int):
    STATE_FILE.write_text(str(update_id))

# ---------- Telegram API ----------
def tg_get_updates(offset: int, timeout: int = 10) -> dict:
    url = f"{API_BASE}/getUpdates?offset={offset}&timeout={timeout}&allowed_updates=[\"message\"]"
    with urllib.request.urlopen(url) as resp:
        return json.load(resp)

def tg_delete_message(chat_id: str, message_id: int) -> dict:
    url = f"{API_BASE}/deleteMessage"
    data = urllib.parse.urlencode({'chat_id': chat_id, 'message_id': message_id}).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

# ---------- Main logic ----------
def is_spam(text: str) -> bool:
    if not text:
        return False
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            return True
    return False

def main():
    print(f"[trashclean] Starting... dry_run={DRY_RUN} chat_id={CHAT_ID}")
    print(f"[trashclean] Patterns loaded: {len(COMPILED_PATTERNS)}")
    
    last_update_id = load_last_update_id()
    print(f"[trashclean] Last update_id: {last_update_id}")
    
    now = time.time()
    deleted = 0
    checked = 0
    
    while True:
        try:
            result = tg_get_updates(last_update_id + 1)
        except Exception as e:
            print(f"[trashclean] getUpdates error: {e}")
            break
        
        if not result.get('ok'):
            print(f"[trashclean] API error: {result}")
            break
        
        updates = result.get('result', [])
        if not updates:
            print("[trashclean] No new updates")
            break
        
        for update in updates:
            update_id = update['update_id']
            last_update_id = max(last_update_id, update_id)
            
            msg = update.get('message')
            if not msg:
                continue
            
            msg_chat_id = str(msg.get('chat', {}).get('id'))
            if msg_chat_id != str(CHAT_ID):
                continue
            
            msg_id = msg.get('message_id')
            msg_date = msg.get('date', 0)
            msg_text = msg.get('text') or msg.get('caption') or ''
            
            # Skip old messages
            if now - msg_date > MAX_AGE:
                continue
            
            checked += 1
            
            if is_spam(msg_text):
                print(f"[trashclean] SPAM detected: msg_id={msg_id} text={msg_text[:80]}")
                if not DRY_RUN:
                    try:
                        del_result = tg_delete_message(CHAT_ID, msg_id)
                        if del_result.get('ok'):
                            print(f"[trashclean] ✓ Deleted msg_id={msg_id}")
                            deleted += 1
                        else:
                            print(f"[trashclean] ✗ Delete failed: {del_result}")
                    except Exception as e:
                        print(f"[trashclean] Delete error: {e}")
                else:
                    print(f"[trashclean] [DRY RUN] Would delete msg_id={msg_id}")
                    deleted += 1
        
        # Save progress after each batch
        save_last_update_id(last_update_id)
        
        # If we got fewer than 100 updates, we're caught up
        if len(updates) < 100:
            break
    
    print(f"[trashclean] Done. Checked: {checked}, Deleted: {deleted}, Last update_id: {last_update_id}")

if __name__ == '__main__':
    main()