#!/usr/bin/env powershell
<#
.SYNOPSIS
    Verify ParanoidX Hybrid Stack after setup
.USAGE
    powershell -ExecutionPolicy Bypass -File "scripts\verify-wsl2-setup.ps1"
#>

$ErrorActionPreference = "Stop"

function Check($name, $cmd) {
    Write-Host -NoNewline "[$name] "
    try {
        $result = & $cmd
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK]" -ForegroundColor Green
            return $true
        } else {
            Write-Host "[FAIL]" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "[ERR] $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host "============================================================"
Write-Host "PARANOIDX HYBRID STACK VERIFICATION"
Write-Host "============================================================"

$passed = 0
$total = 0

# WSL2
$total++; if (Check "WSL2 Ubuntu running" { wsl -d Ubuntu-24.04 -- bash -c 'echo ok' }) { $passed++ }
$total++; if (Check "User tomas exists" { wsl -d Ubuntu-24.04 -- bash -c 'id tomas' }) { $passed++ }
$total++; if (Check "Systemd enabled" { wsl -d Ubuntu-24.04 -- bash -c 'ps -p 1 -o comm=' }) { $passed++ }

# Docker
$total++; if (Check "Docker available" { wsl -d Ubuntu-24.04 -- docker ps }) { $passed++ }
$total++; if (Check "5 containers running" { wsl -d Ubuntu-24.04 -- docker ps --format '{{.Names}}' 2>&1 | Measure-Object | Select-Object -ExpandProperty Count }) { $passed++ }
$total++; if (Check "V2Ray (10808)" { wsl -d Ubuntu-24.04 -- nc -z localhost 10808 2>&1 }) { $passed++ }
$total++; if (Check "SMP Server (5223)" { wsl -d Ubuntu-24.04 -- nc -z localhost 5223 2>&1 }) { $passed++ }
$total++; if (Check "XFTP Server (5225)" { wsl -d Ubuntu-24.04 -- nc -z localhost 5225 2>&1 }) { $passed++ }
$total++; if (Check "Coturn (3478)" { wsl -d Ubuntu-24.04 -- nc -z localhost 3478 2>&1 }) { $passed++ }
$total++; if (Check "Tor (9050)" { wsl -d Ubuntu-24.04 -- nc -z localhost 9050 2>&1 }) { $passed++ }

# Go API
$total++; if (Check "Go API health" { Invoke-WebRequest -Uri "http://localhost:8080/api/health" -TimeoutSec 3 }) { $passed++ }
$total++; if (Check "Go API status" { Invoke-WebRequest -Uri "http://localhost:8080/api/status" -TimeoutSec 3 }) { $passed++ }
$total++; if (Check "Node info Docker healthy" { 
    $r = Invoke-WebRequest -Uri "http://localhost:8080/api/admin/info" -TimeoutSec 3
    $data = $r.Content | ConvertFrom-Json
    $data.services.docker.healthy -eq $true
}) { $passed++ }

# Shared data mount
$total++; if (Check "C:\ParanoidX-data exists" { Test-Path "C:\ParanoidX-data" }) { $passed++ }
$total++; if (Check "Bind mount works" { wsl -d Ubuntu-24.04 -- test -d /mnt/c/ParanoidX-data }) { $passed++ }

# Flutter builds
$total++; if (Check "The-Isle .exe built" { Test-Path "C:\Users\tomas\The-Isle\build\windows\x64\runner\Release\isle_app.exe" }) { $passed++ }
$total++; if (Check "Royal-Isle .exe built" { Test-Path "C:\Users\tomas\Royal-Isle\build\windows\x64\runner\Release\royal_app.exe" }) { $passed++ }

# Summary
Write-Host ""
Write-Host "============================================================"
Write-Host "SUMMARY: $passed / $total checks passed"
Write-Host "============================================================"
if ($passed -eq $total) {
    Write-Host "ALL CHECKS PASSED" -ForegroundColor Green
    exit 0
} else {
    Write-Host "SOME CHECKS FAILED" -ForegroundColor Red
    exit 1
}