# Windows toolchain install — full command transcript & Android license hashes

## Android SDK license hashes (write into `<Sdk>/licenses/`)

`echo y | sdkmanager.bat --licenses` frequently still reports "N licenses not accepted".
The robust fix: create the license files directly with the known SHA-256 hash lines.

```bash
mkdir -p "$LOCALAPPDATA/Android/Sdk/licenses"
cd "$LOCALAPPDATA/Android/Sdk/licenses"
printf '8933bad161af4178b1185d1a37fbf41ea5269c55\n24333f8a63b6825ea9c5514f83c2829b004d1fee\nd56f5187479451eabf01fb78af6dfcb131a6481e\n' > android-sdk-license
printf '84831b9409646a918e30573bab4c9c91346d8abd\n' > android-sdk-preview-license
printf '601085b94cd77f0b54ff86406957099ebe79c4d6\n' > android-googletv-license
printf '859f317696f67ef3d7f3a0ace7cbf5fd497f3564\n' > android-sdk-arm-dbt-license
```

## SDK packages that worked on a 19.8 GB-RAM machine
```bash
JAVA_HOME="C:\\jdk-21.0.12+8" ./sdkmanager.bat \
  "platform-tools" "platforms;android-34" "build-tools;34.0.0" \
  "platforms;android-35" "build-tools;35.0.0"
```
- Build-tools 35.0.0 can fail once with "An error occurred while preparing SDK package ... dl.google.com" — just re-run; it resumes.
- `platform-tools` downloads last sometimes; re-run `./sdkmanager.bat "platform-tools"` alone if `adb.exe` is missing.

## VSCode user-setup flags that worked
```powershell
Start-Process 'C:\Users\<user>\AppData\Local\Temp\vscode-setup.exe' `
  -ArgumentList '/verysilent','/mergetasks=!runcode,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath' `
  -Wait -PassThru
```
- `!runcode` prevents it from launching VSCode after install.
- Installs to `%LOCALAPPDATA%\Programs\Microsoft VS Code\bin` (user scope, no admin).

## winget source selection (msstore cert failure)
```bash
winget install --exact --source winget --id <PACKAGE_ID> --silent \
  --accept-package-agreements --accept-source-agreements --disable-interactivity
```
Always add `--source winget` — without it, winget tries msstore and dies with `0x8a15005e: The server certificate did not match`.

## Killing a hung msiexec that survives taskkill
```powershell
Stop-Service msiserver -Force
Start-Sleep 2
Restart-Service msiserver
```
If `Stop-Process -Name msiexec -Force` fails with access denied, this service restart is the way. After that, prefer zip installs for anything large (Go/Dart/JDK) — they bypass MSI entirely and never need admin.

## git-bash /tmp → Windows path
`cygpath -w /tmp/file` → `C:\Users\<user>\AppData\Local\Temp\file`. Use this when calling `Start-Process -FilePath` from bash-launched PowerShell.

## Python via uv (no MSI, no admin)
```bash
uv python install 3.12
uv python list   # shows cpython-3.12.x-windows-x86_64-none path
```
Add the versioned dir to User PATH via PowerShell SetEnvironmentVariable if `python` should resolve.

## Scheduled-task alternative without admin
`schtasks /Create` and `Register-ScheduledTask` return 0x80070005 (access denied) for non-admin users on Windows 10/11. The HKCU Run key is the no-admin auto-start:
```powershell
New-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' `
  -Name 'AppName' -Value '"C:\path\to\app.exe" args' -PropertyType String -Force
```
