# Site recipes: X поиск, GitHub UI, повторный логин через копию профиля

Проверено 2026-08-05 (сессия: поиск "graph engineering" на X, создание репо cableguard,
добавление SSH-ключа, переключение репо в private).

## Поиск в X (Twitter) через залогиненный браузер

Без API-ключа. Логин один раз в headed-браузере (email+пароль, НЕ через Google —
Google блокирует automation), дальше сессия живёт в профиле.

```python
# 1. Навигация на поиск (БЕЗ кавычек в запросе!):
url = 'https://x.com/search?q=' + urllib.request.quote(query) + '&src=typed_query&f=live'
#    f=live = свежие посты; без него = Top

# 2. Извлечение постов:
js = '''
(() => {
  const articles = Array.from(document.querySelectorAll('article'));
  return JSON.stringify(articles.slice(0, 15).map(a => ({
    text: a.innerText.slice(0, 300),
    time: (a.querySelector('time')||{}).getAttribute ? a.querySelector('time').getAttribute('datetime') : null,
    href: (a.querySelector('a[href*="/status/"]')||{}).href || null
  })));
})()
'''
```

Питфоллы:
- **Точная фраза в кавычках часто даёт 0 результатов** — ищи без кавычек
- После навигации sleep 8-10с, проверь `noResults` в body
- Для полного треда: `window.scrollBy(0, 3000)` несколько раз
- Видео-посты встречаются часто; текстовые статьи со схемами — `f=image` фильтр
  (медиа), либо открывать конкретный статус и читать innerText

## GitHub UI: создание репозитория

Страница `https://github.com/new`:
1. Имя: focus на `#repository-name-input` → `Input.insertText(name)`
2. Описание: label клик → focus `[id="_r_c_"]` → insertText
3. **Проверь радио Public** (по умолчанию выбрано) — иначе форма не отправится
4. Кнопка `Create repository` — если клик не сработал (ошибка "You can't perform
   that action at this time"), перезагрузи страницу и заполни заново — глюк формы
5. После создания URL → `https://github.com/<user>/<repo>` — проверь по нему

## GitHub UI: добавление SSH-ключа

Страница `https://github.com/settings/ssh/new`:
1. Title: focus `#ssh_key_title` → insertText
2. Key: focus `#ssh_key_key` → `Input.insertText(pubkey)` — **insertText, НЕ Runtime-setter**
   (setter давал "Key is invalid. You must supply a key in OpenSSH public key format")
3. Кнопка `Add SSH key` → проверь "successfully added the key"
4. Проверка: `ssh -T git@github.com` → "Hi <user>!"

## GitHub UI: репо public → private

Многошаговый диалог (НЕ простая кнопка):
1. `https://github.com/<user>/<repo>/settings`
2. Клик `#visibility_menu-button` (открывает action-menu)
3. Клик `[data-show-dialog-id="visibility-menu-dialog-private"]`
4. В диалоге: клик кнопку `I have read and understand these effects`
5. Клик финальную `Make this repository private`
6. Проверка: settings-страница → "This repository is currently private"

## GitHub UI: переименование репозитория (проверено 2026-08, cableguard → AISuperGuard)

1. `https://github.com/<user>/<repo>/settings`
2. Поле имени: `#rename-field` → focus → `Input.insertText(new_name)` (сначала select/Delete старое)
3. Кнопка `Rename` (текст ровно "Rename") — клик; страница редиректит на `/owner/new-name`
4. **Локальный repo**: `git remote set-url origin git@github.com:OWNER/new-name.git`
5. **Sweep URL-ов в файлах** (GitHub не переписывает твои скрипты!): `grep -rn "owner/old-name" --include="*.md" --include="*.sh" --include="*.ps1" --include="*.py" .` → `sed -i 's|owner/old-name|owner/new-name|g'` по README/install-скриптам
6. Проверка: `curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/OWNER/new-name/main/README.md` → 200
7. НЕ трогай внутренние идентификаторы, содержащие старое имя (device_id и т.п.) — ломает совместимость

## Повторный логин: копия профиля Chrome (когда --profile Default не пускает)

Chrome 151 отказывает remote debugging со стандартным user-data-dir:
```
DevTools remote debugging requires a non-default data directory
```
Решение — копия профиля:
```bash
SRC="$LOCALAPPDATA/Google/Chrome/User Data/Default"
DST="$HOME/.agent-browser/profiles/chrome-x"
mkdir -p "$DST/Network"
cp -r "$SRC/Network/Cookies"* "$DST/Network/"   # куки — в Network/ (новые Chrome)
cp -r "$SRC/Local Storage" "$SRC/Session Storage" "$SRC/Preferences" "$SRC/Login Data"* "$DST/"
# Для полной сессии (все куки) — скопировать весь Default (~385MB)
```
Запуск: `chrome.exe --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir="$DST" URL`

Проверка порта: `curl http://127.0.0.1:9222/json/version`; вкладки: `/json`.

## Общие питфоллы

- **agent-browser демон**: старые фоновые процессы игнорируют новые флаги запуска.
  Всегда: kill всех proc_* → `agent-browser close --all` → убить chrome.exe → один запуск.
- **Google OAuth из automation** = блок. Всегда нативный логин сайта.
- **Старые background-процессы** агента шлют спам-уведомления "completed normally" —
  это фоновые хвосты, не ошибки.
