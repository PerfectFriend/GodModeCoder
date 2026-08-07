# GitHub-автоматизация через CDP (проверено 2026-08)

Полный флоу: создать публичный/приватный репозиторий, добавить SSH-ключ, сменить приватность — всё через CDP WebSocket на запущенном Chrome (см. SKILL.md, рецепт запуска с копией профиля).

## Предпосылки
- Chrome запущен с `--remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir=<копия профиля>`
- Пользователь уже залогинен в GitHub в этом окне (проверка: вкладка с `github.com/<user>` в списке `/json`)
- SSH-ключ сгенерирован: `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_github -C "desc" -N ""`

## 1. Создание репозитория (`github.com/new`)

```python
# заполнить имя (ОБЯЗАТЕЛЬНО сначала focus!)
send("Runtime.evaluate", {"expression": 'document.querySelector("#repository-name-input").focus(); true'})
send("Input.insertText", {"text": "repo-name"})

# описание: label кликом, потом insertText
send("Runtime.evaluate", {"expression": '''
  (() => { const d = document.querySelector('[id="_r_c_"]');
           const l = document.querySelector('label[for="_r_c_"]');
           if (l) l.click(); else d.focus(); return "ok"; })()
'''})
send("Input.insertText", {"text": "Description text"})

# Private radio (если нужно): найти radio по /private/i и click()
# кнопка: find b => /create repository/i.test(b.innerText); btn.click()
```

**Питфолл (влетел в бою):** `Input.insertText` пишет в ЭЛЕМЕНТ С ФОКУСОМ. Без явного `focus()`/`click()` перед каждой вставкой значение уходит в соседнее поле (описание влипло в имя репозитория → «You can't perform that action at this time»).

**Транзиентная ошибка:** «You can't perform that action at this time» может появиться, если кликнуть Create до полного заполнения. Лечение: перезагрузить `/new`, заполнить заново, ждать 1с после каждого поля, потом кликать. Срабатывает со 2-й попытки.

## 2. Добавление SSH-ключа (`github.com/settings/ssh/new`)

```python
pubkey = open("C:/Users/<user>/.ssh/id_ed25519_github.pub").read().strip()

# Title
send("Runtime.evaluate", {"expression": 'document.querySelector("#ssh_key_title").focus(); document.querySelector("#ssh_key_title").select(); true'})
send("Input.insertText", {"text": "cableguard-deploy"})

# Key — ТОЛЬКО Input.insertText (значение с пробелами и +)
send("Runtime.evaluate", {"expression": 'document.querySelector("#ssh_key_key").focus(); true'})
send("Input.insertText", {"text": pubkey})

# Add SSH key: find b => /add ssh key/i.test(b.innerText); click()
# проверка: редирект на /settings/keys + «You have successfully added the key '...'»
```

**Питфолл:** JS-setter с `json.dumps(key)` в строку JS-выражения вставляет артефакты экранирования (`\"ssh-ed25519 ...`), GitHub отвечает «Key is invalid. You must supply a key in OpenSSH public key format». Только `Input.insertText`.

## 3. Смена приватности (`/settings` → Danger Zone)

Кнопки НЕ в обычном DOM (action-menu/popovertarget). Цепочка:

```python
# 1. меню
document.querySelector("#visibility_menu-button").click()
# 2. пункт Private
document.querySelector('[data-show-dialog-id="visibility-menu-dialog-private"]').click()
# 3. первый шаг подтверждения
find b => /I have read and understand these effects/i
# 4. финальная кнопка
find b => b.innerText.trim() === "Make this repository private"
```

Проверка: в `/settings` текст `This repository is currently private.` (или public). Снаружи: `curl -s https://api.github.com/repos/<user>/<repo>` → `"private": true` (для приватных без токена вернёт null — проверять в браузере).

## 4. Пуш

```bash
git init && git branch -M main
git config user.name "<User>" && git config user.email "<user>@users.noreply.github.com"
cat > ~/.ssh/config <<EOF
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github
  IdentitiesOnly yes
EOF
git remote add origin git@github.com:<User>/<repo>.git
git push -u origin main
```

Проверка доступа: `ssh -T git@github.com` → `Hi <User>! You've successfully authenticated`.
