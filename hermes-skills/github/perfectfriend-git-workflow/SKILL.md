---
name: perfectfriend-git-workflow
description: Push to PerfectFriend GitHub via browser (owner in Chrome).
---

# GitHub Push — PerfectFriend Account

**Trigger**: Push to PerfectFriend GitHub repos (`github.com/PerfectFriend/...`)

**Critical**: Owner logged into Chrome. **Only browser automation works** — SSH/git CLI fails or pushes as wrong user.

---

## Workflow

### 1. Local prep
```bash
cd <repo-dir>
git add .
git commit -m "msg"
git push origin <branch>  # local prep only
```

### 2. Browser verify & merge
```python
browser_navigate("https://github.com/PerfectFriend/<REPO>")
# Check branch, switch if needed
# If main != master: /compare/main...master → Create PR → Merge
# Or Settings → Branches → Switch default to master
```

### 3. Always verify
- `raw.githubusercontent.com/PerfectFriend/<REPO>/main/README.md`
- Check banners, language switcher, content

---

## Key Patterns

### Switch default branch (browser)
Settings → Branches → Default branch → Switch to master

### Merge master into main (browser)
Compare → base: main, compare: master → Create PR → Merge

### Keep banners/assets
- Assets in `assets/` (banner-header.png, banner-footer.png)
- README: `![Alt](assets/banner-header.png)` in `<div align="center">`
- **Top banner** after language switcher, **bottom banner** before license
- Never delete assets folder

---

## Anti-Patterns (DON'T)

❌ `git push origin master` assumes default branch update
❌ SSH push without browser verification
❌ Delete `assets/` or banner images
❌ **Forget banners when rewriting README**
❌ **Forget to update all 3 language READMEs**
❌ Assume `main` == `master` content
❌ Push without `raw.githubusercontent.com` check

---

## Files to Track

```
README.md          # English (default) with language switcher
README.ru.md       # Russian with language switcher
README.es.md       # Spanish with language switcher
assets/
  banner-header.png
  banner-footer.png
```

---

## Known PerfectFriend Repos

| Repo | Default Branch |
|------|----------------|
| AISuperGuard | main |
| the-grimoire | main |
| the-isle | main |
| royal-isle | main |

---

## Remember

> **Owner logged into Chrome = browser automation is the source of truth.**  
> Git CLI is for local prep only. Final verification ALWAYS in browser.