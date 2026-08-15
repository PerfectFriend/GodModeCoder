---
name: windows-ssh-server-setup
description: "Use when installing OpenSSH Server on Windows from MSYS."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [windows, openssh, ssh, server, sshd, keys, authentication]
---

# Windows OpenSSH Server Setup

Reliable path to install, configure, and verify OpenSSH Server (`sshd`) on Windows when working from a git-bash / MSYS terminal. Avoids the common pitfalls: missing `sshd.exe`, host key permission errors, `administrators_authorized_keys` format issues, and Microsoft Account users without local passwords.

## When to use
- Setting up SSH access to a Windows machine (dev box, CI runner, home server).
- Need key-based auth for administrators and/or local users.
- Running from git-bash/MSYS (not PowerShell directly).

## Prerequisites
- Windows 10/11 with admin rights (UAC prompt required for service install/start).
- `winget` available (bundled since Win 10 1809).
- Git-bash / MSYS terminal (this skill's commands assume `/c/...` paths).

## Install OpenSSH Server

```bash
# Best via winget preview (includes sshd.exe; stable OpenSSH.Server often missing from winget)
winget install Microsoft.OpenSSH.Preview

# Verify sshd.exe exists
ls /c/Program\ Files/OpenSSH/sshd.exe
```

## Generate host keys (required before first start)

```bash
# Run from MSYS bash
/c/Program\ Files/OpenSSH/ssh-keygen.exe -A
# Keys land in C:\ProgramData\ssh\ssh_host_*_key
```

## Fix host key permissions (critical — else `sshd: no hostkeys available`)

```bash
# Run elevated (PowerShell -Verb RunAs)
icacls "C:\ProgramData\ssh\ssh_host_*" /reset
# Or: TakeOwn /F C:\ProgramData\ssh\ssh_host_* /A  then icacls ... /grant SYSTEM:F /grant Administrators:F
```

## Configure `sshd_config`

Edit `C:\ProgramData\ssh\sshd_config` (needs admin):
- `PasswordAuthentication yes`  (uncomment)
- `PubkeyAuthentication yes`    (uncomment)
- Ensure `AuthorizedKeysFile .ssh/authorized_keys` is set

**Pitfall:** Default config has a `Match Group administrators` block that forces admins to use `C:\ProgramData\ssh\administrators_authorized_keys`. If you want admins to use their user `~/.ssh/authorized_keys`, comment out that entire block:

```
# Match Group administrators
#        AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```

## Create `administrators_authorized_keys` correctly (if keeping the Match block)

```bash
# Must be a SINGLE LINE, ASCII, LF endings, no BOM
echo "ssh-ed25519 AAAAC3... user@host" > C:\ProgramData\ssh\administrators_authorized_keys
# Use a .bat file run elevated to bypass shell redirection issues:
# echo ssh-ed25519 ... > C:\ProgramData\ssh\administrators_authorized_keys
```

## Start the service

```bash
# Elevated
sc start sshd
sc query sshd  # should show RUNNING
```

## Firewall rule

```bash
# Elevated
netsh advfirewall firewall add rule name="OpenSSH Server" dir=in action=allow protocol=TCP localport=22
```

## User setup

### Local user with password (recommended for password auth)
```bash
# Elevated
net user sshuser "StrongPass123!" /add
net localgroup administrators sshuser /add
```

### Microsoft Account user (e.g., `tomas@outlook.com`)
- No local password → password auth **will not work**.
- Use **key-based auth only**: generate key, put public key in `C:\Users\<name>\.ssh\authorized_keys`.

### Built-in Administrator
```bash
# Elevated
net user Администратор /active:yes
net user Администратор "StrongPass123!"
```

## Key-based auth for a user

```bash
# On client
ssh-keygen -t ed25519

# On server (as that user)
mkdir -p ~/.ssh
echo "<public-key>" > ~/.ssh/authorized_keys
# Permissions: only user + SYSTEM + Administrators should have access
icacls ~/.ssh/authorized_keys /inheritance:r /grant:r "%USERNAME%:F" /grant:r "SYSTEM:F" /grant:r "Administrators:F"
```

## Verification

```bash
# From client
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null user@host "echo OK"
# With key
ssh -i ~/.ssh/id_ed25519 user@host "echo OK"
```

## Common pitfalls & fixes

| Symptom | Cause | Fix |
|---|---|---|
| `sshd.exe` not found | Wrong OpenSSH package | Install `Microsoft.OpenSSH.Preview` |
| `no hostkeys available` | Host key permissions | `icacls C:\ProgramData\ssh\ssh_host_* /reset` (elevated) |
| `Permission denied (publickey)` for admin | `Match Group administrators` uses `administrators_authorized_keys` but file malformed | Fix file format (single line, LF, no BOM) OR comment out Match block |
| Password auth fails for Microsoft Account user | No local password | Use key auth or create local user |
| `sc start sshd` error 5 | Not elevated | Run terminal as Administrator |
| Connection hangs after key exchange | Firewall | Add inbound rule for TCP 22 |

## Support files

- `templates/sshd_config.template` — clean starter config with Match block commented.
- `scripts/fix_administrators_keys.bat` — elevated batch to write `administrators_authorized_keys` correctly.
- `scripts/install_openssh_server.bat` — full elevated install+config script.
- `references/ssh-key-format-fix.md` — detailed fix for `administrators_authorized_keys` format issues (CRLF, BOM, whitespace).
- `references/debugging-log-2026-08-06.md` — session log with root causes, working commands, and fixes for key auth failure, Microsoft Account password issue, and gateway startup.

## Related skills
- `windows-dev-env-setup` — for installing toolchains on the same box.
- `hermes-gateway-setup` — if this SSH server is for Hermes gateway access.