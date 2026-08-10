<# =============================================================================
# Register Hermes Gateways as Windows Scheduled Tasks (run at startup)
# Run this script as Administrator
# ============================================================================= #>

param(
    [switch]$Unregister
)

$hermesHome = "C:\Users\tomas\AppData\Local\hermes"

$gateways = @(
    @{
        Name        = "Hermes-Gateway-Main"
        Description = "Hermes Agent Gateway - Main Bot (personal)"
        EnvPath     = "$hermesHome\gateways\main\.env"
        ScriptPath  = "$hermesHome\gateways\main\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\main\Hermes_Gateway.vbs"
        User        = "tomas"
    },
    @{
        Name        = "Hermes-Gateway-SuperGuard"
        Description = "Hermes Agent Gateway - SuperGuard Alarm Bot"
        EnvPath     = "$hermesHome\gateways\superguard\.env"
        ScriptPath  = "$hermesHome\gateways\superguard\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\superguard\Hermes_Gateway.vbs"
        User        = "tomas"
    }
)

if ($Unregister) {
    Write-Host "Unregistering existing tasks..." -ForegroundColor Yellow
    foreach ($gw in $gateways) {
        try {
            Unregister-ScheduledTask -TaskName $gw.Name -Confirm:$false -ErrorAction Stop
            Write-Host "  Unregistered: $($gw.Name)"
        } catch {
            Write-Host "  Not found: $($gw.Name)"
        }
    }
    exit 0
}

Write-Host "Registering Hermes Gateway tasks..." -ForegroundColor Green

foreach ($gw in $gateways) {
    if (-not (Test-Path $gw.ScriptPath)) {
        Write-Error "  Script not found: $($gw.ScriptPath)"
        continue
    }
    if (-not (Test-Path $gw.EnvPath)) {
        Write-Error "  .env not found: $($gw.EnvPath)"
        continue
    }

    $action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "//B `"$($gw.VbsPath)`""
    $trigger = New-ScheduledTaskTrigger -AtStartup
    
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 2) `
        -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
        -MultipleInstances IgnoreNew

    $principal = New-ScheduledTaskPrincipal -UserId $gw.User -LogonType Interactive -RunLevel Highest

    try {
        Register-ScheduledTask `
            -TaskName $gw.Name `
            -Description $gw.Description `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Principal $principal `
            -Force `
            -ErrorAction Stop
        Write-Host "  Registered: $($gw.Name)"
    } catch {
        Write-Error "  Failed to register $($gw.Name): $_"
    }
}

Write-Host "`nDone. Tasks will run at next login/boot." -ForegroundColor Green
Write-Host "To start now:" -ForegroundColor Cyan
Write-Host "  Start-ScheduledTask -TaskName 'Hermes-Gateway-Main'"
Write-Host "  Start-ScheduledTask -TaskName 'Hermes-Gateway-SuperGuard'"