# Fixing `administrators_authorized_keys` Format on Windows

## Problem
The `administrators_authorized_keys` file at `C:\ProgramData\ssh\administrators_authorized_keys` must be:
- **Single line** (no newlines inside the key)
- **LF endings** (not CRLF)
- **No BOM** (UTF-8 without BOM, or ASCII)
- Correct permissions (only SYSTEM + Administrators readable)

## Symptoms of wrong format
- `debug1: Server accepts key` but then `Permission denied`
- `debug3: sign_and_send_pubkey` succeeds but no session established
- File shows multiple lines in hex dump (0x0d 0x0a = CRLF)

## Root causes in this session
1. PowerShell `Out-File` / `Set-Content` adds CRLF and BOM by default
2. `echo` from cmd in heredoc/VBS adds extra whitespace
3. `write_file` tool writes via bash which may mangle paths

## Working fix (use elevated batch file)

```bat
@echo off
echo ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP8t5XQD4SOBiXtz38H0UT54dCW2GOUMrwp3oLxMOv+p tomas@INQUIZITOR > C:\ProgramData\ssh\administrators_authorized_keys
```

Run as Administrator. This produces clean single-line ASCII with LF.

## Verification
```cmd
type C:\ProgramData\ssh\administrators_authorized_keys
```
Should show exactly one line: `ssh-ed25519 AAAA... user@host`

```cmd
certutil -encodehex C:\ProgramData\ssh\administrators_authorized_keys C:\temp\auth.hex && type C:\temp\auth.hex
```
Check: no 0x0d (CR), no 0xef 0xbb 0xbf (BOM), key is contiguous.

## Alternative: Disable Match block entirely
In `sshd_config`, comment out:
```
# Match Group administrators
#       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```
Then admins use their own `~/.ssh/authorized_keys` (easier to manage).