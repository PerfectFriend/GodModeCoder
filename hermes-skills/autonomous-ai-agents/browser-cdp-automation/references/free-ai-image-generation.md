# Бесплатная генерация изображений: рецепты и приоритет (2026-08)

Когда нужно сгенерировать картинку (баннер, иллюстрацию) и API-ключи не работают.
Проверено в порядке приоритета — **веб-UI всегда запасной и рабочий вариант**.

## Приоритет способов (от лучшего к худшему)

| Способ | Статус 2026-08 | Комментарий |
|---|---|---|
| **Веб-UI Gemini/ChatGPT** | ✅ работает всегда | Отдельная бесплатная квота, не связана с API-ключами |
| HuggingFace Spaces (gradio_client) | ⚠️ ZeroGPU-квота анонима = 0 | `You have exceeded your ZeroGPU quota` — нужен HF-токен |
| Gemini API (generativelanguage) | ❌ 429 quota | Ключи из пула умирают быстро |
| Pollinations.ai | ❌ 402 Insufficient balance | Теперь платный (pollen) |
| NVIDIA NIM (ai.api.nvidia.com) | ⚠️ эндпоинты устаревают | SDXL 404; FLUX требует размеры из списка (768/832/.../1344) |

## Рецепт: веб-UI Gemini (рабочий, бесплатный)

1. Открыть `https://gemini.google.com/app` в CDP-браузере (залогинен).
2. Промпт → поле `.ql-editor` (contenteditable), ввод через `Input.insertText`.
3. Enter → ждать **45–75 сек**.
4. **Gemini сам скачивает файл** в `~/Downloads/Gemini_Generated_Image_*.png` — просто забрать оттуда.
   (Размер 2400×448 для широкого баннера — сам подбирает под «wide banner 16:3».)

## Рецепт: веб-UI ChatGPT (рабочий, бесплатный)

1. Открыть `https://chatgpt.com/`, поле `#prompt-textarea` (fallback textarea), ввод через `Input.insertText`.
2. Enter → ждать **~2 мин** (дольше Gemini).
3. Картинка: `img` с `naturalWidth > 1000` и `src` содержащим `estuary` → fetch → base64 → сохранить
   (см. SKILL.md «Извлечение сгенерированных картинок»).
   Размер 1672×941 — «Mosaic Cyberpunk City Beneath a Watchful Moon»-стиль.

## Промпты, давшие хорошие баннеры (киберпанк × Ван Гог × Гауди)

```
wide cinematic banner, cyberpunk neon city at night in the style of Van Gogh Starry Night,
swirling glowing brushstrokes, Gaudí trencadis mosaic fragments, electric blue and magenta neon,
security camera silhouette, wire mesh fence, futuristic AI surveillance, ultra detailed
```

Негатив/пометка: `Do NOT put any text on the image` — иначе модель рисует буквицы.

## Питфоллы

- **Не проверяй генерацию по `document.querySelectorAll('img')` сразу** — на странице полно аватарок
  (`lh3.googleusercontent.com/a/ACg...`, `s32-c`); фильтруй по `naturalWidth > 500/1000` и по src.
- Gemini может отдать blob-URL (`blob:https://gemini.google.com/...`) — fetch по нему из CDP работает,
  но проще дождаться автоскачивания в Downloads.
- Кнопка «Create API key» в Google AI Studio создаёт ключ, но он **скрыт** в DOM (masked `...tv2w`);
  `navigator.clipboard.readText()` вернёт пусто без permission — не трать время, используй веб-UI вместо API.
- gradio_client: ответ может быть строкой-путём, dict'ом или списком dict'ов — обработка
  `get_path()` должна покрывать все три варианта (в сессии упало на строке).
