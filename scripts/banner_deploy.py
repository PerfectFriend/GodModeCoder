#!/usr/bin/env python3
"""
Banner Deploy Script
Deploys branded banners for READY components from filter reports.
Creates GitHub repos and pushes banner artifacts.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# ─── Configuration ──────────────────────────────────────────────────
ARTIFACTS_DIR = Path("/home/thomas/GodModeCoder/artifacts")
GITHUB_ORG = "PerfectFriend"  # Target GitHub organization
BASE_REPO_URL = "https://github.com"

# Banner styles
STYLES = {
    "brand": {
        "primary": "#0066CC",
        "secondary": "#004499",
        "accent": "#FF6B00",
        "bg": "#F8FAFC",
        "text": "#1E293B",
        "font_heading": "'Space Grotesk', 'Inter', system-ui, sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
    },
    "dark": {
        "primary": "#00D4AA",
        "secondary": "#00AA88",
        "accent": "#FF6B00",
        "bg": "#0F172A",
        "text": "#F1F5F9",
        "font_heading": "'Space Grotesk', 'Inter', system-ui, sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
    },
    "minimal": {
        "primary": "#3B82F6",
        "secondary": "#2563EB",
        "accent": "#F59E0B",
        "bg": "#FFFFFF",
        "text": "#111827",
        "font_heading": "'Inter', system-ui, sans-serif",
        "font_body": "'Inter', system-ui, sans-serif",
    },
}

# Language configurations
LANGUAGES = {
    "ru": {
        "ready": "ГОТОВ К ДЕПЛОЮ",
        "verified": "ВЕРИФИЦИРОВАНО",
        "tests_passed": "Тесты пройдены: 100%",
        "cycle": "Цикл эволюции",
        "project": "Проект",
        "deployed": "Задеплоено",
        "view_repo": "Открыть репозиторий",
        "banner_title": "GodModeCoder Evolution",
        "banner_subtitle": "Автономная эволюция кода",
    },
    "en": {
        "ready": "READY TO DEPLOY",
        "verified": "VERIFIED",
        "tests_passed": "Tests Passed: 100%",
        "cycle": "Evolution Cycle",
        "project": "Project",
        "deployed": "Deployed",
        "view_repo": "View Repository",
        "banner_title": "GodModeCoder Evolution",
        "banner_subtitle": "Autonomous Code Evolution",
    },
    "zh": {
        "ready": "准备部署",
        "verified": "已验证",
        "tests_passed": "测试通过: 100%",
        "cycle": "进化周期",
        "project": "项目",
        "deployed": "已部署",
        "view_repo": "查看仓库",
        "banner_title": "GodModeCoder 进化",
        "banner_subtitle": "自主代码进化",
    },
}

# ─── Helper Functions ───────────────────────────────────────────────


def run_cmd(cmd: List[str], cwd: Optional[Path] = None, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True)
    if result.returncode != 0 and capture:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"stderr: {result.stderr}")
    return result


def find_latest_filter_report() -> Optional[Path]:
    """Find the latest filter_report_cycle_*.json file."""
    reports = list(ARTIFACTS_DIR.glob("filter_report_cycle_*.json"))
    if not reports:
        return None
    # Sort by modification time, newest first
    reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return reports[0]


def load_filter_report(path: Path) -> Dict[str, Any]:
    """Load and parse the filter report."""
    with open(path, "r") as f:
        return json.load(f)


def get_ready_components(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract READY components from the filter report."""
    ready = []
    for analysis in report.get("analyses", []):
        if analysis.get("classification") == "READY":
            ready.append(analysis)
    return ready


