---
name: windows-dev-env-setup
description: "Install dev toolchains on Windows (Go, Dart, Rust, JDK)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [windows, winget, dev-environment, install, toolchain, sdk]
---

# Windows Dev Environment Setup

Reliable path to install programming toolchains/SDKs on Windows from a git-bash (MSYS) terminal. winget is **not** the default path — it has two failure modes that waste hours (below). Prefer direct zip/self-contained installers.

## When to use
- Installing Go, Dart, Rust, Java (JDK), Python, VSCode, Android SDK on a fresh Windows machine.
- winget errors: msstore cert failure, hangs at spinner, `0x8a15005e`, or MSI installs failing with exit code 1618.

## Pitfalls (learned the hard way)

1. **winget msstore source fails with cert error `0x8a15005e`** → every install then fails "The following packages were found among the working sources. Please specify one of them using --source". Fix: add `--source winget` to EVERY winget install: `winget install --exact --source winget --id GoLang.Go --silent --accept-package-agreements --accept-source-agreements --disable-interactivity`.

2. **Hung `msiexec` zombie blocks ALL MSI installs** (error 1618 "another installation is already in progress"). Symptom: msiexec PID exists with 0 CPU, `taskkill`/`Stop-Process` say access denied. Fix: restart the Windows Installer service: `Stop-Service msiserver -Force; Restart-Service msiserver`. If it survives, stop using MSI entirely and switch to zip installs (below) — faster and no admin needed.

3. **git-bash `/tmp` is NOT `C:\tmp`** — when passing paths to PowerShell `Start-Process`, resolve with `cygpath -w /tmp/file` first, or Start-Process fails with "cannot find path".

4. **MSI user installs can silently no-op**: `python.exe /quiet` with no `TargetDir` returned exit 0 but installed nothing. Use `uv python install <ver>` for Python instead — 6 seconds, no MSI, no admin.

5. **New PATH only applies to new shells** — after `[Environment]::SetEnvironmentVariable(..., 'User')`, tell the user to open a new terminal.

## Reliable install commands (zip / self-contained)

| Tool | Command | Result |
|---|---|---|
| Go | `curl -sL -o /tmp/go.zip https://go.dev/dl/go1.26.5.windows-amd64.zip && cd /c && unzip -q -o /tmp/go.zip` | `C:\go\bin` |
| Dart | `curl -sL -o /tmp/dartsdk.zip https://storage.googleapis.com/dart-archive/channels/stable/release/latest/sdk/dartsdk-windows-x64-release.zip && cd /c && unzip -q -o /tmp/dartsdk.zip` | `C:\dart-sdk\bin` |
| JDK 21 | `curl -sL -o /tmp/jdk21.zip "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse" && cd /c && unzip -q -o /tmp/jdk21.zip` | `C:\jdk-21.x\bin` |
| Rust | `curl -sL -o /tmp/rustup-init.exe https://win.rustup.rs/x86_64 && /tmp/rustup-init.exe -y --default-toolchain stable --profile default` | `~\.cargo\bin` |
| Python | `uv python install 3.12` (uv already present) | uv-managed, add exe dir to PATH |
| VSCode | `curl -sL -o /tmp/vscode-setup.exe "https://update.code.visualstudio.com/latest/win32-x64-user/stable"` then PowerShell `Start-Process ... -ArgumentList '/verysilent','/mergetasks=!runcode,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath' -Wait` | `%LOCALAPPDATA%\Programs\Microsoft VS Code\bin` |

## Android SDK (no winget package for full SDK)

1. `mkdir -p "$LOCALAPPDATA/Android/Sdk" && cd $_` — download `commandlinetools-win-*_latest.zip` from `https://dl.google.com/android/repository/`, unzip, then arrange as `cmdline-tools/latest/` (unzip puts contents in `cmdline-tools/` root; move bin/lib/etc into `cmdline-tools/latest/`).
2. `sdkmanager.bat --licenses` needs JAVA_HOME — bash env vars do NOT reach .bat files. Prefix on the same shell line: `JAVA_HOME="C:\\jdk-21.0.12+8" ./sdkmanager.bat "platform-tools" "platforms;android-34" "build-tools;34.0.0"`.
3. `echo y |` piping to accept licenses often reports "7 licenses not accepted" — write license hash files directly into `Sdk/licenses/` (`android-sdk-license`, `android-sdk-preview-license`, `android-googletv-license`, `android-sdk-arm-dbt-license`; hashes in references/windows-toolchain-commands.md).

## Env vars (User scope, persists)

```powershell
[Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\jdk-21.0.12+8', 'User')
[Environment]::SetEnvironmentVariable('ANDROID_HOME', 'C:\Users\<user>\AppData\Local\Android\Sdk', 'User')
[Environment]::SetEnvironmentVariable('ANDROID_SDK_ROOT', $env:ANDROID_HOME, 'User')
[Environment]::SetEnvironmentVariable('Path', $old + ';C:\go\bin;C:\dart-sdk\bin;C:\jdk-21.0.12+8\bin;...', 'User')
```

## Verification
After install: `go version`, `dart --version`, `rustc --version`, `java -version`, `uv python list`, `code --version` — run in a NEW shell. Android: `adb.exe` exists under `Sdk/platform-tools/`.

## Auto-start without admin
`Register-ScheduledTask` and `schtasks /Create` fail with access denied (0x80070005) for normal users. Use the HKCU Run key instead:
```powershell
New-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'MyApp' -Value '"C:\path\app.exe" args' -PropertyType String -Force
```

See `references/windows-toolchain-commands.md` for the full command transcript incl. Android license hashes.

## Support files

- `references/windows-toolchain-commands.md` — full command transcript incl. Android license hashes.
- `references/flutter-windows-build.md` — Flutter Windows build guide for ParanoidX/The-Isle/Royal-Isle apps (in windows-dev-environment skill).
- `references/paranoidx-go-windows-port.md` — Go server Windows port guide (in windows-dev-environment skill).
