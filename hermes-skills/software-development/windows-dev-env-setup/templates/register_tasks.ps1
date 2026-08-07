<# =============================================================================
# Register Hermes Gateways as Windows Scheduled Tasks (run at startup)
# Run this script as Administrator
# ============================================================================= #>

param(
    [switch]$Unregister
)

$hermesHome = "C:\Users\<user>\AppData\Local\hermes"

$gateways = @(
    @{
        Name        = "Hermes-Gateway-Cathedral"
        Description = "Hermes Agent Gateway - Cathedral Bot (main)"
        EnvPath     = "$hermesHome\gateways\Cathedral\.env"
        ScriptPath  = "$hermesHome\gateways\Cathedral\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\Cathedral\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-Torquemada"
        Description = "Hermes Agent Gateway - Torquemada Bot"
        EnvPath     = "$hermesHome\gateways\Torquemada\.env"
        ScriptPath  = "$hermesHome\gateways\Torquemada\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\Torquemada\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-Nexus"
        Description = "Hermes Agent Gateway - Nexus Bot"
        EnvPath     = "$hermesHome\gateways\Nexus\.env"
        ScriptPath  = "$hermesHome\gateways\Nexus\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\Nexus\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-Node2Bot"
        Description = "Hermes Agent Gateway - Node2Bot Bot"
        EnvPath     = "$hermesHome\gateways\Node2Bot\.env"
        ScriptPath  = "$hermesHome\gateways\Node2Bot\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\Node2Bot\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-Elemental"
        Description = "Hermes Agent Gateway - Elemental Bot"
        EnvPath     = "$hermesHome\gateways\Elemental\.env"
        ScriptPath  = "$hermesHome\gateways\Elemental\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\Elemental\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-NodeBot"
        Description = "Hermes Agent Gateway - NodeBot Bot"
        EnvPath     = "$hermesHome\gateways\NodeBot\.env"
        ScriptPath  = "$hermesHome\gateways\NodeBot\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\NodeBot\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-Шурген420"
        Description = "Hermes Agent Gateway - Шурген420 Bot"
        EnvPath     = "$hermesHome\gateways\Шурген420\.env"
        ScriptPath  = "$hermesHome\gateways\Шурген420\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\Шурген420\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-StonedBot"
        Description = "Hermes Agent Gateway - StonedBot Bot"
        EnvPath     = "$hermesHome\gateways\StonedBot\.env"
        ScriptPath  = "$hermesHome\gateways\StonedBot\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\StonedBot\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-Tomas"
        Description = "Hermes Agent Gateway - Tomas Bot"
        EnvPath     = "$hermesHome\gateways\Tomas\.env"
        ScriptPath  = "$hermesHome\gateways\Tomas\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\Tomas\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-Steward"
        Description = "Hermes Agent Gateway - Steward Bot"
        EnvPath     = "$hermesHome\gateways\Steward\.env"
        ScriptPath  = "$hermesHome\gateways\Steward\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\Steward\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-MyGemma"
        Description = "Hermes Agent Gateway - MyGemma Bot"
        EnvPath     = "$hermesHome\gateways\MyGemma\.env"
        ScriptPath  = "$hermesHome\gateways\MyGemma\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\MyGemma\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-DarkPushkin"
        Description = "Hermes Agent Gateway - DarkPushkin Bot"
        EnvPath     = "$hermesHome\gateways\DarkPushkin\.env"
        ScriptPath  = "$hermesHome\gateways\DarkPushkin\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\DarkPushkin\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-MasterInquisitor"
        Description = "Hermes Agent Gateway - MasterInquisitor Bot"
        EnvPath     = "$hermesHome\gateways\MasterInquisitor\.env"
        ScriptPath  = "$hermesHome\gateways\MasterInquisitor\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\MasterInquisitor\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-SuperGuard"
        Description = "Hermes Agent Gateway - SuperGuard Alarm Bot"
        EnvPath     = "$hermesHome\gateways\SuperGuard\.env"
        ScriptPath  = "$hermesHome\gateways\SuperGuard\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\SuperGuard\Hermes_Gateway.vbs"
        User        = "<user>"
    },
    @{
        Name        = "Hermes-Gateway-RedShredZombie"
        Description = "Hermes Agent Gateway - RedShredZombie Bot"
        EnvPath     = "$hermesHome\gateways\RedShredZombie\.env"
        ScriptPath  = "$hermesHome\gateways\RedShredZombie\Hermes_Gateway.cmd"
        VbsPath     = "$hermesHome\gateways\RedShredZombie\Hermes_Gateway.vbs"
        User        = "<user>"
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
Write-Host "  Start-ScheduledTask -TaskName 'Hermes-Gateway-Cathedral'"
Write-Host "  Start-ScheduledTask -TaskName 'Hermes-Gateway-SuperGuard'"
Write-Host "  ... (all 15 tasks)"