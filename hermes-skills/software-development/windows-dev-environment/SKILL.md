---
name: windows-dev-environment
description: "Set up Windows dev toolchains: Go, Dart, Rust, Java, Python."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Windows, DevEnvironment, Toolchain, Install, winget, AndroidSDK]
---

# Windows Dev Environment Setup

Install full developer toolchains on Windows (host shell is git-bash/MSYS; `terminal` runs bash, NOT PowerShell/cmd). Covers: Go, Dart, Rust, Java JDK, Python, VSCode, Android SDK, plus env-var wiring.

## Trigger

User asks to set up / install a dev environment on Windows: "установи полную среду разработчика", "install go dart rust java", "setup android sdk", "install vscode", etc.

## Core rules (learned the hard way)

1. **winget is unreliable on this class of machine**: msstore source fails with certificate error `0x8a15005e` ("server certificate did not match"). Fix: always pass `--source winget` explicitly (`winget install --exact --source winget --id X --silent --accept-package-agreements --accept-source-agreements`).
2. **A zombie `msiexec` process locks ALL MSI installs** — new installs fail instantly with exit code **1618** ("another installation is already in progress"), even hours later. The zombie shows in `Get-Process msiexec` with empty CommandLine/CPU and cannot be killed by `Stop-Process` (access denied). Fix: restart the Windows Installer service: `Stop-Service msiserver -Force; Restart-Service msiserver`.
3. **Zip installs are the most reliable path** on Windows — no installer, no MSI, no admin: download the zip, `unzip -q` into `C:\`, add to PATH. Go, Dart, and Temurin JDK all ship official zips.
4. **Python: use `uv python install 3.12`** — uv is preinstalled on this host, installs a full CPython in ~6s with no MSI (the python.org exe installer hits the 1618 lock). `python` (3.11 via uv) already exists; add the 3.12 dir to PATH.
5. **VSCode**: user-setup exe (`update.code.visualstudio.com/latest/win32-x64-user/stable`), run with `/verysilent /mergetasks=!runcode,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath`. Installs to `%LOCALAPPDATA%\Programs\Microsoft VS Code\`.
6. **Android SDK**: winget only has platform-tools; full SDK needs cmdline-tools zip from `dl.google.com/android/repository/commandlinetools-win-<ver>_latest.zip`. Structure MUST be `Sdk\cmdline-tools\latest\` (the zip unpacks to `cmdline-tools\` — move contents into `cmdline-tools\latest\`). Licenses are plain hash files in `Sdk\licenses\` (see references file). `sdkmanager.bat` needs `JAVA_HOME` set **inside cmd**, bash `export` does NOT propagate to .bat — pass inline: `JAVA_HOME="C:\\jdk-21..." ./sdkmanager.bat ...`.
7. **PATH/JAVA_HOME**: set user-scope env vars via PowerShell: `[Environment]::SetEnvironmentVariable('JAVA_HOME', $val, 'User')`. Takes effect only in NEW shells — current session needs manual export.
8. **MSYS path gotchas**: git-bash `/tmp` maps to `C:\Users\<user>\AppData\Local\Temp` (not `C:\tmp`) — resolve with `cygpath -w /tmp/x` before handing paths to PowerShell. `taskkill //F //PID` in bash (double slashes); single-slash `taskkill /F` is parsed as a path. `python3` is missing on this host — use `python`.

## Steps

1. Inventory what's installed: `go version`, `dart --version`, `rustc --version`, `java -version`, `python --version`, `code --version`, check `$ANDROID_HOME`.
2. For each missing tool, prefer zip install (rule 3), then `uv python install` for Python, then winget `--source winget` as last resort. Exact verified URLs + commands: `references/install-recipes.md`.
3. Wire env vars (rule 7), verify everything in a NEW shell.

## Pitfalls

- **Don't parallelize winget installs** — they serialize on a mutex and can hang mid-install (Go MSI sat at 0% CPU for 12+ min). Prefer zip installs over winget entirely.
- **Don't trust "EXIT=0" from `./installer.exe /quiet | tail` in bash** — the pipe masks the real exit code. Use PowerShell `Start-Process -Wait -PassThru; $p.ExitCode`, and check the target dir exists afterward.
- **Android SDK license files**: running `yes | sdkmanager.bat --licenses` doesn't work through the .bat. Write the hash files directly (list in references).
- **Build-tools download can fail transiently** ("An error occurred while preparing SDK package ... dl.google.com") — just re-run sdkmanager for that package.
- **Deprecated env vars**: Hermes warns about `TERMINAL_CWD` in `.env` — harmless, ignore.
- **New PATH only applies to new terminals** — tell the user, don't re-verify in the old shell and report failure.
9. **WSL2 install requires Admin** — `wsl --install` and `dism.exe` need elevated PowerShell. Cannot be done from non-admin bash/terminal.
10. **PowerShell from bash encoding issues** — Calling `powershell.exe` or `.ps1` scripts from git-bash/MSYS produces garbled UTF-16 output. Always run PowerShell scripts from a native PowerShell terminal (Admin or User), not from bash.
11. **Flutter pub get breaks with Tor proxy** — Global `HTTP_PROXY=socks5://127.0.0.1:9050` blocks pub.dev. Unset all proxy vars before Flutter commands (see templates).
12. **Ubuntu first-run interactive setup** — Fresh Ubuntu 24.04 install requires manual username/password creation via GUI launch. Root is the only user until this completes. Scripts running as root see `$HOME=/root`, not the intended user's home.
13. **RunOnce auto-resume limitation** — HKCU RunOnce only triggers on interactive user logon (Explorer shell), NOT when opening Admin PowerShell via Win+X. User must manually re-run the setup script after each reboot to continue.
14. **PowerShell variable escaping for bash** — In PowerShell double-quoted strings, `$HOME` expands to Windows profile path. Escape with backtick: `` `$HOME `` so bash receives literal `$HOME` and expands to `/home/user`.

## Support files

- `references/install-recipes.md` — verified download URLs, exact commands, Android SDK license hashes, per-tool verification.
- `references/flutter-windows-build.md` — Flutter Windows build guide for ParanoidX/The-Isle/Royal-Isle apps, including Tor proxy workaround, xray/Tor runtime deps, and build script template.
- `references/paranoidx-go-windows-port.md` — Go server Windows port guide: required code changes (path abstraction, signal handling, bash→Go replacements), build commands, runtime dependencies, service installation.
- `references/wsl2-hybrid-foundation.md` — WSL2 Hybrid deployment pattern for ParanoidX: Go server in WSL2 + native Flutter apps on Windows + shared bind mount + Docker in WSL2.
- `references/wsl2-hybrid-troubleshooting.md` — Common issues and fixes: encoding problems, first-run interactive setup, RunOnce auto-resume, admin requirements.
- `templates/setup-wsl2-hybrid.ps1` — Full WSL2 + Ubuntu 24.04 setup, repo cloning, Go build (run as **Admin**).
- `templates/build-windows-flutter.ps1` — Build Flutter apps (The-Isle, Royal-Isle) + Go cross-compile for Windows (run as User).
- `templates/launch-hybrid.ps1` — Launch full stack: Docker (WSL2) + Go server (WSL2) + Flutter apps (native Windows).
