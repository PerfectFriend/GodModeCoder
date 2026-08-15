# PowerShell Encoding Issues on Non-English Windows

## Problem

On Russian/Chinese/other non-English Windows:
- PowerShell outputs in **cp866** (legacy) or **cp1251** (ANSI)
- Terminals/IDEs often read as **UTF-8**
- Result: Garbled text like `Р'РµСЂСЃРёСЏ` instead of `Версия`

## Root Cause

`[Console]::OutputEncoding` defaults to system OEM code page (cp866 for Russian).
`Write-Host` writes in that encoding.
Bash/terminal reads as UTF-8.

## Solution: ASCII-Only Scripts

**Rule**: All PowerShell scripts for cross-environment use must use **ASCII-only output**.

### Do:
```powershell
Write-Host "[OK] Task completed" -ForegroundColor Green
Write-Host "[WARN] Something unusual" -ForegroundColor Yellow
Write-Host "[ERR] Failed: $error" -ForegroundColor Red
Log "Phase 1: Starting..." -ForegroundColor Cyan
```

### Don't:
```powershell
Write-Host "✓ Завершено" -ForegroundColor Green      # Unicode + Cyrillic
Write-Host "⚠ Ошибка: $error" -ForegroundColor Yellow
Write-Host "=== Настройка завершена ===" -ForegroundColor Cyan
```

## If You Must Support Non-ASCII

Set encoding explicitly at script start:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'
```

But this only works if the **calling terminal** also uses UTF-8. Hermes/bash terminal may not.

## Best Practice

1. Write all scripts in **English ASCII**
2. Use `[OK]` `[WARN]` `[ERR]` `[INFO]` prefixes
3. Keep user-facing messages in separate localization files if needed
4. Test on target locale before deploying

## Quick Test

```powershell
# Run this to see your current output encoding
[Console]::OutputEncoding
# Should show UTF8 (code page 65001) for clean output
```

## Hermes Terminal Specific

Hermes runs bash which captures PowerShell output via pipes.
The bash terminal assumes UTF-8.
PowerShell on Russian Windows defaults to cp866.
**Result**: Always garbled unless ASCII-only or explicit UTF8 + terminal support.