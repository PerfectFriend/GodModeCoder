---
name: windows-toolchain-install
description: "Install dev toolchains on Windows without admin or winget."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [windows, toolchain, install, go, dart, rust, java, android-sdk, vscode, winget, msiexec]
    related_skills: [hermes-agent]
---

# Windows Dev Toolchain Install (no-admin / winget-fails path)

Use when installing Go, Dart, Rust, Java (JDK), Android SDK, Python, or VSCode on Windows — especially when winget is broken, slow, or admin rights are missing. Proven on Win10/11 + git-bash (MSYS), 2026-08.

## Decision order

1. **winget with `--source winget`** (see fix below) — quickest when it works.
2. **Direct zip install** for SDKs (Go, Dart, JDK) — no installer, no admin, most reliable.
3. **Standalone installers** (rustup-init.exe, VSCode user-setup, Python exe).
4. **`uv python install <ver>`** for Python — bypasses MSI entirely, takes seconds.

## winget fixes

- Error `0x8a15005e : The server certificate did not match` / "Failed when searching source: msstore" → pass `--source winget` explicitly:
  `winget install --exact --source winget --id GoLang.Go --silent --accept-package-agreements --accept-source-agreements --disable-interactivity`
- winget hangs on an MSI (msiexec alive, CPU≈0, no progress for many minutes) → kill it and install directly via zip. A stuck msiexec blocks ALL subsequent MSI-based installs with exit code **1618 "another installation is already in progress"**.

## msiexec zombie (error 1618) — fix

```powershell
Get-Process msiexec -ErrorAction SilentlyContinue   # zombie: empty Path/CommandLine
Stop-Process -Name msiexec -Force -ErrorAction SilentlyContinue
# if access denied, restart the installer service:
Stop-Service msiserver -Force; Restart-Service msiserver
```

## Direct zip installs (per tool)

```bash
# Go
curl -sL -o /tmp/go.zip https://go.dev/dl/go1.26.5.windows-amd64.zip
cd /c && unzip -q -o /tmp/go.zip            # → C:\go\bin\go.exe
# Dart
curl -sL -o /tmp/dartsdk.zip https://storage.googleapis.com/dart-archive/channels/stable/release/latest/sdk/dartsdk-windows-x64-release.zip
cd /c && unzip -q -o /tmp/dartsdk.zip       # → C:\dart-sdk\bin\dart.exe
# JDK (Temurin 21 LTS)
curl -sL -o /tmp/jdk21.zip "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse"
cd /c && unzip -q -o /tmp/jdk21.zip         # → C:\jdk-21.x+8 ; set JAVA_HOME
# Rust
curl -sL -o /tmp/rustup-init.exe https://win.rustup.rs/x86_64
/tmp/rustup-init.exe -y --default-toolchain stable --profile default   # → ~/.cargo/bin
# Python (fast, no MSI)
uv python install 3.12
# VSCode (user setup, not MSI)
curl -sL -o /tmp/vscode-setup.exe https://update.code.visualstudio.com/latest/win32-x64-user/stable
powershell -Command "Start-Process 'C:\Users\<u>\AppData\Local\Temp\vscode-setup.exe' -ArgumentList '/verysilent','/mergetasks=!runcode,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath' -Wait -PassThru"
```

## Android SDK (cmdline-tools route)

1. `curl -sL https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip` → extract → arrange so sdkmanager lives at `<SDK>/cmdline-tools/latest/bin/sdkmanager.bat` (move bin/lib/source.properties into `cmdline-tools/latest/`).
2. Accept licenses by writing hash files — git-bash `echo y | sdkmanager.bat --licenses` does NOT work:
   ```bash
   mkdir -p "$LOCALAPPDATA/Android/Sdk/licenses"
   printf '8933bad161af4178b1185d1a37fbf41ea5269c55\n24333f8a63b6825ea9c5514f83c2829b004d1fee\nd56f5187479451eabf01fb78af6dfcb131a6481e\n' > android-sdk-license
   printf '84831b9409646a918e30573bab4c9c91346d8abd\n' > android-sdk-preview-license
   ```
3. sdkmanager.bat does NOT see bash-exported JAVA_HOME — pass it inline:
   `JAVA_HOME="C:\\jdk-21.0.12+8" ./sdkmanager.bat "platform-tools" "platforms;android-34" "build-tools;34.0.0"`
4. Set ANDROID_HOME + ANDROID_SDK_ROOT + add `platform-tools` to PATH.

## PATH / env vars (persist for the user)

Bash `export` is session-only. Use PowerShell User scope so it survives reboots:

```powershell
[Environment]::SetEnvironmentVariable('JAVA_HOME','C:\jdk-21.0.12+8','User')
[Environment]::SetEnvironmentVariable('ANDROID_HOME','C:\Users\<u>\AppData\Local\Android\Sdk','User')
[Environment]::SetEnvironmentVariable('ANDROID_SDK_ROOT','C:\Users\<u>\AppData\Local\Android\Sdk','User')
[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User') + ';C:\go\bin;C:\dart-sdk\bin', 'User')
```
New terminals pick it up; the current shell needs `source ~/.bashrc` or a restart.

## Git-bash (MSYS) gotchas

- `/tmp` is `C:\Users\<u>\AppData\Local\Temp`, NOT `C:\tmp`. When passing paths to PowerShell Start-Process, use `cygpath -w /tmp/file` (or the real Windows path) — otherwise Start-Process fails with "cannot find the file".
- `taskkill //F //PID 1234` — MSYS mangles `//`; use single slashes: `taskkill /F /PID 1234`.
- `.bat` files don't inherit bash env vars — pass `VAR=value` inline before the .bat call.

## Verification

```bash
go version; dart --version; rustc --version; java -version; javac -version
code --version   # VSCode
ls "$LOCALAPPDATA/Android/Sdk/platform-tools/adb.exe"   # ADB
```

## Related ParanoidX Windows Port Resources

- `references/flutter-windows-build.md` — Flutter Windows build guide for ParanoidX/The-Isle/Royal-Isle apps (in windows-dev-environment skill).
- `references/paranoidx-go-windows-port.md` — Go server Windows port guide (in windows-dev-environment skill).
- `references/wsl2-hybrid-foundation.md` — WSL2 Hybrid deployment pattern: Go server in WSL2 + native Flutter apps on Windows (in windows-dev-environment skill).
