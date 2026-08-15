<# 
.SYNOPSIS
    Cathedral Code Machine - Quick Reference Card
.DESCRIPTION
    One-page reference for God Mode Coder Cathedral on Windows
.NOTES
    Run in new terminal after Cathedral setup
#>

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  🏛️ CATHEDRAL CODE MACHINE - QUICK REF" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "--- VERIFICATION (run in NEW terminal) ---" -ForegroundColor Yellow
Write-Host "  cathedral-verify.sh          # Full system check"
Write-Host "  rustc --version && cargo --version"
Write-Host "  java -version"
Write-Host "  go version"
Write-Host "  dart --version"
Write-Host "  /c/gradle-9.1.0/bin/gradle --version"
Write-Host "  flutter --version"
Write-Host "  kotlinc -version             # via kotlinc.bat wrapper"
Write-Host "  mvn --version"
Write-Host "  clang --version"
Write-Host "  protoc --version"
Write-Host "  adb version"
Write-Host ""

Write-Host "--- ENV VARS (permanent, HKCU) ---" -ForegroundColor Yellow
$vars = @('JAVA_HOME','ANDROID_HOME','ANDROID_SDK_ROOT','GRADLE_HOME','FLUTTER_HOME','KOTLIN_HOME','MAVEN_HOME','LLVM_HOME','PROTOC_HOME','ANDROID_STUDIO_HOME')
foreach ($v in $vars) {
    $val = [Environment]::GetEnvironmentVariable($v, 'User')
    Write-Host "  $v = $val"
}

Write-Host ""
Write-Host "--- PROJECT INIT ---" -ForegroundColor Yellow
Write-Host "  bash cathedral-init.sh my-app --stack=flutter"
Write-Host "  bash cathedral-init.sh my-service --stack=rust"
Write-Host "  bash cathedral-init.sh my-kotlin --stack=kotlin"
Write-Host "  bash cathedral-init.sh my-go --stack=go"
Write-Host "  bash cathedral-init.sh my-cpp --stack=cpp"
Write-Host "  bash cathedral-init.sh my-monorepo --stack=full"

Write-Host ""
Write-Host "--- DAILY DEV LOOP ---" -ForegroundColor Yellow
Write-Host "  # Rust"
Write-Host "  cargo watch -x test          # Auto-test on save"
Write-Host "  cargo clippy -- -D warnings  # Strict lint"
Write-Host "  cargo fmt --check            # Format check"
Write-Host ""
Write-Host "  # Flutter"
Write-Host "  flutter analyze              # Static analysis"
Write-Host "  flutter test                 # Unit/widget tests"
Write-Host "  flutter run -d chrome        # Hot reload web"
Write-Host "  flutter build apk --release  # Android release"
Write-Host ""
Write-Host "  # Kotlin/Gradle"
Write-Host "  ./gradlew detekt ktlintCheck test"
Write-Host "  ./gradlew :app:installDebug  # Android debug"
Write-Host ""
Write-Host "  # Go"
Write-Host "  go vet ./... && go test ./..."
Write-Host "  gofmt -l .                   # Format check"
Write-Host ""
Write-Host "  # C++ (MSVC)"
Write-Host "  cmake -B build -DCMAKE_BUILD_TYPE=Release"
Write-Host "  cmake --build build --config Release"
Write-Host "  ctest --test-dir build"
Write-Host ""

Write-Host "--- QUALITY GATES (pre-commit) ---" -ForegroundColor Yellow
Write-Host "  ./cathedral-check.sh         # Runs all stack checks"

Write-Host ""
Write-Host "--- RELEASE ---" -ForegroundColor Yellow
Write-Host "  git tag v1.0.0 && git push origin v1.0.0"
Write-Host "  # → GitHub Actions matrix build → all artifacts"

Write-Host ""
Write-Host "--- DEBUGGING ---" -ForegroundColor Yellow
Write-Host "  # Rust: rust-gdb / rust-lldb / VS Code"
Write-Host "  # Kotlin: IntelliJ / VS Code debugger"
Write-Host "  # Flutter: flutter devtools / VS Code"
Write-Host "  # C++: Visual Studio Debugger / LLDB"
Write-Host "  # Android: Android Studio Profiler"
Write-Host "  # System: WPA (Windows Performance Analyzer)"

Write-Host ""
Write-Host "--- EVOLUTION (auto, every 6h) ---" -ForegroundColor Yellow
Write-Host "  cronjob run graph-pulse-export"
Write-Host "  # Checks: security, perf, API compat, arch drift"
Write-Host "  # Reports → C:\Vault\Evolution\"

Write-Host ""
Write-Host "--- KEY PATHS ---" -ForegroundColor Yellow
Write-Host "  C:\Vault\Evolution\CATHEDRAL_CODE_MACHINE.md  # This spec"
Write-Host "  C:\Users\tomas\cathedral-verify.sh            # System check"
Write-Host "  C:\Users\tomas\cathedral-init.sh              # Project init"
Write-Host "  C:\Users\tomas\.cargo\bin\kotlinc.bat         # Kotlin wrapper"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  God Mode Coder: Cathedral is OPERATIONAL" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan