# Multi-Language README Pattern for International Deployments

**Context**: SuperGuard Alarm deployed in Spain with multi-language clientele (RU/EN/ES).

## Pattern

Every README file in the repo carries the same header line for cross-navigation:

```markdown
**[English](README.md) | [Русский](README.ru.md) | [Español](README.es.md)**
```

- **README.md** (English) is the default rendered by GitHub
- **README.ru.md** — Russian
- **README.es.md** — Spanish
- Links are relative (work on any fork)
- Added 2026-08-06 per client requirement: "английский вариант ставь по умолчанию" + links in header

## Implementation Notes

- Keep the three files in sync for structure/sections — only translate content
- The language switcher header is identical in all three (copy-paste)
- GitHub renders README.md by default; users click their language
- This pattern applies to any project with international users