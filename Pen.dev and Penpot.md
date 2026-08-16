Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
type: reference
tags: ["#design", "#ai", "#mcp", "#opensource", "#tools"]
so
C:\Vault\Pen.dev and Penpot.md


urce: "https://x.com/i/status/2086107198640300369"
date: 2026-08-09
---

# Pen.dev и Penpot — AI-нативные дизайн-инструменты

## Источник

- Твит @midudev (Miguel Ángel Durán), 2026-08-08: https://x.com/i/status/2086107198640300369 (2.1k лайков)
- Суть: «Если Figma и Claude Code имели бы ребёнка — это pen.dev. Генерирует интерфейсы, правишь вживую. Работает с Codex, Cursor, Claude Code... Windows, macOS, Linux. Сейчас бесплатно»
- Топ-комментарий @Valen: «Лучше Penpot, и он open-source» — https://penpot.app/
- Комментарий @astranua: в pen.dev можно создавать design systems (lib.pen) для примитивов фронтенда — агент не выдумывает дизайн, а берёт компонент из библиотеки. Всё в одном репозитории
- Контр-комментарий @IACadaDia: промежуточные слои «режут» часть возможностей, вернулся к чистому Claude Code (мнение одного пользователя)

## Pen.dev (бывш. pencil.dev)

| Параметр | Значение |
|---|---|
| Сайт | https://www.pen.dev/ (docs: https://docs.pencil.dev/) |
| Что это | Agent-driven MCP-канвас: векторный дизайн-инструмент, живёт внутри IDE рядом с кодом |
| Формат | Открытый формат `.pen` (файлы в репозитории — «design as code») |
| Интеграции | VSCode, Cursor, Claude Code, OpenAI Codex, любой IDE; MCP read + полный write-доступ |
| Фичи | Бесконечный канвас, генерация экранов/флоу AI-агентами (AI Multiplayer / SWARM — параллельные агенты), импорт из Figma (copy-paste: векторы, текст, стили), design kits, генерация HTML/CSS/React «пиксель-в-пиксель» |
| Экосистема | Подключаются другие MCP: БД, API, чарты, Playwright/Puppeteer; файлы версионируются в Git |
| Бэкер | Speedrun |
| Платформы | Windows, macOS, Linux; сейчас бесплатно |
| ⚠️ Отзывы | Красный дит: быстро жрёт токены Claude; по возможностям далеко до Figma |

## Penpot

| Параметр | Значение |
|---|---|
| Сайт | https://penpot.app/ (GitHub: https://github.com/penpot/penpot, 58.3k ⭐) |
| Что это | Open-source дизайн-платформа (веб-приложение), альтернатива Figma |
| Лицензия | MPL-2.0, разработчик — Kaleidos INC (Испания) |
| Self-host | Да, Docker-образы; также бесплатный облачный сервис |
| Стек | Clojure / ClojureScript |
| UI Design | Адаптивные/rules-based интерфейсы, вайрфреймы, интерактивные прототипы, CSS Grid и Flex |
| Design Systems | Компоненты, нативные дизайн-токены, общие библиотеки |
| AI Workflows | Интеграция любых агентов/LLM/инструментов: code-to-design, design-to-code, design-to-design |
| Code | Открытые стандарты: CSS, HTML, SVG, JSON; открытый файловый формат |
| Аудитория | Продуктовые команды, дизайнеры, разработчики, AI-агенты; self-host для compliance/governance |

## Сравнение

| Критерий | Pen.dev | Penpot |
|---|---|---|
| Модель | Локальный инструмент в IDE (десктоп) | Веб + self-host (Docker) |
| Open source | Формат открыт, сам продукт — нет | Полностью open source (MPL-2.0) |
| AI-агенты | Ядро продукта (MCP, AI Multiplayer) | AI Workflows + открытые API |
| Дизайн-системы | Design kits, lib.pen в репо | Компоненты + токены, библиотеки |
| Цена | Бесплатно (сейчас) | Free cloud / self-host |
| Ключевая идея | Дизайн = код, живёт в репозитории | Команда и агенты в одном open-source контуре |

## Выводы / применение

- Оба инструмента — ответ на «Figma vs AI-агенты»: дизайн переезжает ближе к коду (pen.dev) или в открытый self-hosted контур (Penpot)
- Pen.dev релевантен стеку Hermes/агентов: MCP-канвас с write-доступом = агент сам правит UI в репозитории
- Penpot — безопасный выбор для команд/проектов с требованиями к контролю и лицензиям (MPL-2.0, self-host)
- ⚠️ Оценки «бесплатно» и фичи быстро меняются (переименование pencil.dev → pen.dev, активная разработка)
