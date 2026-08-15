# Flutter Windows Build for ParanoidX/The-Isle/Royal-Isle

## Project Structure (from GitHub repos)

| Repo | App Dir | Platform Support |
|------|---------|-----------------|
| DarkPushkin/The-Isle | isle_app/ | Linux, Windows, macOS, Android, iOS, Web |
| DarkPushkin/Royal-Isle | royal_app/ | Linux, Windows, macOS, Android, iOS, Web |
| DarkPushkin/shared-libs | api_client/, models/, widgets/ | Pure Dart packages (local path deps) |

## Windows Build Requirements

### Prerequisites (install via windows-toolchain-install skill)
- **Flutter SDK** (stable channel, 3.x+)
- **Visual Studio 2022** with "Desktop development with C++" workload
- **CMake** (for Windows runner)
- **Ninja** (for Windows runner)

### Flutter Windows Setup
```bash
# From git-bash/MSYS
flutter config --enable-windows-desktop
flutter doctor -v  # Verify VS2022 + C++ workload detected
```

### Building The-Isle (Civilian App) for Windows
```bash
cd The-Isle/isle_app

# Get dependencies (needs pub.dev via Tor proxy - see below)
flutter pub get

# Build release
flutter build windows --release
# Output: build\windows\x64\runner\Release\isle_app.exe + DLLs + data\
```

### Building Royal-Isle (Admin App) for Windows
```bash
cd Royal-Isle/royal_app
flutter pub get
flutter build windows --release
# Output: build\windows\x64\runner\Release\royal_app.exe + DLLs + data\
```

### Shared Libs Dependency Resolution
Both apps reference `shared-libs` via local paths in pubspec.yaml:
```yaml
dependencies:
  models:
    path: ../../shared-libs/models
  api_client:
    path: ../../shared-libs/api_client
  widgets:
    path: ../../shared-libs/widgets
```

**Clone all 4 repos side-by-side:**
```
C:\Projects\
├── ParanoidX\          (Go server)
├── The-Isle\           (isle_app/)
├── Royal-Isle\         (royal_app/)
└── shared-libs\        (models/, api_client/, widgets/)
```

## Tor Proxy Issue on Windows
**Problem**: ParanoidX global proxy (`HTTP_PROXY=socks5://127.0.0.1:9050`) breaks `flutter pub get` and `flutter build`.

**Solution**: Unset proxy env vars before Flutter commands:
```bash
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy
flutter pub get
flutter build windows --release
```

**PowerShell equivalent:**
```powershell
$env:HTTP_PROXY = ""; $env:HTTPS_PROXY = ""; $env:http_proxy = ""; $env:https_proxy = ""; $env:ALL_PROXY = ""; $env:all_proxy = ""
flutter pub get
flutter build windows --release
```

## Windows-Specific Runtime Dependencies

### Tor (for SimpleX Chat over Tor)
- **Tor Expert Bundle for Windows**: https://www.torproject.org/download/tor/
- Extract `tor.exe` to `C:\Tools\tor\` or app bundle
- Run with custom `torrc` (SOCKS5 on 9050, hidden services)

### xray/V2Ray (for ParanoidX VPN)
- **xray-windows-64.zip**: https://github.com/XTLS/Xray-core/releases
- Extract `xray.exe` to `C:\Tools\xray\`
- Config: `xray -c config.json`

### SQLite (for api_client drift)
- Uses `sqlite3_flutter_libs` — bundles native sqlite3
- Works on Windows without extra install

## Distribution

### Standalone Executable Bundle
```
build\windows\x64\runner\Release\
├── isle_app.exe (or royal_app.exe)
├── flutter_windows.dll
├── *.dll (system + plugin)
├── data\
│   ├── flutter_assets\
│   ├── icudtl.dat
│   └── app.so (on Linux) / icudtl.dat
└── icons\
```

### Installer Options
1. **MSIX** (Windows Store / sideload) - modern, sandboxed
2. **Inno Setup** - classic installer, full control
3. **NSIS** - lightweight, scriptable
4. **Zip + portable** - just copy `Release` folder

### Code Signing (recommended)
```powershell
# SignTool from Windows SDK
signtool sign /f cert.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 isle_app.exe
```

## Known Issues / Pitfalls

| Issue | Fix |
|-------|-----|
| `dart:io` used in app → blocks web build | Web not supported; use native Windows |
| `file_picker` Windows plugin needs WinRT | Included in `file_picker` v8+ |
| `shared_preferences` Windows uses registry | Works out of box |
| Tor proxy breaks pub get | Unset proxy vars before Flutter commands |
| VS2022 not found by flutter doctor | Install "Desktop development with C++" workload |
| CMake/Ninja missing | `winget install --source winget Kitware.CMake Ninja-build.Ninja` |

## Build Script Template (PowerShell)

```powershell
# build-windows.ps1 - Run from C:\Projects\

# 1. Unset proxy
$env:HTTP_PROXY = ""; $env:HTTPS_PROXY = ""; $env:http_proxy = ""; $env:https_proxy = ""; $env:ALL_PROXY = ""; $env:all_proxy = ""

# 2. Build Go server
cd ParanoidX
$env:GOOS="windows"; $env:GOARCH="amd64"; $env:CGO_ENABLED="0"
go build -ldflags="-X main.buildVersion=win-01" -o ParanoidX.exe ./cmd/ParanoidX/

# 3. Build The-Isle
cd ..\The-Isle\isle_app
flutter pub get
flutter build windows --release

# 4. Build Royal-Isle
cd ..\..\Royal-Isle\royal_app
flutter pub get
flutter build windows --release

# 5. Copy outputs to dist
mkdir -Force dist
Copy-Item ParanoidX\ParanoidX.exe dist\
Copy-Item The-Isle\isle_app\build\windows\x64\runner\Release\* dist\The-Isle\ -Recurse
Copy-Item Royal-Isle\royal_app\build\windows\x64\runner\Release\* dist\Royal-Isle\ -Recurse

Write-Host "Build complete. Output in dist\" -ForegroundColor Green
```