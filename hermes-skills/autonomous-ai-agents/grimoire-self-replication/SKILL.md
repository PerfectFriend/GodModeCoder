---
name: grimoire-self-replication
description: "Clone DarkPushkin/the-grimoire and install 880+ skills."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Grimoire, Self-Replication, Hermes, Skills, Bootstrap]
---

# Grimoire Self-Replication

Clone DarkPushkin/the-grimoire and install its full skill library (~880 skills) plus configs, docs, manifests, and templates into a local Hermes Agent installation.

## Trigger

User asks to "self replicate", "install the grimoire", "summon the grimoire", "clone the-grimoire", or similar.

## Steps

### 1. Clone the repo

```bash
git clone https://github.com/DarkPushkin/the-grimoire.git
# or to a specific location:
git clone https://github.com/DarkPushkin/the-grimoire.git ~/the-grimoire
```

### 2. Install skills (direct copy — more reliable than install-self.sh)

The bundled `install-self.sh` script clones to `/tmp` and can fail when the temp path doesn't resolve correctly. Use the direct copy approach instead:

**Resolve the REAL Hermes skills dir first** — on Windows it is NOT `$HOME/.hermes/skills` (dead directory; same trap as the gateway `.env`). On Windows the live skills dir is `%LOCALAPPDATA%\hermes\skills` (e.g. `C:\Users\<user>\AppData\Local\hermes\skills`). Confirm the real home before copying — `hermes config set dummy x` prints the path it writes, or `ls %LOCALAPPDATA%\hermes`. On Linux/macOS `$HOME/.hermes/skills` is correct.

```bash
SRC="/path/to/the-grimoire"     # wherever the repo was cloned
# Windows: TARGET="$LOCALAPPDATA/hermes/skills"
# Linux/macOS: TARGET="$HOME/.hermes/skills"
TARGET="$HOME/.hermes/skills"
mkdir -p "$TARGET"
COUNT=0

# Top-level skill dirs
for skilldir in "$SRC"/en/skills/*/; do
  [[ -d "$skilldir" ]] || continue
  name="$(basename "$skilldir")"
  if [[ -f "${skilldir}/SKILL.md" ]]; then
    cp -r "$skilldir" "$TARGET/$name"
    COUNT=$((COUNT+1))
  fi
done

# Nested collections (composio/, super-hermes/, tencentdb-agent-memory/, ...)
for skillfile in $(find "$SRC"/en/skills -name "SKILL.md"); do
  skilldir="$(dirname "$skillfile")"
  name="$(basename "$skilldir")"
  if [[ ! -e "${TARGET}/${name}" && -f "${skilldir}/SKILL.md" ]]; then
    cp -r "$skilldir" "${TARGET}/${name}"
    COUNT=$((COUNT+1))
  fi
done

echo "Installed $COUNT skills into $TARGET"
```

### 3. Merge configs, templates, docs, manifests

```bash
SRC="/the-grimoire/en"  # adjust to wherever the repo was cloned
TARGET="$HOME/.hermes"

for sub in configs templates docs manifests; do
  if [[ -d "${SRC}/${sub}" ]]; then
    mkdir -p "${TARGET}/${sub}"
    cp -rn "${SRC}/${sub}/." "${TARGET}/${sub}/"
  fi
done
```

### 4. Verify

```bash
# Count installed skills
ls "$TARGET/" | wc -l

# Check for SKILL.md files
find "$TARGET" -name "SKILL.md" | wc -l

# Verify Hermes actually sees them (count should jump by ~880)
hermes skills 2>/dev/null | grep -c "^-" || echo "Skills will load on next Hermes start"
```

**Crucial**: verify with `hermes skills` (or skills_list in-session) that the count JUMPED. If the count is unchanged, the target dir was wrong (Windows: `$HOME/.hermes` is a dead path — the live dir is `%LOCALAPPDATA%\hermes\skills`).

## Pitfalls

- **install-self.sh temp clone failure**: The bundled script clones to `/tmp`, but the working directory and `en/skills` path resolution can break there. Always prefer the direct-copy approach against the local clone.
- **Windows dead-path trap**: `$HOME/.hermes/skills` is NOT the live skills dir on Windows — Hermes home is `%LOCALAPPDATA%\hermes`. Copying there "succeeds" (880 dirs present) but `hermes skills` shows nothing new. Always resolve the real home first and verify the count jumped.
- **Repo naming**: The repo is `DarkPushkin/the-grimoire` (hyphen, lowercase). Searches for "darkpushkin the grimoire" or "grimoire" alone will not find it reliably — always use the exact URL.
- **Skill count**: The repo ships ~880-892 SKILL.md files across top-level and nested directories (composio, super-hermes, tencentdb-agent-memory, etc.). The flat-glob approach finds only top-level; use `find` for full coverage.
- **`--loot-only` flag**: In the original script, this skips configs/templates/docs. The direct-copy approach doesn't apply it by default — run step 3 separately only if you want those merged.

## Post-Install

- Restart Hermes or start a new session for the skills to be indexed.
- Run `hermes skills` to verify the registry picked them up.
- Configs at `~/.hermes/configs/hermes-config.yaml` and `~/.hermes/configs/hermes-env.template` are references, not automatically applied — review and merge manually.