# Поиск трендов/публикаций в X через залогиненный браузер (CDP)

Когда нужно «прочесать соцсети по теме за последние дни» (тренд-ресёрч) из аккаунта пользователя.

## Как искать

URL: `https://x.com/search?q=<query>&src=typed_query&f=live`
- `f=live` — свежие посты (Latest); без него X показывает Top.
- `f=image` — только посты с медиа.
- **Без кавычек вокруг запроса** — точная фраза в кавычках часто даёт «No results»
  (пользователь явно просил «ковычки не делай!»).
- Синонимы обязательны: если точный термин пуст, пробовать смежные
  («autonomous graph evolution» → 0; «graph engineering» → десятки свежих постов).

## Извлечение постов (Runtime.evaluate)

```js
const articles = Array.from(document.querySelectorAll('article'));
const posts = articles.slice(0, 12).map(a => ({
  text: a.innerText.slice(0, 400),
  time: (a.querySelector('time')||{}).getAttribute?.('datetime') || null,
  href: (a.querySelector('a[href*="/status/"]')||{}).href || null,
}));
```

Возвращать `JSON.stringify({count, noResults, body, posts})` — по `body.includes('No results')`
понять, пусто ли. Полезно сохранять `href` — открывать треды потом через `Page.navigate`.

## Питфоллы

- Первый поиск (с кавычками) → «No results» — это норма, не паниковать, менять формулировку.
- Тред (длинный пост) обрезается при открытии — виден только первый `article`; скролл
  (`window.scrollBy(0, 3000)`) не всегда догружает остальные части — для сводки хватает начала.
- В выдаче много видео (amplify_video_thumb) — если нужны статьи со схемами, использовать `f=image`
  и фильтровать посты с `img` не-аватарками.
- X часто делает редирект на onboarding/Google при нелогиненом профиле — проверять
  `location.href` и наличие `article` перед извлечением.

## Кейс 2026-08: «автономная граф-эволюция» = Graph Engineering

Тренд лета-2026 в AI-сообществах: **Graph Engineering** (эволюция от Prompt → Context →
Skills → Loop → Graph). Ключевые термины для поиска: `graph engineering`, `loop engineering`,
`harness engineering`, `self-evolving graph`. Anthropic: «85% инженеров запускают сотни агентов —
способ — graph engineering»; «Prompt testing — старый воркфлоу, graph evaluation — новый».
