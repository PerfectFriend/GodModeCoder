# WSL2 Hybrid Architecture Pattern

## Decision Record

**Context**: Need to run Linux backend services (Go, Docker, VPN/TUN) alongside Windows-native UI apps (Flutter, Electron) with shared data.

**Decision**: Hybrid WSL2 + native Windows approach.

**Rationale**:
- WSL2 provides real Linux kernel, systemd, Docker, TUN/TAP support
- Windows-native Flutter/Electron apps get GPU acceleration, native look/feel
- Bind mounts (`C:\Project-data` ↔ `/mnt/c/Project-data`) enable zero-copy data sharing
- Avoids full native Windows port complexity (Wintun driver, Windows Services, path translation)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Windows Host                         │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Flutter Apps    │  │  Shared Data     │                │
│  │  (The-Isle,      │  │  C:\Project-data │◄──┐            │
│  │   Royal-Isle)    │  └──────────────────┘   │            │
│  └──────────────────┘                         │            │
└────────────────────────────────────────────────┼────────────┘
                                                 │ Bind Mount (9P)
┌────────────────────────────────────────────────┼────────────┐
│                     WSL2 (Ubuntu)              │            │
│  ┌──────────────────┐  ┌──────────────────┐   │            │
│  │  Go Backend      │  │  Shared Data     │───┘            │
│  │  (ParanoidX)     │  │  /mnt/c/Project  │                │
│  └──────────────────┘  └──────────────────┘                │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  Docker          │  │  systemd         │                │
│  │  (Postgres,      │  │  (services)      │                │
│  │   Redis, etc.)   │  └──────────────────┘                │
│  └──────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Go backend** writes to `/mnt/c/Project-data/logs/`, `/mnt/c/Project-data/dc/`
2. **Flutter apps** read/write `C:\Project-data\logs\`, `C:\Project-data\dc\`
3. **Docker volumes** can also mount `/mnt/c/Project-data` for DB persistence
4. **VPN/TUN** works natively in WSL2 (no Wintun needed for backend)

## When to Use Full Native Windows Instead

- VPN client must integrate with Windows networking stack (split tunneling, system proxy)
- Kernel-mode drivers required
- Real-time audio/video processing with Windows APIs
- Distribution as single `.exe` without WSL2 dependency