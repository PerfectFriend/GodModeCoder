Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
type: reference
tags: ["#second-brain", "#obsidian", "#method", "#hermes"]
s
C:\Vault\Second Brain Method.md


ource: "https://x.com/i/status/2082760310792798495"
date: 2026-08-09
---

# Second Brain — метод Ryven (твит @imryven)

## Источник
- Твит «I Replaced a $2,000 Assistant With a $20 Second Brain», @imryven (Ryven), 2026-07-30, 413.6K просмотров
- https://x.com/i/status/2082760310792798495 (внутри — ссылка на предысторию про ассистента за $2000)

## Суть метода (6 компонентов)
1. **writing-style.md** — анализ стиля автора по 3 образцам (длина предложений, ритм, словарь, открытия/закрытия, формальность, избегаемое); читать перед любым написанием.
2. **Структура проекта**: Inputs / Process / Outputs / Feedback + CLAUDE.md внутри (что за проект, единственная цель, что значит «готово», роль агента; интервью при неясностях).
3. **Компаундинг**: каждый ответ агента возвращается в wiki новой страницей; противоречия фиксируются с датами; паттерны копятся.
4. **Ежедневный обход 7:00**: агент сам ходит по vault, линкует новое со старым, флагает устаревшее (>2 недель), шлёт 3 строки: что изменилось за ночь / что требует внимания / что непоследовательно.
5. **raw → wiki → output**: raw = неизменяемые источники; wiki = сгенерированные статьи из raw; output = готовые результаты. CLAUDE.md в корне читается каждую сессию.
6. **CLAUDE.md = полная картина человека**: кто ты, как думаешь, что строишь, где застреваешь, как с тобой говорить (собирается интервью по одному вопросу).

## Адаптация под стек Hermes (применено 2026-08-09)
| Компонент Ryven | Аналог в стеке |
|---|---|
| CLAUDE.md (корень) | `C:\Vault\BRAIN.md` (имя CLAUDE.md защищено guard'ом — см. pitfalls) |
| Inputs | `C:\Vault\Inbox\` (сырьё, immutable) + `processed/` |
| wiki | Reference-заметки в корне vault (frontmatter `type: reference`) |
| Индекс знаний | `Учебник.md` (чек-лист, категории с приоритетами, 🟢/🔴) |
| output | `Projects.md`, готовые артефакты |
| writing-style.md | `C:\Vault\writing-style.md` (черновик) |
| Ежедневный обход 7:00 | cron `second-brain-daily` → DM 519292 (3 строки) |
| Память агента | memory-engineering: дедуп, прунинг при >90%, противоречия с датами |

## Вывод
Метод дёшев и воспроизводим (у Ryven $20/мес; в стеке Hermes — локально, бесплатно). Ключевая идея: «перестать сбрасывать и начать компаундить» — каждое исследование/ответ оседает в vault и линкуется со старым. Ограничения: нужна дисциплина разбора Inbox; Учебник не перегружать мусором; «бесплатно/фичи» быстро меняются.
