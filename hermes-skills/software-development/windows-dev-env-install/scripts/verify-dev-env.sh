#!/usr/bin/env bash
# verify-dev-env.sh — check a Windows dev toolchain is installed and on PATH.
# Usage: bash verify-dev-env.sh
# Exit 0 if all found, non-zero otherwise. Prints a table.

ok=0; miss=0

check() {
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "  ✓ $name"; ok=$((ok+1))
  else
    echo "  ✗ $name — НЕ найден"; miss=$((miss+1))
  fi
}

echo "== Dev toolchain check =="
check "Go        " go version
check "Dart      " dart --version
check "Rustc     " rustc --version
check "Cargo     " cargo --version
check "Java      " java -version
check "Javac     " javac -version
check "Python    " python --version
check "VSCode    " code --version
check "ADB       " adb version
check "sdkmanager" sdkmanager --version

echo ""
echo "Итог: $ok найдено, $miss отсутствует"
# NOTE: binaries installed into user PATH (via [Environment]::SetEnvironmentVariable)
# only appear in NEW terminals. If a check fails but you just installed it,
# re-run from a fresh shell or prepend the known install dirs to PATH.
[ "$miss" -eq 0 ]
