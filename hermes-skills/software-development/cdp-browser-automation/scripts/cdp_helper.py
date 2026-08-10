#!/usr/bin/env python3
"""
cdp_helper.py — переиспользуемый CDP-помощник для Chrome automation.

Предпосылка: Chrome запущен с
  --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir=<копия профиля>

Использование:
  from cdp_helper import CDP
  c = CDP(9222)
  c.navigate("https://github.com/new")          # по URL вкладки
  c.eval("document.title")                       # выполнить JS, вернуть значение
  c.fill("#repository-name-input", "repo")       # нативный setter + input/change
  c.insert_text("ssh-ed25519 AAAA...")           # реальные клавиши в фокус
  c.click_button("Create repository")            # кнопка по тексту (regex)
  c.radio_by_text("private")                     # radio по тексту label
"""

import json
import time
import urllib.request
import websocket


class CDP:
    def __init__(self, port=9222, url_filter=None):
        self.base = f"http://127.0.0.1:{port}"
        self.url_filter = url_filter  # подстрока URL вкладки (напр. "github.com")
        self.ws = None

    def _tabs(self):
        return json.load(urllib.request.urlopen(f"{self.base}/json", timeout=5))

    def _pick_ws(self):
        tabs = self._tabs()
        for t in tabs:
            u = t.get("url", "")
            if t.get("type") == "page" and (not self.url_filter or self.url_filter in u):
                return t["webSocketDebuggerUrl"]
        raise RuntimeError(f"вкладка с '{self.url_filter}' не найдена")

    def _send(self, method, params=None, mid=None):
        if self.ws is None:
            self.ws = websocket.create_connection(self._pick_ws(), timeout=25)
        msg_id = mid or int(time.time() * 1000) % 100000
        self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == msg_id:
                return msg
            if msg.get("method") == "Page.frameNavigated":  # проброс навигаций
                continue

    def eval(self, expression, return_by_value=True):
        r = self._send("Runtime.evaluate",
                       {"expression": expression, "returnByValue": return_by_value})
        return r.get("result", {}).get("result", {}).get("value")

    def navigate(self, url, wait=6):
        self._send("Page.navigate", {"url": url})
        time.sleep(wait)
        return self.eval("location.href")

    def fill(self, selector, value):
        """Нативный setter (React-совместимый) + input/change события."""
        return self.eval(f"""
          (() => {{
            const el = document.querySelector({json.dumps(selector)});
            if (!el) return 'NO_EL: ' + {json.dumps(selector)};
            const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
            Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, {json.dumps(value)});
            el.dispatchEvent(new Event('input', {{bubbles: true}}));
            el.dispatchEvent(new Event('change', {{bubbles: true}}));
            return 'OK: ' + el.value.slice(0, 30);
          }})()
        """)

    def insert_text(self, text, selector=None):
        """Input.insertText — реальные клавиши в элемент с фокусом.
        Если selector задан — сначала фокус на него (иначе пишет в текущий фокус!)."""
        if selector:
            self.eval(f"document.querySelector({json.dumps(selector)}).focus(); true")
            time.sleep(0.3)
        self._send("Input.insertText", {"text": text})
        time.sleep(0.3)

    def click_button(self, text_regex, scope="document"):
        """Клик по кнопке/элементу, чей текст матчит regex."""
        return self.eval(f"""
          (() => {{
            const root = {scope};
            const els = Array.from(root.querySelectorAll('button, [role="button"], a, summary'));
            const re = new RegExp({json.dumps(text_regex)}, 'i');
            const el = els.find(e => re.test((e.innerText || '').trim()));
            if (!el) return 'NO_BTN';
            el.click();
            return 'CLICKED: ' + (el.innerText || '').trim().slice(0, 40);
          }})()
        """)

    def radio_by_text(self, text_regex):
        """Клик по radio-кнопке, чей label/значение матчит regex."""
        return self.eval(f"""
          (() => {{
            const radios = Array.from(document.querySelectorAll('input[type="radio"]'));
            const re = new RegExp({json.dumps(text_regex)}, 'i');
            const r = radios.find(x => re.test((x.value||'') + ' ' + ((x.closest('label')||{{}}).innerText||'')));
            if (!r) return 'NO_RADIO';
            if (!r.checked) r.click();
            return 'RADIO: ' + (r.value || '');
          }})()
        """)

    def close(self):
        if self.ws:
            self.ws.close()
            self.ws = None
