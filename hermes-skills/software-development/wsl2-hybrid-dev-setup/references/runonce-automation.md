# RunOnce Post-Reboot Automation Pattern

## Problem

WSL2 installation and configuration often requires **multiple reboots**. Scripts must survive reboot and continue from where they left off.

## Solution: Registry RunOnce Key

Windows `HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce` runs commands **once per user login**, then deletes the value.

## Pattern

```powershell
$runOnceKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce"
$runOnceValue = "MyProject-Setup"

# On phase completion, register next phase:
Set-ItemProperty -Path $runOnceKey -Name $runOnceValue -Value "next-phase-name" -Force

# Trigger reboot
Restart-Computer -Force
```

## Script Structure

```powershell
# 1. Determine current phase
$phase = "init"
if (Get-ItemProperty -Path $runOnceKey -Name $runOnceValue -ErrorAction SilentlyContinue) {
    $phase = (Get-ItemProperty -Path $runOnceKey -Name $runOnceValue).($runOnceValue)
    Remove-ItemProperty -Path $runOnceKey -Name $runOnceValue -ErrorAction SilentlyContinue
}

# 2. Phase switch
switch ($phase) {
    "init" { 
        # Enable WSL2 features, install Ubuntu
        # If reboot needed:
        Set-ItemProperty -Path $runOnceKey -Name $runOnceValue -Value "configure-wsl" -Force
        Restart-Computer -Force
    }
    "configure-wsl" {
        # Create user, write wsl.conf, set default user
        Set-ItemProperty -Path $runOnceKey -Name $runOnceValue -Value "clone-repos" -Force
        Restart-Computer -Force  # For clean systemd
    }
    "clone-repos" {
        # Clone repos
        Set-ItemProperty -Path $runOnceKey -Name $runOnceValue -Value "build-go" -Force
    }
    "build-go" {
        # Install Go, build project, create data folder
    }
}
```

## Key Points

1. **RunOnce runs at user LOGIN**, not at boot. User must log in.
2. **Value is DELETED after execution** - safe for repeated reboots.
3. **Use descriptive phase names** for debugging: `install-wsl`, `configure-wsl`, `clone-repos`, `build-go`
4. **Always remove the value at phase start** to avoid re-execution on crash.
5. **Pass data between phases** via files in `$env:TEMP` or script parameters.

## Phase Design Rules

| Phase | Should Reboot? | Reason |
|-------|----------------|--------|
| Enable WSL features | Yes | Kernel/driver load |
| Install Ubuntu | Yes | First-run initialization |
| Write wsl.conf | Yes | systemd activation |
| Clone repos | No | Pure user-space |
| Build project | No | Pure user-space |

## Example: Multi-Phase WSL2 Setup

See `setup-wsl2-hybrid-full.ps1` for complete implementation with 4 phases and 2-3 reboots.

## Troubleshooting

**Script doesn't resume after reboot**:
- Check RunOnce key exists: `reg query HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce /v MyProject-Setup`
- User must log in interactively (not RDP, not service account)
- PowerShell execution policy must allow script (`-ExecutionPolicy Bypass`)

**Phase runs twice**:
- Forgot to `Remove-ItemProperty` at phase start
- Two scripts using same RunOnce value name

**Access denied writing RunOnce**:
- Must run in user context (not SYSTEM)
- HKCU is per-user, works in admin PowerShell if same user