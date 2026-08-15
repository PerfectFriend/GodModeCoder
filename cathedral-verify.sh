#!/usr/bin/env bash
# cathedral-verify.sh — полная верификация Cathedral Code Machine
# Запуск: bash cathedral-verify.sh

set -euo pipefail

echo "=========================================="
echo "  CATHEDRAL CODE MACHINE — VERIFICATION"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check() {
    local name="$1"
    local cmd="$2"
    local expected="${3:-}"
    
    if eval "$cmd" >/dev/null 2>&1; then
        local version=$(eval "$cmd" 2>&1 | head -1)
        echo -e "${GREEN}✅${NC} $name: $version"
        return 0
    else
        echo -e "${RED}❌${NC} $name: NOT FOUND"
        return 1
    fi
}

check_version() {
    local name="$1"
    local cmd="$2"
    local min_version="${3:-}"
    
    if eval "$cmd" >/dev/null 2>&1; then
        local version=$(eval "$cmd" 2>&1 | head -1)
        echo -e "${GREEN}✅${NC} $name: $version"
        return 0
    else
        echo -e "${RED}❌${NC} $name: NOT FOUND"
        return 1
    fi
}

FAILURES=0

echo "--- CORE LANGUAGES & RUNTIMES ---"
check_version "Rust" "rustc --version" || ((FAILURES++))
check_version "Cargo" "cargo --version" || ((FAILURES++))
check_version "Java" "java -version 2>&1 | head -1" || ((FAILURES++))
check_version "Go" "go version" || ((FAILURES++))
check_version "Dart" "dart --version" || ((FAILURES++))
check_version "Node.js" "node --version" || ((FAILURES++))
check_version "Python" "python --version" || ((FAILURES++))

echo ""
echo "--- BUILD SYSTEMS ---"
check_version "Gradle" "/c/gradle-9.1.0/bin/gradle --version 2>&1 | head -1" || ((FAILURES++))
check_version "Maven" "/c/apache-maven-3.9.9/bin/mvn.cmd --version 2>&1 | head -1" || ((FAILURES++))
check_version "CMake" "cmake --version 2>&1 | head -1" || ((FAILURES++))
check_version "MSBuild" "ls /c/Program\ Files/Microsoft\ Visual\ Studio/18/Insiders/MSBuild/Current/Bin/MSBuild.exe 2>/dev/null && echo 'FOUND'" || ((FAILURES++))

echo ""
echo "--- MOBILE & CROSS-PLATFORM ---"
check_version "Flutter" "/c/Users/tomas/develop/flutter/bin/flutter --version 2>&1 | head -1" || ((FAILURES++))
check_version "Kotlin" "cmd.exe /c \"C:\Users\tomas\.cargo\bin\kotlinc.bat -version\" 2>&1" || ((FAILURES++))
check_version "Android SDK" "ls /c/Users/tomas/AppData/Local/Android/Sdk/platforms/ 2>/dev/null | wc -l" || ((FAILURES++))
check_version "Android Studio" "ls /c/Program\ Files/Android/Android\ Studio/bin/studio64.exe 2>/dev/null && echo 'FOUND'" || ((FAILURES++))
check_version "ADB" "adb --version 2>&1 | head -1" || ((FAILURES++))

echo ""
echo "--- NATIVE & SYSTEMS ---"
check_version "LLVM/Clang" "clang --version 2>&1 | head -1" || ((FAILURES++))
check_version "MSVC" "ls /c/Program\ Files/Microsoft\ Visual\ Studio/18/Insiders/VC/Tools/MSVC/14.51.36231/bin/Hostx64/x64/cl.exe 2>/dev/null && echo 'FOUND'" || ((FAILURES++))
check_version "Windows SDK" "ls '/c/Program Files (x86)/Windows Kits/10/bin/10.0.26100.0/' 2>/dev/null && echo 'FOUND (10.0.26100.0)'" || ((FAILURES++))
check_version "Protocol Buffers" "protoc --version 2>&1" || ((FAILURES++))

echo ""
echo "--- INFRASTRUCTURE ---"
check_version "Docker" "docker --version 2>&1" || ((FAILURES++))
check_version "Git" "git --version 2>&1" || ((FAILURES++))

echo ""
echo "--- ENVIRONMENT VARIABLES ---"
for var in JAVA_HOME ANDROID_HOME ANDROID_SDK_ROOT GRADLE_HOME FLUTTER_HOME KOTLIN_HOME MAVEN_HOME LLVM_HOME PROTOC_HOME ANDROID_STUDIO_HOME; do
    val=$(powershell.exe -Command "[Environment]::GetEnvironmentVariable('$var', 'User')" 2>/dev/null | tr -d '\r')
    if [[ -n "$val" && "$val" != "" ]]; then
        echo -e "${GREEN}✅${NC} $var=$val"
    else
        echo -e "${RED}❌${NC} $var: NOT SET"
        ((FAILURES++))
    fi
done

echo ""
echo "=========================================="
if [[ $FAILURES -eq 0 ]]; then
    echo -e "${GREEN}🏛️ CATHEDRAL CODE MACHINE: FULLY OPERATIONAL${NC}"
    echo "=========================================="
    exit 0
else
    echo -e "${RED}⚠️  CATHEDRAL CODE MACHINE: $FAILURES CHECKS FAILED${NC}"
    echo "=========================================="
    exit 1
fi