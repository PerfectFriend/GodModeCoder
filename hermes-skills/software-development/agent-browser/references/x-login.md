# Кейс: логин в X.com для поиска трендов

Контекст: пользователь (Master Inquisitor) исследует AI/код-тренды через свой X-аккаунт. API X заблокирован («злодеи заблокировали») — только браузерный путь. Сессия 2026-08-04, тема поиска «автономная граф-эволюция» (граф-эволюция).

## Рабочий путь (проверен в сессии)

1. `agent-browser close --all` — сброс демона (иначе новые флаги игнорируются).
2. Убить все фоновые процессы запуска браузера (process kill) — они держат демон со старыми параметрами.
3. Запуск:
   ```bash
   export PATH="$HOME/AppData/Local/hermes/hermes-agent/node_modules/.bin:$PATH"
   agent-browser --headed --profile "$HOME/.agent-browser/profiles/xcom" open "https://x.com/login"
   ```
4. Пользователь логинится в видимом окне: email/телефон + пароль. **НЕ кнопка «Continue with Google»** — Google блокирует вход из automation-браузера («Не удалось войти в аккаунт», «может быть небезопасно»).
5. Проверка: `agent-browser get url` → должен стать `https://x.com/home` (лента) — залогинен.

## Грабли по пути (что НЕ работает)

- **Google OAuth из automation-браузера** — всегда блок. Вход только прямой (email/пароль/телефон). X.com сам automation пускает нормально.
- **Редирект на accounts.google.com при открытии `x.com/home`** — в куках профиля остался незавершённый OAuth-флоу от прошлой попытки. Фикс: открывать `https://x.com/login` напрямую.
- **Запуск пользовательского Chrome (`--remote-debugging-port=9222/9223` + `--user-data-dir` + `--profile-directory=Default`)** — процесс стартует, профиль с логином открывается, НО CDP-порт не слушается (Chrome 151 на Windows), `--auto-connect` не находит инстанс. Не тратить время — сразу путь через `agent-browser --headed --profile <путь>`.
- **`--executable-path` с MSYS-путём** (`/c/Program Files/...`) — «Системе не удается найти указанный путь». Только Windows-путь `C:\Program Files\...`.
- **Профиль Chrome пользователя нельзя взять, пока Chrome запущен** — профиль блокирован первым процессом (SingletonLock). Сначала убить все процессы chrome (Get-Process chrome | Stop-Process -Force), потом запускать.

## Поиск по теме (что накопал через Brave, август 2026)

Тема «autonomous graph evolution» / «граф-эволюция» — свежие англоязычные зацепки:
- Neo4j NODES AI 2026 — «Agentic GraphRAG: autonomous knowledge graph construction and adaptive retrieval» (neo4j.com/videos/nodes-ai-2026-agentic-graphrag-...)
- Sartech Labs — «Graph Engineering: The Next Evolution» (sartechlabs.com/blog/graph-engineering-guide)
- AI Builder Club — «Graph Engineering with Claude Code» (aibuilderclub.com/blog/graph-engineering-with-claude-code)
- LangChain LangGraph — Graph API (docs.langchain.com/oss/python/langgraph/graph-api)
- MIT Tech Review 2026-08-03 — «Why AI agents lie and cheat to reach their goals»

Поисковая методика (какие движки капчат, что работает) — в скилле `web-search-fallbacks`.
