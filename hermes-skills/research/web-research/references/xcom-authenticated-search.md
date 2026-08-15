# agent-browser + X.com (авторизованный поиск по постам)

Контекст: X API заблокирован (был, отозвали). Рабочий путь — автоматизация браузера
через agent-browser CLI с профилем, в который пользователь логинится вручную один раз.

## Установка (однократно)

```bash
# Бинарник живёт в node_modules Hermes, не в PATH:
export PATH="$HOME/AppData/Local/hermes/hermes-agent/node_modules/.bin:$PATH"

agent-browser install   # качает Chrome ~192MB в C:\Users\tomas\.agent-browser\browsers\chrome-151.0.7922.76
```

Ключевые флаги (из `agent-browser --help` и `agent-browser skills get core`):
- `--headed` — видимое окно (по умолчанию headless!)
- `--profile <путь>` — **полный путь к директории**, голое имя не работает («profile not found»)
- `--session-name <name>` — автосохранение/восстановление сессии
- `--session <name>` — изолированная сессия
- `auth save <name> --url ... --username ... --password-stdin` — vault для кредов
- `state save ./auth.json` / `--state ./auth.json` — куки+localStorage

## Флоу «пользователь логинится сам»

1. Создать директорию профиля:
   `mkdir -p ~/.agent-browser/profiles/xcom`

2. Открыть X.com в видимом окне (в background! open в headed блокирует терминал):
   ```bash
   agent-browser --headed --profile "$HOME/.agent-browser/profiles/xcom" open "https://x.com/home"
   ```
   → запускать с background=true, состояние проверять отдельными вызовами:
   ```bash
   agent-browser get title   # "X. Главное происходит здесь. / X"
   agent-browser get url
   agent-browser snapshot -i # доступные элементы (кнопки логина, поля)
   ```

3. Пользователь логинится в открытом окне (пароль/2FA вводит сам, не агенту).
   На странице логина есть: «Принять все файлы cookie», кнопки Google/Apple,
   поле «Электронная почта или имя пользователя».

4. После «готово» от пользователя — профиль сохранён, можно искать:
   ```bash
   agent-browser --profile "$HOME/.agent-browser/profiles/xcom" open "https://x.com/search?q=%22autonomous+graph+evolution%22&f=live"
   agent-browser snapshot -i   # посты, сниппеты
   ```
   Параметры поиска X: `f=live` (последние), `f=top`, `src=typed_query`.

## Питфоллы (проверено на практике)

- **Профиль голым именем** → ошибка `Chrome profile "xcom" not found. Available profiles: Default`.
  Всегда полный путь — ИЛИ используй реальный профиль юзера (см. ниже).
- **`open` в headed** → команда висит до закрытия окна (timeout 120s). Лечится background=true.
- **Кириллица в URL браузера Hermes** → utf-8 codec error; percent-encode (или curl).
- **Google OAuth блокирует automation-Chrome** («может быть небезопасно»): Google распознаёт
  Chrome for Testing/свежий профиль и режет вход. Юзер входит **родным логином X**
  (телефон/почта + пароль + 2FA), а НЕ через Google-кнопку.
- **X.com зацикливается на Google-редиректе**: после незавершённого OAuth-флоу `x.com/home`
  упорно кидает на `accounts.google.com`. Лечится прямым открытием `https://x.com/login`
  (в обход home); email подставляется автозаполнением профиля.
- **Реальный профиль юзера (Default) — можно и нужно использовать**, если юзер уже залогинен
  в X в своём Chrome: `agent-browser --headed --executable-path "C:\Program Files\Google\Chrome\Application\chrome.exe" --profile Default open "https://x.com/login"`.
  Требования: (1) `agent-browser close --all` сначала — демон держит старые опции запуска;
  (2) юзер **полностью закрыл свой Chrome** (все окна), иначе «profile in use»;
  (3) `--executable-path` — **Windows-путь** (`C:\...`); MSYS `/c/Program Files/...` падает
  с `os error 3` («Системе не удается найти указанный путь»).
  Список профилей: `agent-browser profiles`.
- Chrome для автоматизации — отдельная копия, не конфликтует с Opera/основным Chrome
  (пока не трогаешь профиль Default).

## Куда копать дальше по теме (свежее, август 2026)

Найдено через Brave (tf=pd) до авторизации в X:
- Neo4j NODES AI 2026 — «Agentic GraphRAG: autonomous knowledge graph construction and adaptive retrieval»
- Sartech Labs — «Graph Engineering: The Next Evolution»
- AI Builder Club — «Graph Engineering with Claude Code»
- LangChain LangGraph Graph API
- MIT Tech Review 03.08.2026 — «Why AI agents lie and cheat to reach their goals»

Пользовательский запрос: «автономная граф-эволюция» — тренд в AI/код-сообществах X,
переход от циклической эволюции (The Grimoire protocol) к граф-эволюции.
