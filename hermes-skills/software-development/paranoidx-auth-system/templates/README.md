# ParanoidX Auth System — Templates

## register.html

Two-tab registration page:
- **Register with Invite**: username, password, confirm, invite token (prefilled `UNIVERSAL-UNLIMITED`), optional mnemonic
- **Restore from Seed**: username, mnemonic (required), new password, confirm

Features:
- Real-time validation (username pattern, password length, mnemonic word count)
- Generated mnemonic displayed prominently with numbered words + warning banner
- Auto-redirect to dashboard on success
- CSRF-safe: uses HttpOnly cookie via `credentials: 'include'`

## login.html

Username/password login (no email):
- Username field (type=text, not email)
- Password field
- Enter key support
- Link to `/register.html`
- HttpOnly cookie `dashboard_token`
- Version badge in corner (A06)

Both templates use the Saint Mary Liberty Island dark theme with gold accents.