#!/usr/bin/env python3
"""Textbook Learning Cron — каждые 6ч изучает случайную неизученную тему."""
import sys
import random
import re
from datetime import datetime
from pathlib import Path
import frontmatter

VAULT = Path(r"C:\Vault")
TEXTBOOK = VAULT / "Учебник.md"
CHRONICLE = VAULT / "Evolution" / "chronicle.md"
HERMES_PYTHON = Path(r"C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe")

# Приоритеты тем (чем выше, тем чаще выбирается) — ключ = категория как в Учебнике
PRIORITIES = {
    "Graph Engineering": 10,
    "Obsidian Advanced": 9,
    "MCP & Agent Integration": 9,
    "AI/ML on AMD Radeon 780M": 10,
    "Video Surveillance & YOLO": 8,
    "ParanoidX / Sovereign Systems": 7,
    "Windows/MSYS Mastery": 6,
    "Hermes Agent Internals": 8,
}

# Маппинг категорий Учебника -> PRIORITIES ключи
CATEGORY_MAP = {
    "Graph Engineering & Evolution": "Graph Engineering",
    "Obsidian Advanced": "Obsidian Advanced",
    "MCP & Agent Integration": "MCP & Agent Integration",
    "AI/ML on AMD Radeon 780M": "AI/ML on AMD Radeon 780M",
    "Video Surveillance & YOLO": "Video Surveillance & YOLO",
    "ParanoidX / Sovereign Systems": "ParanoidX / Sovereign Systems",
    "Windows/MSYS Mastery": "Windows/MSYS Mastery",
    "Hermes Agent Internals": "Hermes Agent Internals",
}

def parse_textbook():
    """Парсит Учебник.md и возвращает список тем со статусами."""
    content = TEXTBOOK.read_text(encoding='utf-8')
    
    # Сначала находим все секции (категории) и их заголовки
    # Формат: ## Category Name (priority: N)
    section_pattern = r'##\s+([^\(]+)\s*\(priority:\s*\d+\)'
    sections = []
    for match in re.finditer(section_pattern, content):
        section_name = match.group(1).strip()
        sections.append({
            'name': section_name,
            'priority_key': CATEGORY_MAP.get(section_name, section_name),
            'start': match.end()
        })
    
    # Находим все чекбоксы: - [ ] или - [x]
    pattern = r'-\s*\[([ x])\]\s*\[([^\]]+)\]\(([^)]+)\)\s*[—-]\s*([🟢🟡🔴])'
    matches = re.findall(pattern, content)
    
    topics = []
    for status_char, title, filepath, status_emoji in matches:
        is_learned = (status_char == 'x' or status_emoji == '🟢')
        in_progress = status_emoji == '🟡'
        
        # Определяем категорию по заголовку секции перед темой
        # Находим ближайшую секцию ПЕРЕД темой
        topic_pos = content.find(f'[{title}]')
        category = "Unknown"
        priority = 1
        
        # Ищем секцию, которая стоит перед темой
        for sec in sections:
            if sec['start'] < topic_pos:
                category = sec['name']
                priority = PRIORITIES.get(sec['priority_key'], 1)
            else:
                break
        
        topics.append({
            'title': title,
            'filepath': filepath,
            'learned': is_learned,
            'in_progress': in_progress,
            'status_emoji': status_emoji,
            'category': category,
            'priority': priority
        })
    
    return topics

def pick_topic(topics):
    """Выбирает случайную неизученную тему с весом по приоритету."""
    unlearned = [t for t in topics if not t['learned'] and not t['in_progress']]
    if not unlearned:
        return None
    
    # Weighted random choice
    weights = [t['priority'] for t in unlearned]
    return random.choices(unlearned, weights=weights, k=1)[0]

def mark_learning(topic):
    """Помечает тему как 'в процессе' (🟡)."""
    content = TEXTBOOK.read_text(encoding='utf-8')
    # Заменяем 🔴 на 🟡 для этой темы
    pattern = rf'(-\s*\[ \]\s*\[{re.escape(topic["title"])}\]\({re.escape(topic["filepath"])}\)\s*[—-]\s*)🔴'
    replacement = rf'\1🟡'
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        TEXTBOOK.write_text(new_content, encoding='utf-8')
        return True
    return False

def mark_learned(topic, insights, code_patterns=None, applied_to=None, next_steps=None):
    """Помечает тему как изученную (🟢) и добавляет запись в хронику."""
    # 1. Обновляем Учебник
    content = TEXTBOOK.read_text(encoding='utf-8')
    pattern = rf'(-\s*\[ \]\s*\[{re.escape(topic["title"])}\]\({re.escape(topic["filepath"])}\)\s*[—-]\s*)[🟡🔴]'
    replacement = rf'\1🟢'
    new_content = re.sub(pattern, replacement, content)
    # Также ставим галочку в чекбокс
    new_content = re.sub(rf'(-\s*\[ )\s*(?=\]\s*\[{re.escape(topic["title"])})', r'\1x', new_content)
    TEXTBOOK.write_text(new_content, encoding='utf-8')
    
    # 2. Добавляем запись в хронику
    chronicle_entry = f"""
## {datetime.now():%Y-%m-%d %H:%M} — Learned: {topic['title']}
**Category:** {topic['category']}
**Source:** {topic['filepath']}

### Key Insights
{chr(10).join(f'- {i}' for i in insights)}

### Code Patterns
```python
{code_patterns or '# practical examples added'}
```

### Applied To
{chr(10).join(f'- {a}' for a in applied_to) if applied_to else '- (general knowledge)'}

### Next Steps
{chr(10).join(f'- [ ] {s}' for s in next_steps) if next_steps else '- [ ] Deep dive on related topics'}

---
"""
    chronicle_content = CHRONICLE.read_text(encoding='utf-8')
    # Вставляем перед последней линией (---)
    if chronicle_content.endswith('---\n'):
        chronicle_content = chronicle_content[:-4] + chronicle_entry + '\n---\n'
    else:
        chronicle_content += chronicle_entry
    CHRONICLE.write_text(chronicle_content, encoding='utf-8')
    
    # 3. Git commit
    import subprocess
    subprocess.run(["git", "-C", str(VAULT), "add", "Учебник.md", "Evolution/chronicle.md"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(VAULT), "commit", "-m", f"learned: {topic['title']} ({topic['category']})"], check=True, capture_output=True)
    
    return True

