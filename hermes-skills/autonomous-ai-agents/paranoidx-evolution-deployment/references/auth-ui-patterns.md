# Production-Ready Login/Register/Restore UI Patterns

## Overview
All auth forms in `C:\ParanoidX-data\` are **functional products** — not simulations. They make real API calls, handle loading states, display errors, preserve user input, and redirect on success.

## Common Patterns (Applied to All Forms)

### Eye Toggle (Password Visibility)
**Position: Far right of input** — this is the standard UX pattern users expect.

```html
<div class="pw-wrap">
  <input type="password" id="password" name="password" ...>
  <button type="button" class="pw-toggle" data-target="password" aria-label="Show password" tabindex="-1">👁️</button>
</div>
```

```css
.pw-wrap { position:relative; width:100%; }
.pw-wrap input { width:100%; padding-right:44px; }
.pw-wrap .pw-toggle { 
  position:absolute; right:10px; top:50%; transform:translateY(-50%); 
  background:none; border:none; color:var(--muted); cursor:pointer; font-size:16px;
  padding:4px; line-height:1; display:flex; align-items:center; justify-content:center;
  width:32px; height:32px; border-radius:6px; tabindex:-1;
}
.pw-wrap .pw-toggle:hover { color:var(--text); background:var(--bg); }
.pw-wrap .pw-toggle:focus { outline:none; }
```

**Key details:**
- `tabindex="-1"` on toggle button prevents focus stealing during Tab navigation
- `data-target` attribute links toggle to input ID (no inline `onclick`)
- Delegated event handler on document: `document.addEventListener('click', e => { ... e.target.closest('.pw-toggle') ... })`
- Toggles between `👁️` (show) and `🙈` (hide), updates `aria-label`

### Tab Switching (Register Page)
Two tabs: "Register with Invite" + "Restore from Seed"

```html
<div class="tabs" role="tablist" aria-label="Registration mode">
  <div class="tab active" data-tab="register" role="tab" aria-selected="true" tabindex="0" id="tab-register">Register with Invite</div>
  <div class="tab" data-tab="restore" role="tab" aria-selected="false" tabindex="-1" id="tab-restore">Restore from Seed</div>
</div>

<div class="panel active" id="panel-register" role="tabpanel" aria-labelledby="tab-register">...</div>
<div class="panel" id="panel-restore" role="tabpanel" aria-labelledby="tab-restore" hidden>...</div>
```

```javascript
function activateTab(tabName) {
  tabs.forEach(t => {
    const isActive = t.dataset.tab === tabName;
    t.classList.toggle('active', isActive);
    t.setAttribute('aria-selected', isActive);
    t.tabIndex = isActive ? 0 : -1;
  });
  panels.forEach(p => {
    const isActive = p.id === 'panel-' + tabName;
    p.classList.toggle('active', isActive);
    p.hidden = !isActive;
  });
  clearMsg();
}

tabs.forEach(tab => {
  tab.addEventListener('click', () => activateTab(tab.dataset.tab));
  tab.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activateTab(tab.dataset.tab); }
    if (e.key === 'ArrowRight') { e.preventDefault(); tabs[1].focus(); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); tabs[0].focus(); }
  });
});
```

**Key details:**
- No focus stealing — `tabIndex` managed programmatically
- Keyboard accessible: ArrowLeft/Right, Enter, Space
- ARIA roles: `tablist`, `tab`, `tabpanel`, `aria-selected`, `aria-labelledby`
- `hidden` attribute on inactive panels (better than `display:none` for accessibility)

### Form Submission — No Clearing on Error
**Critical UX rule:** Never clear user input on validation error. Only show error message.

```javascript
document.getElementById('form-register').addEventListener('submit', async function(e) {
  e.preventDefault();
  clearMsg();
  
  // Validation - show inline error, RETURN early, form stays filled
  if (!invite || !username || !pwd) { showMsg('All fields required', true); return; }
  if (pwd !== cpwd) { showMsg('Passwords do not match', true); return; }
  
  // Loading state
  var submitBtn = document.getElementById('btn-register');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Creating...';
  
  try {
    // Real API call
    var res = await fetch('/api/auth/register-with-invite', {...});
    var data = await res.json();
    
    if (res.ok && data.status === 'created') {
      showMsg('Account created! ...', false);
      setTimeout(() => window.location.href = '/', 3000);
    } else {
      showMsg(data.error || ('Error: ' + res.status), true);
    }
  } catch(err) { showMsg(err.message, true); }
  finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Create Account';
  }
});
```

### Enter Key Support
```javascript
document.getElementById('password').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') submitLogin();
});
document.getElementById('username').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') submitLogin();
});
```

### Credentials Handling
All fetch calls use `credentials: 'include'` for cookie-based auth:
```javascript
fetch('/api/auth/register-with-invite', {
  method: 'POST', credentials: 'include',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(body)
});
```

## Login Page (`/login.html`)
- Eye toggle on password field
- Tab navigation only between username/password fields (toggle has `tabindex="-1"`)
- Submit button disables during request, shows "Signing in..."
- Enter key on both fields triggers submit
- Links to Register + Restore from seed
- POST `/login` → sets `dashboard_token` cookie → redirects to `/`

## Register Page (`/register.html`)
- Two working tabs with keyboard navigation
- Eye toggles on all 4 password fields (register pwd, confirm, restore pwd, confirm)
- No form clearing on error — user input preserved
- Password mismatch → inline error, form stays filled
- Submit buttons disable during request: "Creating..." / "Restoring..."
- Real API calls to `/api/auth/register-with-invite` and `/api/auth/restore`
- Success: shows generated mnemonic with numbered words + warning banner, redirects to dashboard
- Restore tab: complete form with username, mnemonic (required), new password, confirm

## Restore Page (Tab in Register)
Complete BIP39 recovery flow:
- Username + 12/24 word mnemonic + new password + confirm
- Calls `POST /api/auth/restore` with `{username, mnemonic, password}`
- On success: logs in and redirects to dashboard

## CSS Variables (Consistent Dark Theme)
```css
:root {
  --bg:#0a0a1a; --bg2:#0d0d22; --panel:#14142e; --card:#1a1a34;
  --border:#2a2a50; --gold:#ffd700; --green:#4ade80; --red:#f87171;
  --blue:#60a5fa; --text:#e0e0ee; --muted:#8a8aa5;
  --disabled:#3a3a5a; --disabled-text:#5a5a7a;
}
```

## Focus Styles
```css
input:focus, textarea:focus { 
  outline:none; border-color:var(--blue); box-shadow:0 0 0 2px rgba(96,165,250,.2); 
}
input:disabled, textarea:disabled, button:disabled {
  background:var(--disabled); color:var(--disabled-text); cursor:not-allowed; border-color:var(--disabled);
}
```

## Pitfalls Avoided
1. **No dropdown for invite tokens** — plain text input (user mandate)
2. **No form clearing on error** — preserve user input
3. **Eye toggle at far right** — standard position, not left/middle
4. **Toggle has `tabindex="-1"`** — prevents focus stealing during Tab navigation
5. **Delegated event handlers** — no inline `onclick`, single handler on document
6. **ARIA accessibility** — roles, labels, keyboard navigation
7. **Loading states** — buttons disable, show spinner/text
8. **Real API calls** — no simulations, proper error handling
9. **HTTPS with self-signed certs** — `curl -k` for testing, browser trusts via Windows cert store
10. **Version badge** — displayed on all auth pages (A38 current)