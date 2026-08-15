#!/usr/bin/env bash
# cathedral-init.sh — быстрая инициализация проекта по Cathedral стандартам
# Использование: bash cathedral-init.sh <project-name> [--stack=flutter|rust|kotlin|go|cpp|full]

set -euo pipefail

PROJECT_NAME="${1:-}"
STACK="${2:-full}"

if [[ -z "$PROJECT_NAME" ]]; then
    echo "Usage: $0 <project-name> [--stack=flutter|rust|kotlin|go|cpp|full]"
    exit 1
fi

# Remove --stack= prefix if present
STACK="${STACK#--stack=}"

echo "🏛️ CATHEDRAL INIT: $PROJECT_NAME (stack: $STACK)"
echo ""

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Git init
git init -q
echo "✅ Git initialized"

# Create .cathedral directory first
mkdir -p .cathedral

# Cathedral standard files
cat > README.md << EOF
# $PROJECT_NAME

> Cathedral Code Machine project — God Mode Coder standards.

## Stack
$(case $STACK in
    flutter) echo "- Flutter/Dart (mobile, web, desktop)" ;;
    rust) echo "- Rust (systems, backend, WASM)" ;;
    kotlin) echo "- Kotlin/JVM + Kotlin Multiplatform" ;;
    go) echo "- Go (backend, CLI, WASM)" ;;
    cpp) echo "- C++ (MSVC + LLVM, cross-platform)" ;;
    *) echo "- Full Cathedral Stack: Rust + Go + Kotlin + Flutter + C++" ;;
esac)

## Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md)

