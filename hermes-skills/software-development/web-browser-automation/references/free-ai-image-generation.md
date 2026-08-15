# Бесплатная AI-генерация изображений (когда API-ключи исчерпаны)

Проверено 2026-08-05. Цель: получить рекламные баннеры (киберпанк × Ван Гог × Гауди)
без денег, когда API-пути мертвы.

## Что НЕ работает (не трать время)

| Путь | Почему мёртв |
|---|---|
| `image.pollinations.ai` | теперь требует платный баланс "pollen" (HTTP 402) |
| Gemini API-ключи (generativelanguage.googleapis.com) | лимит 429 на обоих ключах аккаунта |
| HuggingFace Spaces (FLUX.1-schnell, SD3-medium) | ZeroGPU-квота анонима = 0s; нужно авторизоваться |
| NVIDIA API (ai.api.nvidia.com FLUX) | медленный (таймаут 180с), размеры жёстко ограничены списком |

## Что РАБОТАЕТ: веб-интерфейсы через браузер (agent-browser + CDP)

**Ключевой инсайт:** у веб-UI (gemini.google.com, chatgpt.com) свои бесплатные лимиты,
отдельные от API-ключей того же аккаунта. Через браузер генерация проходит даже когда
API-ключи дают 429.

### Gemini (gemini.google.com/app) — лучший для широких баннеров
1. Открыть в браузере, дождаться загрузки (залогинен через профиль)
2. Поле ввода: `document.querySelector('.ql-editor')` → focus → `Input.insertText(prompt)`
3. Enter (dispatchKeyEvent keyDown/keyUp)
4. Ждать 45-90с; URL сменится на `/app/<id>` — значит чат создан
5. Картинка: `<img>` с blob-URL или googleusercontent; **Gemini сам скачивает файл**
   в `~/Downloads/Gemini_Generated_Image_*.png` — проверь Downloads в первую очередь!
6. Результат: 2400×448 (идеальный широкий баннер) для промпта "wide cinematic banner"

### ChatGPT (chatgpt.com) — детальнее, 16:9
1. Поле: `#prompt-textarea` → focus → `Input.insertText`
2. Enter, ждать 60-120с (gpt-image-1 дольше)
3. Картинка: `img[src*="backend-api/estuary"]` с naturalWidth > 1000
4. Скачивание: `fetch(img.src)` → arrayBuffer → b64 → записать файл (CDP awaitPromise)
5. Результат: 1672×941, «Mosaic Cyberpunk City Beneath a Watchful Moon» стиль

## Скачивание картинки через CDP (универсальный способ)

```js
// Runtime.evaluate с awaitPromise=true, returnByValue=true
(async () => {
  const img = Array.from(document.querySelectorAll('img'))
    .find(i => i.naturalWidth > 500);
  const resp = await fetch(img.src);
  const blob = await resp.blob();
  const buf = await blob.arrayBuffer();
  const bytes = new Uint8Array(buf);
  let bin = '';
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return {b64: btoa(bin), mime: blob.type, size: bytes.length};
})()
```

Потом в Python: `base64.b64decode(d['b64'])` → `Path(...).write_bytes(...)`.

## Fallback без AI: программные баннеры (PIL)

`scripts/gen_banners.py` — рабочий генератор баннеров на чистом PIL без сети:
неоновый текст со свечением (neon_text), вихревые мазки Ван Гога (спирали линий),
тренкадис-мозаика Гауди (случайные многоугольники), киберпанк-цепи (ломаные линии).
Параметры: 1600×480 RGBA, детерминирован по seed (same seed → same output).
Стиль задаётся промптом для AI, но PIL-версия — гарантированный оффлайн-запас.

## Промпт-паттерн для баннеров

```
wide cinematic banner (16:3), cyberpunk neon city at night in the style of
Van Gogh Starry Night, swirling glowing brushstrokes, Gaudí trencadis mosaic
fragments, electric blue and magenta neon, [subject], ultra detailed,
Do NOT put any text on the image
```

Проверка результата без vision: PIL-метрики — яркость (тёмная ночь ~55-70),
контраст (std > 50), доля ярких пикселей (неоновые акценты ~3%), доминирующий
канал RGB (B>R = холодный киберпанк, R>B = тёплое золото Гауди).
