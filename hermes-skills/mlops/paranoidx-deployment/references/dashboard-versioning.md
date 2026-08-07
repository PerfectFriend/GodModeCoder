# Dashboard Versioning Reference

## Version Badge Format

- Format: `A` + two-digit hex (00, 01, 02... FF)
- Incremented on **every** dashboard code change
- Located in header/sidebar of dashboard and login pages

## Implementation

### Dashboard (dashboard.html)
```html
<span class="version-badge" id="dashVersion">A06</span>
```

### Login Page (login.html)
```html
<div class="version-badge" id="dashVersion">A06</div>
```

## Version Increment Procedure

1. Edit dashboard HTML (`C:\ParanoidX-data\dashboard.html`)
2. Edit login page (`C:\ParanoidX-data\login.html`)
3. Find current version: `<span class="version-badge" id="dashVersion">A06</span>`
4. Increment hex: A06 → A07 → A08... A0F → A10 → A11...
5. Update both files to same version

## Version History

| Version | Date | Changes |
|---------|------|---------|
| A00 | Initial | First deployment |
| A01 | | Added wallet tab |
| A02 | | Added VPN tab |
| A03 | | Added treasury tab |
| A04 | | Added exchanger/radio |
| A05 | | Added marketplace/bridge |
| A06 | 2025-08-06 | HTTPS, BIP39 auth, 16 tabs verified |

## CSS Styling

```css
.version-badge {
  background: var(--gold);
  color: #0a0a1a;
  font-weight: 700;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: auto;
}
```

## Verification

Check version in rendered HTML:
```bash
curl -k https://127.0.0.1:8080/ | grep -o 'version-badge" id="dashVersion">A[0-9A-F]*'
```

Expected: `version-badge" id="dashVersion">A06`