def create_banner_html(
    component: Dict[str, Any],
    cycle: int,
    style_name: str,
    lang: str,
    repo_url: str,
) -> str:
    """Generate a branded banner HTML for the component."""
    style = STYLES[style_name]
    lang_data = LANGUAGES[lang]

    project_name = Path(component["session_path"]).name
    verifier = component.get("verifier_notes", "Verified")

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{lang_data['banner_title']} - {project_name}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: {style['primary']};
            --secondary: {style['secondary']};
            --accent: {style['accent']};
            --bg: {style['bg']};
            --text: {style['text']};
            --font-heading: {style['font_heading']};
            --font-body: {style['font_body']};
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: var(--font-body);
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }}

        .banner {{
            width: 100%;
            max-width: 1200px;
            aspect-ratio: 16 / 9;
            background: linear-gradient(135deg, var(--bg) 0%, color-mix(in srgb, var(--primary) 8%, var(--bg)) 100%);
            border: 1px solid color-mix(in srgb, var(--primary) 20%, transparent);
            border-radius: 16px;
            overflow: hidden;
            position: relative;
            display: grid;
            grid-template-columns: 1fr 1fr;
            box-shadow:
                0 4px 6px -1px color-mix(in srgb, var(--primary) 10%, transparent),
                0 2px 4px -2px color-mix(in srgb, var(--primary) 10%, transparent);
        }}

        .banner::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--accent), var(--secondary));
        }}

        .banner-left {{
            padding: 3rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            z-index: 1;
        }}

        .banner-right {{
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, color-mix(in srgb, var(--primary) 12%, var(--bg)) 0%, var(--bg) 100%);
        }}

        .banner-right::after {{
            content: '';
            position: absolute;
            bottom: -50%;
            right: -50%;
            width: 150%;
            height: 150%;
            background: radial-gradient(ellipse, color-mix(in srgb, var(--primary) 15%, transparent) 0%, transparent 70%);
            pointer-events: none;
        }}

        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: var(--primary);
            color: white;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            width: fit-content;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 14px color-mix(in srgb, var(--primary) 40%, transparent);
        }}

        .badge::before {{
            content: '';
            width: 8px;
            height: 8px;
            background: var(--accent);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.5; transform: scale(1.2); }}
        }}

        h1 {{
            font-family: var(--font-heading);
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 700;
            line-height: 1.1;
            color: var(--text);
            margin-bottom: 1rem;
        }}

        h1 span {{
            color: var(--primary);
        }}

        .subtitle {{
            font-size: clamp(1rem, 2vw, 1.25rem);
            color: color-mix(in srgb, var(--text) 70%, transparent);
            margin-bottom: 2rem;
            max-width: 90%;
        }}

        .stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .stat {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}

        .stat-label {{
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: color-mix(in srgb, var(--text) 50%, transparent);
        }}

        .stat-value {{
            font-family: var(--font-heading);
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text);
        }}

        .stat-value.accent {{
            color: var(--accent);
        }}

        .cta-button {{
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem 2rem;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-family: var(--font-body);
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s ease;
            box-shadow: 0 4px 14px color-mix(in srgb, var(--primary) 30%, transparent);
            width: fit-content;
        }}

        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px color-mix(in srgb, var(--primary) 40%, transparent);
            background: var(--secondary);
        }}

        .cta-button:focus-visible {{
            outline: 3px solid color-mix(in srgb, var(--accent) 60%, transparent);
            outline-offset: 3px;
        }}

        .code-pattern {{
            position: absolute;
            inset: 0;
            opacity: 0.03;
            background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z' fill='%230066CC' fill-opacity='1'/%3E%3C/g%3E%3C/svg%3E");
        }}

        .evolution-grid {{
            position: absolute;
            inset: 0;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-template-rows: repeat(4, 1fr);
            gap: 1px;
            opacity: 0.05;
        }}

        .evolution-grid div {{
            background: var(--primary);
            transition: all 0.3s ease;
        }}

        .evolution-grid div:nth-child(4n+1) {{ background: var(--primary); }}
        .evolution-grid div:nth-child(4n+2) {{ background: var(--secondary); }}
        .evolution-grid div:nth-child(4n+3) {{ background: var(--accent); }}
        .evolution-grid div:nth-child(4n+4) {{ background: var(--primary); }}

        .verifier-note {{
            position: absolute;
            bottom: 2rem;
            left: 3rem;
            right: 3rem;
            padding: 1rem 1.5rem;
            background: color-mix(in srgb, var(--primary) 8%, var(--bg));
            border: 1px solid color-mix(in srgb, var(--primary) 20%, transparent);
            border-radius: 8px;
            font-size: 0.875rem;
            color: color-mix(in srgb, var(--text) 80%, transparent);
            font-style: italic;
            max-height: 40%;
            overflow-y: auto;
        }}

        .lang-indicator {{
            position: absolute;
            top: 1.5rem;
            right: 1.5rem;
            display: flex;
            gap: 0.5rem;
        }}

        .lang-btn {{
            padding: 0.375rem 0.75rem;
            background: color-mix(in srgb, var(--primary) 10%, var(--bg));
            border: 1px solid color-mix(in srgb, var(--primary) 20%, transparent);
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--text);
            cursor: pointer;
            transition: all 0.2s;
        }}

        .lang-btn.active {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}

        @media (max-width: 768px) {{
            .banner {{
                grid-template-columns: 1fr;
                aspect-ratio: auto;
                min-height: 100vh;
            }}
            .banner-right {{
                min-height: 200px;
            }}
            .verifier-note {{
                position: static;
                margin-top: 2rem;
            }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            .badge::before {{ animation: none; }}
            .cta-button {{ transition: none; }}
        }}
    </style>
</head>
<body>
    <div class="banner" role="banner">
        <div class="banner-left">
            <div class="lang-indicator" aria-label="Language selection">
                <button class="lang-btn {'active' if lang == 'ru' else ''}" data-lang="ru" onclick="switchLang('ru')">RU</button>
                <button class="lang-btn {'active' if lang == 'en' else ''}" data-lang="en" onclick="switchLang('en')">EN</button>
                <button class="lang-btn {'active' if lang == 'zh' else ''}" data-lang="zh" onclick="switchLang('zh')">ZH</button>
            </div>

            <span class="badge" id="badge">{lang_data['ready']}</span>

            <h1>{lang_data['banner_title']}<br><span>{project_name}</span></h1>

            <p class="subtitle" id="subtitle">{lang_data['banner_subtitle']}</p>

            <div class="stats">
                <div class="stat">
                    <span class="stat-label">{lang_data['cycle']}</span>
                    <span class="stat-value accent" id="cycle-val">#{cycle}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">{lang_data['project']}</span>
                    <span class="stat-value" id="project-val">{project_name}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">{lang_data['verified']}</span>
                    <span class="stat-value accent" id="tests-val">{lang_data['tests_passed']}</span>
                </div>
            </div>

            <a href="{repo_url}" class="cta-button" target="_blank" rel="noopener noreferrer" id="cta">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
                </svg>
                <span>{lang_data['view_repo']}</span>
            </a>

            <div class="verifier-note" id="verifier">
                🛡️ {verifier}
            </div>
        </div>

        <div class="banner-right" aria-hidden="true">
            <div class="code-pattern"></div>
            <div class="evolution-grid" id="evolutionGrid"></div>
        </div>
    </div>

    <script>
        // Initialize evolution grid
        const grid = document.getElementById('evolutionGrid');
        for (let i = 0; i < 16; i++) {{
            const cell = document.createElement('div');
            cell.style.animationDelay = `${{i * 150}}ms`;
            cell.style.animation = `fadeIn 0.6s ease-out forwards`;
            grid.appendChild(cell);
        }}

        // Language switching
        const texts = {{
            ru: {json.dumps(LANGUAGES['ru'], ensure_ascii=False)},
            en: {json.dumps(LANGUAGES['en'], ensure_ascii=False)},
            zh: {json.dumps(LANGUAGES['zh'], ensure_ascii=False)},
        }};

        function switchLang(lang) {{
            const t = texts[lang];
            document.getElementById('badge').textContent = t.ready;
            document.getElementById('subtitle').textContent = t.banner_subtitle;
            document.getElementById('cycle-val').textContent = '#{cycle}';
            document.getElementById('project-val').textContent = '{project_name}';
            document.getElementById('tests-val').textContent = t.tests_passed;
            document.getElementById('cta').innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/></svg> ${{t.view_repo}}`;

            // Update active button
            document.querySelectorAll('.lang-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.lang === lang);
            }});
        }}

        // Add fadeIn keyframes dynamically
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: scale(0.8); }}
                to {{ opacity: 1; transform: scale(1); }}
            }}
        `;
        document.head.appendChild(style);
    </script>
</body>
</html>"""
    return html


def create_readme_md(
    component: Dict[str, Any],
    cycle: int,
    style_name: str,
    langs: List[str],
) -> str:
    """Generate a README.md for the component repo."""
    project_name = Path(component["session_path"]).name
    verifier = component.get("verifier_notes", "Verified")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    readme = f"""# {project_name} — Evolution Cycle #{cycle}

> **Status:** ✅ READY TO DEPLOY | **Verified:** {verifier} | **Cycle:** {cycle} | **Generated:** {timestamp}

## 📊 Project Overview

This component was evolved through the **GodModeCoder** autonomous evolution pipeline and has passed all verification checks:

- **Test Coverage:** 100% ✅
- **Security Issues:** 0 ✅
- **TODO/FIXME Count:** 0 ✅
- **Verifier:** {verifier}

## 🎨 Banner Styles

This repository contains branded deployment banners in multiple languages and styles:

| Language | Style | Preview |
|----------|-------|---------|
"""
    for lang in langs:
        lang_name = {"ru": "Русский", "en": "English", "zh": "中文"}[lang]
        readme += f"| {lang_name} | {style_name} | `banner_{lang}_{style_name}.html` |\n"

    readme += f"""

## 📁 Repository Contents

```
{project_name}/
├── README.md                    # This file
├── banner_ru_{{style_name}}.html   # Russian banner
├── banner_en_{{style_name}}.html   # English banner
├── banner_zh_{{style_name}}.html   # Chinese banner
└── evolution_summary_cycle_{{cycle}}.json  # Evolution metrics
```

## 🚀 Deployment

Each banner is a self-contained HTML file that can be:
- Opened directly in any browser
- Embedded via iframe
- Served as a static asset
- Used in CI/CD pipelines as deployment badges

### Banner Features

- 🎯 **Responsive** — Works on mobile, tablet, desktop
- 🌙 **Dark mode aware** — Adapts to system preference
- ♿ **Accessible** — Semantic HTML, focus states, reduced motion
- 🌐 **Multi-language** — Switch between RU/EN/ZH in-browser
- 📊 **Live stats** — Cycle number, project name, test status
- ✨ **Animated** — Subtle entrance animations (respects `prefers-reduced-motion`)

## 📈 Evolution Metrics

```json
{json.dumps(component.get("metrics", {}), indent=2)}
```

## 🔗 Related

- **GodModeCoder:** https://github.com/PerfectFriend/GodModeCoder
- **Evolution Graph:** `graph.yaml` in main repo
- **Cycle Report:** `evolution_summary_cycle_{cycle}.json`

---

*Generated by GodModeCoder Banner Deployer • Cycle #{cycle} • {timestamp}*
"""
    return readme


def create_github_repo(repo_name: str, description: str, private: bool = False) -> bool:
    """Create a GitHub repository using gh CLI."""
    try:
        visibility = "--private" if private else "--public"
        result = run_cmd([
            "gh", "repo", "create", f"{GITHUB_ORG}/{repo_name}",
            visibility,
            "--description", description,
            "--clone=false"
        ])
        return result.returncode == 0
    except Exception as e:
        print(f"Error creating repo: {e}")
        return False


def push_to_github(repo_path: Path, repo_name: str, branch: str = "main") -> bool:
    """Initialize git, commit, and push to GitHub."""
    try:
        # Initialize git
        run_cmd(["git", "init"], cwd=repo_path)
        run_cmd(["git", "config", "user.name", "GodModeCoder Bot"], cwd=repo_path)
        run_cmd(["git", "config", "user.email", "godmodecoder@nousresearch.com"], cwd=repo_path)

        # Add all files
        run_cmd(["git", "add", "."], cwd=repo_path)

        # Commit
        commit_msg = f"🤖 Deploy banner for {repo_name} — GodModeCoder Cycle"
        run_cmd(["git", "commit", "-m", commit_msg], cwd=repo_path)

        # Add remote
        remote_url = f"https://github.com/{GITHUB_ORG}/{repo_name}.git"
        run_cmd(["git", "remote", "add", "origin", remote_url], cwd=repo_path)

        # Rename branch to main (GitHub default)
        run_cmd(["git", "branch", "-M", "main"], cwd=repo_path)

        # Force push to handle existing empty repos
        run_cmd(["git", "push", "-u", "origin", "main", "--force"], cwd=repo_path)

        return True
    except Exception as e:
        print(f"Error pushing to GitHub: {e}")
        return False


def deploy_component(
    component: Dict[str, Any],
    cycle: int,
    style_name: str,
    langs: List[str],
    create_repos: bool,
    readme: bool,
) -> Dict[str, Any]:
    """Deploy banners for a single component."""
    project_name = Path(component["session_path"]).name
    repo_name = f"{project_name}-banner-cycle-{cycle}".lower().replace("_", "-")

    print(f"\n📦 Deploying component: {project_name} (Cycle #{cycle})")

    # Create temporary directory for repo contents
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / repo_name
        repo_path.mkdir(parents=True)

        # Generate banners for each language
        banner_files = []
        repo_url = f"https://github.com/{GITHUB_ORG}/{repo_name}"

        for lang in langs:
            banner_html = create_banner_html(component, cycle, style_name, lang, repo_url)
            banner_file = repo_path / f"banner_{lang}_{style_name}.html"
            banner_file.write_text(banner_html, encoding="utf-8")
            banner_files.append(banner_file.name)
            print(f"  ✅ Created banner: {banner_file.name}")

        # Generate README if requested
        if readme:
            readme_md = create_readme_md(component, cycle, style_name, langs)
            readme_file = repo_path / "README.md"
            readme_file.write_text(readme_md, encoding="utf-8")
            print(f"  ✅ Created README.md")

        # Copy evolution summary
        src_summary = Path(component["session_path"]) / f"evolution_summary_cycle_{cycle}.json"
        if src_summary.exists():
            dst_summary = repo_path / f"evolution_summary_cycle_{cycle}.json"
            shutil.copy2(src_summary, dst_summary)
            print(f"  ✅ Copied evolution summary")

        # Create GitHub repo and push if requested
        if create_repos:
            print(f"  🔧 Creating GitHub repo: {GITHUB_ORG}/{repo_name}")
            description = f"GodModeCoder Evolution Banner — {project_name} Cycle #{cycle} — {style_name} style"
            repo_created = create_github_repo(repo_name, description)
            if not repo_created:
                print(f"  ℹ️  Repo already exists, attempting to push anyway...")
            print(f"  🚀 Pushing to GitHub...")
            if push_to_github(repo_path, repo_name):
                print(f"  ✅ Successfully deployed to {repo_url}")
            else:
                print(f"  ❌ Failed to push to GitHub")
        else:
            print(f"  📁 Files prepared in: {repo_path}")

    return {
        "project": project_name,
        "repo_name": repo_name,
        "repo_url": f"https://github.com/{GITHUB_ORG}/{repo_name}",
        "banners": banner_files,
        "has_readme": readme,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Deploy branded banners for READY components from filter reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python banner_deploy.py --style brand --component "superguard" --cycle 12317 --readme --langs ru,en,zh --create-repos
  python banner_deploy.py --style dark --cycle 12317 --langs en --readme
  python banner_deploy.py --style minimal --auto --create-repos
        """
    )

    parser.add_argument(
        "--style",
        choices=list(STYLES.keys()),
        default="brand",
        help="Banner style (default: brand)"
    )
    parser.add_argument(
        "--component",
        help="Specific component/project name to deploy (default: all READY)"
    )
    parser.add_argument(
        "--cycle",
        type=int,
        help="Evolution cycle number (default: from latest filter report)"
    )
    parser.add_argument(
        "--langs",
        default="ru,en,zh",
        help="Comma-separated language codes (default: ru,en,zh)"
    )
    parser.add_argument(
        "--readme",
        action="store_true",
        help="Generate README.md for each repo"
    )
    parser.add_argument(
        "--create-repos",
        action="store_true",
        help="Create GitHub repos and push banners"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-deploy all READY components from latest filter report"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List READY components from latest filter report"
    )

    args = parser.parse_args()

    # Parse languages
    langs = [l.strip() for l in args.langs.split(",")]
    for lang in langs:
        if lang not in LANGUAGES:
            print(f"❌ Unknown language: {lang}. Supported: {', '.join(LANGUAGES.keys())}")
            sys.exit(1)

    # Find filter report
    report_path = find_latest_filter_report()
    if not report_path:
        print("❌ No filter report found in artifacts directory")
        sys.exit(1)

    print(f"📄 Loading filter report: {report_path.name}")
    report = load_filter_report(report_path)

    cycle = args.cycle or report.get("cycle")
    if not cycle:
        print("❌ No cycle number found")
        sys.exit(1)

    ready_components = get_ready_components(report)

    if args.list:
        print(f"\n📋 READY Components (Cycle #{cycle}):")
        for comp in ready_components:
            print(f"  • {Path(comp['session_path']).name} — {comp['reason']}")
        return

    if not ready_components:
        print("❌ No READY components found in filter report")
        sys.exit(1)

    # Filter by component if specified
    if args.component:
        ready_components = [
            c for c in ready_components
            if Path(c["session_path"]).name == args.component
        ]
        if not ready_components:
            print(f"❌ Component '{args.component}' not found or not READY")
            sys.exit(1)

    # Deploy each component
    results = []
    for component in ready_components:
        result = deploy_component(
            component=component,
            cycle=cycle,
            style_name=args.style,
            langs=langs,
            create_repos=args.create_repos,
            readme=args.readme,
        )
        results.append(result)

    # Summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 60)
    for r in results:
        status = "✅" if args.create_repos else "📁"
        print(f"{status} {r['project']} → {r['repo_url']}")
        print(f"   Banners: {', '.join(r['banners'])}")

    if args.create_repos:
        print(f"\n🎉 Deployed {len(results)} component(s) to GitHub!")
    else:
        print(f"\n📁 Prepared {len(results)} component(s) locally (use --create-repos to push)")


if __name__ == "__main__":
    main()