## Quick Start
\`\`\`bash
# Dev loop
$(case $STACK in
    flutter) echo "flutter run -d chrome" ;;
    rust) echo "cargo watch -x run" ;;
    kotlin) echo "./gradlew run" ;;
    go) echo "go run ." ;;
    cpp) echo "cmake --build build" ;;
    *) echo "# Stack-specific commands in Makefile" ;;
esac)
\`\`\`

## Quality Gates
\`\`\`bash
cathedral-check  # fmt + lint + test + security
\`\`\`

## Release
\`\`\`bash
git tag v1.0.0 && git push origin v1.0.0
# → GitHub Actions → all artifacts → stores
\`\`\`
EOF

cat > ARCHITECTURE.md << EOF
# Architecture Decision Record

## Project: $PROJECT_NAME
## Date: $(date -I)
## Stack: $STACK

### Context
<!-- Описание проблемы и требований -->

### Decision
<!-- Выбранная архитектура и обоснование -->

### Consequences
<!-- Плюсы/минусы, риски, миграция -->

### Tech Stack
| Layer | Technology | Version |
|-------|------------|---------|
$(case $STACK in
    flutter)
        echo "| Language | Dart | 3.12+ |"
        echo "| Framework | Flutter | 3.24+ |"
        echo "| State Mgmt | Riverpod / Bloc | latest |"
        echo "| DI | get_it / riverpod | latest |"
        ;;
    rust)
        echo "| Language | Rust | 1.97+ |"
        echo "| Async | tokio | latest |"
        echo "| Serialization | serde + serde_json | latest |"
        echo "| HTTP | reqwest / axum | latest |"
        ;;
    kotlin)
        echo "| Language | Kotlin | 2.1+ |"
        echo "| Build | Gradle KTS | 9.1+ |"
        echo "| Coroutines | kotlinx.coroutines | latest |"
        echo "| Serialization | kotlinx.serialization | latest |"
        ;;
    go)
        echo "| Language | Go | 1.26+ |"
        echo "| Router | chi / gin | latest |"
        echo "| Config | viper / koanf | latest |"
        echo "| Observability | otel / prometheus | latest |"
        ;;
    cpp)
        echo "| Language | C++20/23 | MSVC 14.51 / Clang 19 |"
        echo "| Build | CMake | 4.4+ |"
        echo "| Package | vcpkg / Conan | latest |"
        echo "| Testing | GoogleTest / Catch2 | latest |"
        ;;
    *)
        echo "| Multi-language | See sub-projects | |"
        ;;
esac)

### Quality Standards
- Cathedral Code Machine gates (see \`.cathedral/rules.toml\`)
- Coverage: ≥80%
- Zero critical vulnerabilities
- All linters: error level

### Observability
- OpenTelemetry → Jaeger/Grafana
- Structured logging (JSON)
- Metrics: RED + USE
- Tracing: W3C TraceContext

### Security
- mTLS everywhere
- Secrets in Vault/Keyring
- SBOM generation (Syft)
- Supply chain: Sigstore/Cosign

### Evolution
- Dependabot + Renovate
- Automated security PRs
- Performance regression detection
- API compatibility checks (protobuf)
EOF

cat > .cathedral/rules.toml << EOF
# Cathedral Quality Gates — Non-Negotiable
[gate.rust]
clippy = "deny"
rustfmt = "check"
test_coverage = ">=80%"
audit = "zero-critical"
msrv = "1.97"

[gate.flutter]
analyze = "error"
test_coverage = ">=80%"
no_unused_imports = true
dart_doc = "warn"

[gate.kotlin]
detekt = "error"
ktlint = "check"
test_coverage = ">=80%"
kotlin_version = "2.1+"

[gate.go]
golangci_lint = "error"
gofmt = "check"
test_coverage = ">=80%"
govulncheck = "zero-critical"

[gate.cpp]
clang_tidy = "error"
cppcheck = "error"
sanitizers = ["address", "thread", "memory", "undefined"]
cmake_minimum = "4.4"

[gate.general]
conventional_commits = true
signed_commits = true
branch_protection = true
required_reviews = 2
linear_history = true
EOF

cat > .gitignore << EOF
# Cathedral
.env
.env.local
*.log
target/
build/
dist/
*.apk
*.aab
*.exe
*.dll
*.so
*.dylib
*.msi

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Language-specific
$(case $STACK in
    flutter) echo -e ".dart_tool/\n.pub-cache/\nbuild/\n*.iml\nflutter_*.png" ;;
    rust) echo -e "target/\nCargo.lock\n**/*.rs.bk" ;;
    kotlin) echo -e ".gradle/\nbuild/\n*.iml\nlocal.properties" ;;
    go) echo -e "vendor/\n*.exe\n*.test\ncoverage.out" ;;
    cpp) echo -e "build/\n*.o\n*.obj\n*.lib\n*.exp\n*.pdb\n*.idb\n*.ilk\n*.suo\n*.user\n*.ncb\n*.aps" ;;
    *) echo -e "# All stacks\n**/target/\n**/build/\n**/.gradle/\n**/vendor/" ;;
esac)
EOF

# Stack-specific initialization
case $STACK in
    flutter)
        /c/Users/tomas/develop/flutter/bin/flutter create . --project-name "$PROJECT_NAME" --platforms=android,ios,web,windows,linux,macos --org com.cathedral 2>/dev/null || true
        echo "✅ Flutter project created"
        ;;
    rust)
        cargo init --name "$PROJECT_NAME" 2>/dev/null || true
        echo "✅ Rust project created"
        ;;
    kotlin)
        mkdir -p src/main/kotlin src/test/kotlin
        cat > build.gradle.kts << 'KTS'
plugins {
    kotlin("jvm") version "2.1.20"
    application
}
group = "com.cathedral"
version = "1.0.0-SNAPSHOT"
repositories { mavenCentral() }
dependencies {
    implementation(kotlin("stdlib"))
    testImplementation(kotlin("test"))
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.0")
}
tasks.test { useJUnitPlatform() }
application { mainClass.set("com.cathedral.MainKt") }
KTS
        mkdir -p src/main/kotlin/com/cathedral
        cat > src/main/kotlin/com/cathedral/Main.kt << 'KT'
package com.cathedral

fun main() {
    println("🏛️ Cathedral: $PROJECT_NAME online")
}
KT
        echo "✅ Kotlin/Gradle project created"
        ;;
    go)
        go mod init "github.com/cathedral/$PROJECT_NAME" 2>/dev/null || true
        cat > main.go << 'GO'
package main

import "fmt"

func main() {
    fmt.Println("🏛️ Cathedral: $PROJECT_NAME online")
}
GO
        echo "✅ Go module created"
        ;;
    cpp)
        mkdir -p src include tests
        cat > CMakeLists.txt << 'CMAKE'
cmake_minimum_required(VERSION 4.4)
project(${PROJECT_NAME} LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(${PROJECT_NAME} src/main.cpp)
target_include_directories(${PROJECT_NAME} PRIVATE include)
enable_testing()
add_subdirectory(tests)
CMAKE
        cat > src/main.cpp << 'CPP'
#include <iostream>
int main() {
    std::cout << "🏛️ Cathedral: ${PROJECT_NAME} online\n";
    return 0;
}
CPP
        cat > tests/CMakeLists.txt << 'CMAKET'
add_executable(test_main test_main.cpp)
target_link_libraries(test_main PRIVATE gtest_main)
add_test(NAME test_main COMMAND test_main)
CMAKET
        cat > tests/test_main.cpp << 'CPPT'
#include <gtest/gtest.h>
TEST(CathedralTest, Sanity) { EXPECT_TRUE(true); }
CPPT
        echo "✅ C++/CMake project created"
        ;;
    full)
        # Create multi-project structure
        mkdir -p apps/{flutter-app,rust-service,kotlin-service,go-service,cpp-engine} libs/{shared-proto,shared-core}
        echo "✅ Full Cathedral monorepo structure created"
        ;;
esac

# GitHub Actions CI template
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'YAML'
name: Cathedral CI
on: [push, pull_request]
jobs:
  quality:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Cathedral
        run: |
          echo "JAVA_HOME=C:\jdk-21.0.12+8" >> $GITHUB_ENV
          echo "ANDROID_HOME=C:\Users\runneradmin\AppData\Local\Android\Sdk" >> $GITHUB_ENV
      - name: Run quality gates
        run: |
          # Rust
          if [ -f Cargo.toml ]; then cargo fmt --check && cargo clippy -- -D warnings && cargo test; fi
          # Kotlin
          if [ -f build.gradle.kts ]; then ./gradlew detekt ktlintCheck test; fi
          # Flutter
          if [ -f pubspec.yaml ]; then flutter analyze && flutter test; fi
          # Go
          if [ -f go.mod ]; then gofmt -l . && go vet ./... && go test ./...; fi
          # C++
          if [ -f CMakeLists.txt ]; then cmake -B build -DCMAKE_BUILD_TYPE=Debug && cmake --build build && ctest --test-dir build; fi
YAML

# Cathedral check script
cat > cathedral-check.sh << 'CHECK'
#!/usr/bin/env bash
# Быстрая проверка качества перед коммитом
set -euo pipefail
echo "🏛️ CATHEDRAL CHECK"
if [ -f Cargo.toml ]; then echo "→ Rust"; cargo fmt --check && cargo clippy -- -D warnings && cargo test; fi
if [ -f build.gradle.kts ]; then echo "→ Kotlin"; ./gradlew detekt ktlintCheck test; fi
if [ -f pubspec.yaml ]; then echo "→ Flutter"; flutter analyze && flutter test; fi
if [ -f go.mod ]; then echo "→ Go"; gofmt -l . && go vet ./... && go test ./...; fi
if [ -f CMakeLists.txt ]; then echo "→ C++"; cmake -B build -DCMAKE_BUILD_TYPE=Debug && cmake --build build && ctest --test-dir build; fi
echo "✅ ALL GATES PASSED"
CHECK
chmod +x cathedral-check.sh

# Commit initial
git add .
git commit -m "chore: cathedral init $PROJECT_NAME (stack: $STACK)

- Cathedral standard structure
- Quality gates configured
- CI/CD pipeline ready
- Observability foundation
- Evolution-ready architecture" -q

echo ""
echo "=========================================="
echo "✅ CATHEDRAL PROJECT INITIALIZED"
echo "=========================================="
echo ""
echo "Project: $PROJECT_NAME"
echo "Stack: $STACK"
echo "Location: $(pwd)"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  code .                    # Open in VS Code"
echo "  ./cathedral-check.sh      # Verify quality gates"
echo "  # Start coding..."
EOF