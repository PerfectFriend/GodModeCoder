---
name: windows-dev-env-install
description: "Use when installing dev toolchains on Windows."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [windows, toolchain, install, winget, android-sdk, vscode, rust, go, dart, java]
---

# Windows Dev Environment Installation

Install a full developer toolchain (Go, Dart, Rust, JDK, Python, Android SDK, VSCode) on Windows reliably — including when winget breaks.

## Trigger

- User asks to install a dev environment ("установи полную среду разработчика", "install go dart rust java python vscode")
- winget fails or hangs
- Need Android SDK / JDK / toolchain without admin rights

## Key insight: skip MSI installers when possible

On Windows the **zip/portable install + PATH via registry** path is more reliable than winget/MSI installers, which frequently hang (see pitfalls). Verified working installs:

| Tool | Method | Path |
|---|---|---|
| Go | zip from go.dev/dl → unzip to `C:\go` | `C:\go\bin` |
| Dart | zip from storage.googleapis.com (dart-archive stable sdk) → `C:\dart-sdk` | `C:\dart-sdk\bin` |
| Rust | `rustup-init.exe -y --default-toolchain stable` | `%USERPROFILE%\.cargo\bin` |
| JDK | zip from api.adoptium.net (`/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse`) → `C:\jdk-21*` | `JAVA_HOME` + `\bin` |
| Python | **`uv python install 3.12`** (fastest, no MSI!) → `%APPDATA%\uv\python\cpython-3.12*\` | add to PATH |
| VSCode | user-setup exe `/verysilent /mergetasks=!runcode,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath` | `%LOCALAPPDATA%\Programs\Microsoft VS Code\bin` |

Python installer (.exe) also works: `python-3.12.x-amd64.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 TargetDir=...` — but ONLY if no stale msiexec is running (exit 1618 = "another installation in progress").

## Setting PATH / env vars (user scope, no admin)

```powershell
[Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\jdk-21.0.12+8', 'User')
[Environment]::SetEnvironmentVariable('ANDROID_HOME', "$env:LOCALAPPDATA\Android\Sdk", 'User')
[Environment]::SetEnvironmentVariable('ANDROID_SDK_ROOT', "$env:LOCALAPPDATA\Android\Sdk", 'User')
# PATH append:
$p = [Environment]::GetEnvironmentVariable('Path','User')
[Environment]::SetEnvironmentVariable('Path', "$p;C:\go\bin;C:\dart-sdk\bin;...", 'User')
```

Note: new terminals (or `source ~/.bashrc`) are needed for changes to take effect.

## Android SDK (manual, no Android Studio)

1. `mkdir -p "$LOCALAPPDATA/Android/Sdk"` 
2. Download `commandlinetools-win-*_latest.zip` from dl.google.com/android/repository/
3. **Layout requirement**: sdkmanager must live at `<sdk>\cmdline-tools\latest\bin\sdkmanager.bat` (unzip gives `cmdline-tools/bin` — move into `latest/` subdir, then move `bin`/`lib` up into `latest/`)
4. Accept licenses: `yes | sdkmanager.bat --licenses` needs JAVA_HOME visible to the .bat — set it **Windows-style inline**: `JAVA_HOME="C:\\jdk-21.0.12+8" ./sdkmanager.bat ...` (bash `export` alone does NOT reach .bat). Or pre-write license files (see below).
5. Install: `sdkmanager.bat "platform-tools" "platforms;android-34" "build-tools;34.0.0"`

License files (pre-write to `<sdk>\licenses\` to skip interactive prompts):
- `android-sdk-license`: `8933bad161af4178b1185d1a37fbf41ea5269c55` + `24333f8a63b6825ea9c5514f83c2829b004d1fee` + `d56f5187479451eabf01fb78af6dfcb131a6481e`
- `android-sdk-preview-license`: `84831b9409646a918e30573bab4c9c91346d8abd`
- `android-googletv-license`: `601085b94cd77f0b54ff86406957099ebe79c4d6`
- `android-sdk-arm-dbt-license`: `859f317696f67ef3d7f3a0ace7cbf5fd497f3564`

Note: network hiccups during sdkmanager downloads (e.g. "Build-Tools 35: dl.google.com" error) are transient — retry the single package.

## Auto-start on login without admin rights

`Register-ScheduledTask` fails with `HRESULT 0x80070005` (access denied) for non-admin users. Use the HKCU Run key instead:

```powershell
$runKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
New-ItemProperty -Path $runKey -Name 'HermesGateway' -Value '"C:\path\hermes.exe" gateway run' -PropertyType String -Force
```

**Double insurance (verified 2026-08):** pair the HKCU Run entry with a shortcut in the Startup folder — some AV/policies kill registry Run keys, the folder is bulletproof. WScript.Shell shortcut with args:

```powershell
$startup = [Environment]::GetFolderPath('Startup')
$lnk = Join-Path $startup 'Obsidian - Vault.lnk'
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($lnk)
$sc.TargetPath = 'C:\Users\tomas\AppData\Local\Programs\Obsidian\Obsidian.exe'
$sc.Arguments = '"vault://C:\Vault"'
$sc.Description = 'Obsidian: эволюционный граф + заметки'
$sc.Save()
```

This makes the app (e.g. Obsidian) start at login **independently of Hermes** — user wants it alive without the agent. Both mechanisms coexist safely (same command).

## Obsidian: headless vault provisioning (verified 2026-08)

winget `Obsidian.Obsidian` installs to `%LOCALAPPDATA%\Programs\Obsidian` (NOT Program Files). To point it at a custom vault (e.g. `C:\Vault`) without clicking the UI:

1. `mkdir -p /c/Vault && printf '# Welcome\n' > /c/Vault/Welcome.md`
2. Pre-write `%APPDATA%\obsidian\obsidian.json` (app creates it on first run; safe to write first):
   ```json
   { "vaults": { "<any-uuid>": { "path": "C:\\Vault", "ts": 1754419200000, "open": true } } }
   ```
3. Launch: `"$LOCALAPPDATA/Programs/Obsidian/Obsidian.exe" "vault://C:\Vault"` (background process), verify via `tasklist //FI "IMAGENAME eq Obsidian.exe"`.

## Databases and services (verified 2026-08)

- **PostgreSQL — EDB installer 403-blocks our IP.** get.enterprisedb.com returns 403 for wget/curl (even with browser UA), winget (`Download request status is not success 0x80190193 Forbidden`), and `Start-Process` of the exe. **Use Docker instead** — up in 1 min:
  ```bash
  docker run -d --name pg17 --restart unless-stopped \
    -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres \
    -p 5432:5432 -v pgdata:/var/lib/postgresql/data postgres:17-alpine
  ```
  Verify: `docker exec pg17 psql -U postgres -c "SELECT version();"`. Named volume survives restarts. `psql` client lives inside the container — no Windows install needed. Note: EDB's `pg-setup.exe` may also fail to launch from git-bash with `Permission denied` (needs `cmd //c start /wait` or `Start-Process -Verb RunAs`), but the 403 is the real blocker.
- **Redis via winget** (`Redis.Redis`) installs to `C:\Program Files\Redis`, auto-creates **Windows service "Redis" (Running)** — no manual service registration. Add `C:\Program Files\Redis` to PATH yourself; test `redis-cli ping` → PONG. Config: `redis.windows.conf`.
- **Gradle is NOT in winget** (no official package; searches return unrelated tools). Install official zip:
  ```bash
  wget -q https://services.gradle.org/distributions/gradle-9.1.0-bin.zip -O g.zip
  unzip -q g.zip -d /c/ && rm g.zip      # → C:\gradle-9.1.0
  # PATH += C:\gradle-9.1.0\bin  (gradle.bat)
  ```
- **GnuWin32 zip/make (winget GnuWin32.Zip/GnuWin32.Make)** install to `C:\Program Files (x86)\GnuWin32\bin` but are **NOT added to PATH** — append manually. Same for `wget` (use `JernejSimoncic.Wget`, not `GnuWin32.Wget` which no longer exists) and `jq` (`jqlang.jq`).
- **winget CLI links land in `%LOCALAPPDATA%\Microsoft\WinGet\Links\`** — visible only to NEW shells. To verify without restarting: `powershell -NoProfile -Command "$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User'); Get-Command jq,cmake,gh"`.
- **adb/sdkmanager may exist off-PATH**: `%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe` + `cmdline-tools\latest\bin\sdkmanager.bat` are valid even when `Get-Command adb` fails — just append the platform-tools dir to PATH.
- **MSYS path leak creates orphan `C:\c\Users\...` trees** — if an MSYS path like `/c/Users/tomas/...` is passed to a Windows-native tool (PowerShell, cmd, Start-Process), it's interpreted as `C:\c\Users\tomas\...` and a whole phantom directory tree gets created (observed: 40 MB orphan `C:\c\Users\tomas\.agent-browser\` profile). Fix: `cygpath -w` any path crossing into Windows tools, and when cleaning up, check `ls /c/c/` for orphans and `mv` their contents into `C:\Users\tomas\...` before `rm -rf /c/c`.

## Pitfalls (all hit in production)

1. **winget msstore source fails with `0x8a15005e: server certificate did not match`** → add `--source winget` to every install command. Plain `winget install --id X` tries msstore and dies even when the package is in the winget source.
2. **winget/MSI hangs forever** (spinner >2 min, `msiexec` at 0% CPU) → kill `msiexec`/`winget`; if a zombie msiexec survives `Stop-Process` (access denied), restart the service: `Stop-Service msiserver -Force; Restart-Service msiserver`. A stale msiexec blocks ALL subsequent MSI installs with exit 1618.
3. **Windows Installer service (msiserver)** may show running while msiexec zombie persists — the service restart is the reliable reset.
4. `python3` on git-bash may hit the Microsoft Store alias stub ("Python was not found") — use `python` or the uv-managed exe path directly.
5. MSYS `/tmp` ≠ `C:\tmp` — when passing paths to PowerShell/native tools use `cygpath -w` output.
6. Background winget installs via `bash script.sh` in one process are fine, but don't parallelize winget calls — the MSI mutex serializes them anyway.
7. VSCode user-setup exit code 0 with no install → rerun via `Start-Process -Wait -PassThru` and check `$p.ExitCode`; also the `!runcode` mergetask flag prevents it launching at the end of install.

## Verification

```bash
go version && dart --version && rustc --version && java -version && python --version && code --version
ls "$LOCALAPPDATA/Android/Sdk/platform-tools/adb.exe"
```

Or run the packaged one-shot checker: `bash scripts/verify-dev-env.sh` (prints a pass/fail table for the whole toolchain, exits non-zero on any miss).

## Related ParanoidX Windows Port Resources

- `references/flutter-windows-build.md` — Flutter Windows build guide for ParanoidX/The-Isle/Royal-Isle apps (in windows-dev-environment skill).
- `references/paranoidx-go-windows-port.md` — Go server Windows port guide (in windows-dev-environment skill).
