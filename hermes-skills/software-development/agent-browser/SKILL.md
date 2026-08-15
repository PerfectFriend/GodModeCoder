---
name: agent-browser
description: "Вход в сайты через agent-browser: обход блокировок, профили."
trigger: "Вход в сайты через agent-browser: обход блокировок, профили."
---

# agent-browser — автоматизация браузера через CLI

CLI-автоматизация Chrome (CDP): логины, профили, обход анти-автоматизации. Живёт внутри hermes-agent как npm-пакет.

## Где CLI (в PATH по умолчанию НЕТ)
```bash
export PATH="$HOME/AppData/Local/hermes/hermes-agent/node_modules/.bin:$PATH"
agent-browser --help
agent-browser skills get core --full   # офиц. гайд, шаблоны, рефы
```

## Первый запуск
```bash
agent-browser install     # Chrome for Testing → C:\Users\<user>\.agent-browser\browsers\chrome-XXX
agent-browser doctor      # диагностика установки
agent-browser profiles    # список профилей Chrome пользователя (Default = его логины/куки)
```

## Ключевые флаги
| Флаг | Назначение |
|---|---|
| `--headed` | видимое окно (по умолчанию headless!) |
| `--profile <имя\|путь>` | `Default` = профиль Chrome пользователя; путь = изолированный профиль (`~/.agent-browser/profiles/<name>`) |
| `--session-name <имя>` | автосохранение кук/состояния |
| `--executable-path <путь>` | свой браузер (⚠ Windows-путь, НЕ MSYS `/c/...`) |
| `--auto-connect` / `--cdp <port>` | подключение к уже запущенному Chrome |

## Питфоллы (проверено на практике, все — реальные грабли)

1. **Демон кеширует флаги запуска.** Если сессия уже жива, новые `--headed/--profile/--executable-path` молча игнорируются:
   `⚠ --profile, --headed ignored: daemon already running. Use 'agent-browser close' first to restart with new options.`
   → ВСЕГДА `agent-browser close --all` перед запуском с другими флагами. И убивай старые фоновые процессы запуска (process kill) — иначе они держат демон с устаревшими параметрами.

2. **Google блокирует вход из automation-браузера.** Симптом: «Не удалось войти в аккаунт» / «может быть небезопасно» на accounts.google.com. Google детектит CDP/automation-флаги и режет OAuth-вход.
   → Обход: **прямой логин сайта** (email/пароль/телефон), НЕ кнопка «Continue with Google». X.com, например, automation пускает нормально.

3. **Зависший OAuth-редирект.** Сайт упорно кидает на accounts.google.com — в куках остался незавершённый OAuth-флоу. → Открывай `https://<site>/login` напрямую, а не `/home`.

4. **`--executable-path` с MSYS-путём** (`/c/Program Files/...`) не работает: «Системе не удается найти указанный путь». → Только Windows-путь: `C:\Program Files\...`.

5. **`--remote-debugging-port` с пользовательским профилем** на Windows (Chrome 151) не гарантирует открытия порта — в этой среде порт не поднялся. Надёжный путь — `agent-browser --headed --profile <путь>` (паттерн ниже).

## Паттерн «дать пользователю залогиниться» (headed + профиль)
```bash
agent-browser close --all
# убить старые фоновые процессы запуска (они держат демон)
agent-browser --headed --profile "$HOME/.agent-browser/profiles/xcom" open "https://<site>/login"
# пользователь логинится в видимом окне (только в этом окне!)
agent-browser get url; agent-browser snapshot -i   # проверка состояния
```
Логин сохраняется в профиле → следующие запуски с тем же `--profile` стартуют уже залогиненными.

## Проверка состояния
- `agent-browser get url` / `get title` / `snapshot -i` (интерактивные элементы)
- `agent-browser console` / `errors` — JS-ошибки страницы
- `agent-browser open <url>` — навигация в текущей сессии (флаги профиля уже не нужны)

## Реальный кейс: логин в X.com
Разбор полётов, рабочий путь и обходы — в `references/x-login.md`.