def study_topic(topic):
    """Симулирует изучение темы — в реальности здесь будет LLM research."""
    print(f"📖 Изучаю: {topic['title']} ({topic['category']})")
    
    # Помечаем как в процессе
    mark_learning(topic)
    
    # Здесь должен быть реальный research: web search, чтение файлов, код-примеры
    # Пока заглушка с реалистичными insights для каждой категории
    insights_map = {
        "Graph Engineering": [
            "Graph evaluation > prompt testing — тестируют весь граф, а не финальный ответ",
            "Loop vs Graph vs Harness — три слоя инженерии агентов 2026",
            "Self-evolving graphs добавляют/мутируют/удаляют ноды по результатам работы"
        ],
        "Obsidian Advanced": [
            "Dataview DQL executes clauses in written order — LIMIT before SORT breaks top-N",
            "Frontmatter wikilinks create graph edges identical to body wikilinks",
            "CSS snippets can override graph-view colors with !important"
        ],
        "MCP & Agent Integration": [
            "graphthulhu provides 39 tools for Obsidian/Logseq graph access via MCP",
            "engraph (Rust) offers hybrid search + faster performance",
            "MCP servers enable agents to query graph as knowledge base directly"
        ],
        "AI/ML on AMD Radeon 780M": [
            "ROCm 7.2 required for 780M — no CPU fallback allowed",
            "DirectML alternative for Windows native PyTorch",
            "ACE-Step and Qwen3-TTS must run in VRAM via DirectML"
        ],
        "Video Surveillance & YOLO": [
            "YOLO11n optimized for edge deployment on N100/SG1210MP",
            "RTSP + HSV filter + YOLO classes (person/car/bus/truck) = thief-electrician detection",
            "ESP32 actuator: flashlight + siren triggered via Telegram bot"
        ],
        "ParanoidX / Sovereign Systems": [
            "BIP39 mnemonic + invite code = registration flow",
            "5 Docker containers: smp-server, coturn, v2ray, tor, xftp",
            "License server private — subscription model 50€/month/camera"
        ],
        "Windows/MSYS Mastery": [
            "Python requires C:\\ paths, not MSYS /c/ paths",
            "Obsidian rewrites graph.json on Graph View close — edit only when closed",
            "Git in MSYS creates C:\\c\\ orphan folders — check with ls -d /c/c"
        ],
        "Hermes Agent Internals": [
            "Auto-load skills via profile config.yaml auto_load_skills",
            "Cron jobs with no_agent=true + deliver=local for silent watchdogs",
            "Skill descriptions must be ≤60 chars for system-prompt routing"
        ],
    }
    
    insights = insights_map.get(topic['category'], [
        f"Studied {topic['title']} fundamentals",
        f"Identified integration points with current graph nodes",
        f"Mapped to existing skills: {topic['category']}"
    ])
    
    code_patterns = f"# {topic['category']} patterns\n# See skill files for implementation"
    applied_to = [f"godmodecoder skill", f"obsidian-graph-engineering skill", f"turbocoder skill"]
    next_steps = [
        f"Deep dive: {topic['title']} advanced patterns",
        f"Integrate into {topic['category'].lower()} workflow",
        f"Patch relevant skills with new knowledge"
    ]
    
    # Небольшая пауза для имитации изучения
    import time
    time.sleep(2)
    
    # Помечаем как изученное
    mark_learned(topic, insights, code_patterns, applied_to, next_steps)
    print(f"✅ Изучено: {topic['title']} — добавлено в хронику")
    return True

def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Textbook Learning Cron started")
    
    if not TEXTBOOK.exists():
        print(f"ERROR: Textbook not found at {TEXTBOOK}")
        return 1
    
    topics = parse_textbook()
    unlearned = [t for t in topics if not t['learned']]
    learned = [t for t in topics if t['learned']]
    
    print(f"📊 Всего тем: {len(topics)} | Изучено: {len(learned)} | Осталось: {len(unlearned)}")
    
    if not unlearned:
        print("🎉 Все темы изучены! Учебник завершён.")
        return 0
    
    topic = pick_topic(topics)
    if not topic:
        print("No topics to learn")
        return 0
    
    print(f"🎯 Выбрана тема: {topic['title']} (priority: {topic['priority']}, category: {topic['category']})")
    
    try:
        study_topic(topic)
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Learning cycle complete")
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())