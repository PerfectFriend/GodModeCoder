# System Audit — 2026-08-06 (Beelink SER9, Ryzen 7 255HX / Radeon 780M, 24GB RAM, Windows 11)

> Snapshot of a fully provisioned dev machine. Use as reference for "what should be installed" on a fresh box.

---

## Windows (winget) — 120+ packages

### Core Dev Toolchains
| Tool | Version | Source |
|------|---------|--------|
| Git | 2.55.0.3 | winget |
| GitHub CLI | 2.97.0 | winget |
| Go | 1.26.5 | winget |
| Dart SDK | 3.12.2 | winget |
| Python | 3.12.10 | winget |
| Rust | 1.97.1 (stable) | rustup |
| JDK | 10.0.302 / 10.0.400-preview | VS installer |
| Node.js | ❌ (use WSL) | — |
| Docker Desktop | 4.85.0 | winget |
| WSL | 2.7.11 | winget |

### Terminal / Shell
| Tool | Version |
|------|---------|
| Windows Terminal | 1.24.11911 |
| PowerShell | 7+ (built-in) |
| git-bash / MSYS | bundled with Git |

### Build / C++
| Tool | Version |
|------|---------|
| CMake | 4.4.1 |
| Ninja | 1.13.2 |
| MSVC / WinLibs | bundled |
| GnuWin32 Make/Zip | 3.81 / 3.0 |

### CLI Utilities
| Tool | Version |
|------|---------|
| ripgrep | 15.2.0 |
| jq | 1.8.2 |
| wget | 1.21.4 |
| ffmpeg | 8.1.2 |
| sqlite | 3.53.4 |
| sox | 14.4.2 |

### AI / ML
| Tool | Version |
|------|---------|
| Ollama | 0.32.6 |
| ComfyUI Desktop | 1.0.35 |

### SSH / VPN
| Tool | Version |
|------|---------|
| OpenSSH Server (Preview) | 10.0.0.0 |
| Tailscale | 1.98.10 |
| Telegram Desktop | 7.0.8 |

### Databases
| Tool | Version |
|------|---------|
| Redis | 3.0.504 |
| SQLite | 3.53.4 |
| SQL Server 2025 LocalDB | 17.0.4025.3 |
| SSMS | 22.8.2 |

### Editors
| Tool | Version |
|------|---------|
| VS Code (User) | 1.131.0 |
| VS Code Insiders | 18.9.12023.133 |
| Vim | 9.2.0 |

### Misc
| Tool | Version |
|------|---------|
| Total Commander | 11.58 |
| Obsidian | 1.13.4 |
| Seelen UI | 2.8.2.0 |
| Sucrose Wallpaper | 26.7.5.0 |

---

## WSL2 — 3 distros

### Ubuntu-24.04 (default, Running)
- Python 3.12.3 (system, full python3-* stack)
- Go 1.22.2 (golang-1.22-go + golang-go)
- Git 2.43.0, Vim 9.1, byobu, cron
- ❌ Node.js, ❌ Rust (only rust-coreutils)

### Ubuntu-26.04 (Running)
- Python 3.14.3 (cutting edge)
- Git 2.53.0, Vim 9.1
- ✅ rust-coreutils 0.8.0
- ❌ Go, ❌ Node.js

### docker-desktop (Running)
- Minimal Alpine for Docker Engine

---

## Rust (Windows)
```
stable-x86_64-pc-windows-msvc (default)
targets: x86_64-pc-windows-msvc
cargo install --list: (empty)
```

---

## Python ML Stack (Windows venv: `C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv`)

| Package | Version |
|---------|---------|
| torch | 2.4.1+cu118 |
| torch-directml | 0.2.5.dev240914 |
| torchaudio | 2.4.1+cu118 |
| torchvision | 0.19.1 |
| transformers | 4.40.0 |
| diffusers | 0.28.0 |
| accelerate | 1.14.0 |
| faster-whisper | 1.2.1 |
| onnxruntime | 1.27.0 |
| xformers | 0.0.27.post2+cu118 |

---

## Missing / To Install

| Item | Command |
|------|---------|
| **cargo binaries** | `cargo install cargo-watch cargo-edit cargo-audit cargo-outdated just ripgrep fd-find zoxide eza bat btop lazygit` |
| **Node.js in WSL** | `curl -fsSL https://deb.nodesource.com/setup_lts.x \| sudo bash - && sudo apt install nodejs` (both Ubuntus) |
| **GitHub SSH key** | `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_github -C "github-tomas"` |
| **Obsidian Vault** | `mkdir -p C:\CodeBase\ObsidianVault && cd ... && git init` |
| **SuperGuard token** | Edit `gateways\superguard\.env` |
| **VS Code extensions** | Install: Rust Analyzer, Python, GitLens, Docker, WSL, etc. |

---

## Verification Commands

```bash
# Windows
winget list --name Go --name Git --name Rust --name Python --name Docker

# WSL (Ubuntu-24.04)
wsl -d Ubuntu-24.04 -- bash -c 'go version && python3 --version && git --version'

# Rust
rustup show

# Python venv
C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.version.cuda)"
```

---

> **Generated**: 2026-08-06 by Hermes Agent during system audit session.  
> **Machine**: Beelink SER9 (Ryzen 7 255HX / Radeon 780M, 24GB RAM, Win 11)  
> **Purpose**: Reference for fresh machine provisioning / drift detection.