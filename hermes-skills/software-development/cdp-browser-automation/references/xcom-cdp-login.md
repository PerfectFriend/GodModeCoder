# X.com через CDP: логин, поиск, извлечение

Проверено 2026-08: вход в X через CDP-порт после копии профиля.

## Логин X (последовательность шагов)

1. Открыть `https://x.com/login` (или `/home` → редирект на `x.com/i/jf/onboarding/web?mode=login`).
2. Поля формы: `input[name="username_or_email"]` + `input[type="password"]`.
3. Кнопка: текст `Продолжить` (НЕ «Вход с аккаунтом Google» — он заблокирован для automation).
4. Дальше возможны ступени онбординга (URL вида `x.com/i/jf/onboarding/web#/s/...`):
   - `knowledge_check` — «Подтверди свой аккаунт» → поле `input[name="challenge_response"]` = username **без @**.
   - `verify_code` — «Проверьте свою электронную почту» → код из письма в поле `Verification code`.
5. Готово: `x.com/home`, лента. Куки сохраняются в скопированном профиле (chrome-x).

## Поиск по X

URL: `https://x.com/search?q=<query>&src=typed_query&f=live`

- `f=live` — свежие посты (Latest); без него — Top.
- `f=image` — только посты с картинками (диаграммы/схемы — золото для изучения трендов).
- **НЕ ставить кавычки** в запросе: `q=graph ai` работает, `q="graph ai"` → «No results for "..."».
- Короткие запросы лучше длинных: «graph ai», «graph engineering», «loop engineering».
- После `Page.navigate` — sleep 8–10 с (SPA грузится), потом `Runtime.evaluate`.

## Скрипт-заготовка (Python, websocket-client)

```python
import json, urllib.request, websocket, sys, time

def tabs():
    return json.load(urllib.request.urlopen('http://127.0.0.1:9222/json'))

def find_ws(url_part='x.com'):
    for t in tabs():
        if url_part in t.get('url','') and 'blob' not in t.get('url',''):
            return t['webSocketDebuggerUrl']
    return None

def ev(ws, js):
    w = websocket.create_connection(ws, timeout=25)
    w.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate',
                       'params': {'expression': js, 'returnByValue': True}}))
    while True:
        m = json.loads(w.recv())
        if m.get('id') == 1:
            w.close()
            return m.get('result', {}).get('result', {}).get('value')

# 1. поиск
ws = find_ws()
ev(ws, f"location.href='https://x.com/search?q={urllib.request.quote('graph ai')}&src=typed_query&f=live'")
time.sleep(9)

# 2. извлечение постов
js = """(() => {
  const arts = Array.from(document.querySelectorAll('article'));
  return JSON.stringify(arts.slice(0,15).map(a => ({
    text: a.innerText.slice(0,300),
    time: (a.querySelector('time')||{}).getAttribute?.( 'datetime') || null,
    href: (a.querySelector('a[href*=\\"/status/\\"]')||{}).href || null
  })));
})()"""
print(ev(ws, js))

# 3. заполнение React-поля (логин)
js_fill = """(() => {
  const setVal = (el, val) => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el, val);
    el.dispatchEvent(new Event('input', {bubbles:true}));
    el.dispatchEvent(new Event('change', {bubbles:true}));
  };
  setVal(document.querySelector('input[name="username_or_email"]'), EMAIL);
  return 'ok';
})()"""
```

## Полезные селекторы X
- Посты: `article`
- Ссылка на пост: `a[href*="/status/"]`
- Время: `time[datetime]`
- Кнопка: `[role="button"]` + фильтр по innerText
