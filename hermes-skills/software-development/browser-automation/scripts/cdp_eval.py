#!/usr/bin/env python3
"""Evaluate JavaScript on a Chrome tab via CDP (port 9222).

Usage:
    python cdp_eval.py <url_substring> '<js expression>'
    python cdp_eval.py "x.com" "document.body.innerText.slice(0,500)"

Finds the first tab whose URL contains url_substring, connects via its
webSocketDebuggerUrl, runs Runtime.evaluate with returnByValue, prints result.
Requires: websocket-client (uv pip install websocket-client)
"""
import json
import sys
import urllib.request

try:
    import websocket
except ImportError:
    print("Missing dep: run  uv pip install websocket-client", file=sys.stderr)
    sys.exit(2)

CDP_HTTP = "http://127.0.0.1:9222"


def find_tab(url_part):
    tabs = json.load(urllib.request.urlopen(CDP_HTTP + "/json"))
    for t in tabs:
        u = t.get("url", "")
        if url_part in u and "blob:" not in u and "accounts.google" not in u:
            return t["webSocketDebuggerUrl"]
    return None


def eval_js(ws_url, expression, timeout=20):
    ws = websocket.create_connection(ws_url, timeout=timeout)
    try:
        ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate",
                            "params": {"expression": expression,
                                       "returnByValue": True}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == 1:
                return msg.get("result", {}).get("result", {}).get("value", None)
    finally:
        ws.close()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    url_part, expr = sys.argv[1], sys.argv[2]
    ws_url = find_tab(url_part)
    if not ws_url:
        print(f"NO TAB containing '{url_part}'. Tabs:")
        for t in json.load(urllib.request.urlopen(CDP_HTTP + "/json")):
            print(f"  - {t.get('title','')[:40]} | {t.get('url','')[:70]}")
        sys.exit(1)
    result = eval_js(ws_url, expr)
    print(result if result is not None else "NO VALUE / undefined")


if __name__ == "__main__":
    main()
