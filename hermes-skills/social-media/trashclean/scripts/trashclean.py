#!/usr/bin/env python3
"""
TrashClean — Telegram Spam Cleaner
Auto-deletes spam/flood messages in a Telegram group via Bot API.
"""

import os
import re
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

# Load .env from Hermes home
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / "AppData" / "Local" / "hermes"))
ENV_PATH = HERMES_HOME / ".env"

def load_env():
    """Load environment variables from .env file."""
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"')

load_env()

# Configuration
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CLEANUP_CHAT_ID")

# Default patterns from skill
DEFAULT_PATTERNS = r"(.)\1{4,}|[A-ZА-Я]{10,}|https?://\S+|(купи|продам|заработ|крипт|биткоин|казино|ставки|лотерея|выигрыш|бонус|промокод|скидка|акция).{0,3}\d|^\s*[💰💵💎🚀🔥⚡️✨🎁💸🤑]{3,}\s*$"

PATTERNS = os.environ.get("TELEGRAM_CLEANUP_PATTERNS", DEFAULT_PATTERNS)
MAX_AGE = int(os.environ.get("TELEGRAM_CLEANUP_MAX_AGE", "300"))
DRY_RUN = os.environ.get("TELEGRAM_CLEANUP_DRY_RUN", "false").lower() == "true"

# State file for persistence
STATE_DIR = HERMES_HOME / "state"
STATE_DIR.mkdir(exist_ok=True)
STATE_FILE = STATE_DIR / "last_update_id.txt"

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def load_state():
    """Load last processed update_id."""
    if STATE_FILE.exists():
        try:
            return int(STATE_FILE.read_text().strip())
        except:
            return 0
    return 0

def save_state(update_id):
    """Save last processed update_id."""
    STATE_FILE.write_text(str(update_id))

def api_call(method, params=None):
    """Make a Telegram Bot API call."""
    url = f"{API_BASE}/{method}"
    data = None
    if params:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        log(f"API error ({method}): {e}")
        return {"ok": False, "error": str(e)}

def split_patterns(pattern_string):
    """Split pattern string by | respecting parentheses."""
    parts = []
    current = []
    paren_depth = 0
    
    for char in pattern_string:
        if char == '(':
            paren_depth += 1
            current.append(char)
        elif char == ')':
            paren_depth -= 1
            current.append(char)
        elif char == '|' and paren_depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            current.append(char)
    
    if current:
        parts.append(''.join(current).strip())
    
    return [p for p in parts if p]

def compile_patterns(pattern_string):
    """Compile regex patterns from newline-separated or pipe-separated string."""
    patterns = []
    
    # Try splitting by newlines first (each line is a pattern)
    lines = [line.strip() for line in pattern_string.split("\n") if line.strip() and not line.strip().startswith("#")]
    
    if len(lines) > 1:
        # Multi-line format: each line is a pattern
        for line in lines:
            if line.endswith("|"):
                line = line[:-1]
            try:
                patterns.append(re.compile(line, re.IGNORECASE))
            except re.error as e:
                log(f"Invalid regex pattern '{line}': {e}")
    else:
        # Single line - split by | respecting parentheses
        for p in split_patterns(pattern_string):
            try:
                patterns.append(re.compile(p, re.IGNORECASE))
            except re.error as e:
                log(f"Invalid regex pattern '{p}': {e}")
    return patterns

def is_spam(text, patterns):
    """Check if message text matches any spam pattern."""
    if not text:
        return False
    for pattern in patterns:
        if pattern.search(text):
            return True
    return False

def delete_message(chat_id, message_id):
    """Delete a message via Bot API."""
    if DRY_RUN:
        log(f"[DRY RUN] Would delete message {message_id} in chat {chat_id}")
        return True
    result = api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
    if result.get("ok"):
        log(f"Deleted message {message_id}")
        return True
    else:
        log(f"Failed to delete message {message_id}: {result}")
        return False

def main():
    if not BOT_TOKEN:
        log("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        return 1
    if not CHAT_ID:
        log("ERROR: TELEGRAM_CLEANUP_CHAT_ID not set in .env")
        return 1

    try:
        chat_id = int(CHAT_ID)
    except ValueError:
        log(f"ERROR: Invalid CHAT_ID: {CHAT_ID}")
        return 1

    log(f"Starting trashclean for chat {chat_id} (dry_run={DRY_RUN})")

    patterns = compile_patterns(PATTERNS)
    log(f"Loaded {len(patterns)} spam patterns")

    last_update_id = load_state()
    log(f"Last processed update_id: {last_update_id}")

    # Get updates
    params = {"offset": last_update_id + 1, "timeout": 5, "allowed_updates": ["message"]}
    result = api_call("getUpdates", params)

    if not result.get("ok"):
        log(f"Failed to get updates: {result}")
        return 1

    updates = result.get("result", [])
    if not updates:
        log("No new updates")
        return 0

    deleted_count = 0
    checked_count = 0

    for update in updates:
        update_id = update["update_id"]
        last_update_id = max(last_update_id, update_id)

        message = update.get("message")
        if not message:
            continue

        # Only process messages in target chat
        if message.get("chat", {}).get("id") != chat_id:
            continue

        # Check message age
        msg_date = message.get("date", 0)
        age = int(time.time()) - msg_date
        if age > MAX_AGE:
            log(f"Skipping message {message.get('message_id')} (age {age}s > {MAX_AGE}s)")
            continue

        text = message.get("text", "") or message.get("caption", "")
        message_id = message.get("message_id")

        checked_count += 1

        if is_spam(text, patterns):
            log(f"SPAM detected: message {message_id} - '{text[:80]}...'")
            if delete_message(chat_id, message_id):
                deleted_count += 1
        else:
            log(f"OK: message {message_id} - '{text[:80]}...'")

    save_state(last_update_id)
    log(f"Done. Checked: {checked_count}, Deleted: {deleted_count}")
    return 0

if __name__ == "__main__":
    exit(main())