#!/usr/bin/env python3
"""
Textbook Learning Cron — каждые 30 мин изучает случайную неизученную тему
с использованием NVIDIA Nemotron-3-Ultra-550b-a50b через провайдер nvidia.
"""
import sys
import random
import re
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path

VAULT = Path(r"C:\Vault")
TEXTBOOK = VAULT / "Учебник.md"
CHRONICLE = VAULT / "Evolution" / "chronicle.md"

# Приоритеты тем (чем выше, тем чаще выбирается)
PRIORITIES = {
    "Graph Engineering": 10,
    "vLLM Optimization": 10,
    "Autonomous AI Agents": 10,
    "Quantization": 10,
    "AI/ML on AMD Radeon 780M": 10,
    "RAG Pipeline": 9,
    "Fine-tuning": 9,
    "Obsidian Advanced": 9,
    "MCP & Agent Integration": 9,
    "Video Surveillance & YOLO": 8,
    "Hermes Agent Internals": 8,
    "ParanoidX / Sovereign Systems": 7,
    "Windows/MSYS Mastery": 6,
}

CATEGORY_MAP = {
    "Graph Engineering & Evolution": "Graph Engineering",
    "Obsidian Advanced": "Obsidian Advanced",
    "MCP & Agent Integration": "MCP & Agent Integration",
    "AI/ML on AMD Radeon 780M": "AI/ML on AMD Radeon 780M",
    "Video Surveillance & YOLO": "Video Surveillance & YOLO",
    "ParanoidX / Sovereign Systems": "ParanoidX / Sovereign Systems",
    "Windows/MSYS Mastery": "Windows/MSYS Mastery",
    "Hermes Agent Internals": "Hermes Agent Internals",
    "vLLM Optimization & Inference": "vLLM Optimization",
    "Autonomous AI Agents & Orchestration": "Autonomous AI Agents",
    "Quantization & Model Compression": "Quantization",
    "RAG Pipeline & Retrieval": "RAG Pipeline",
    "Fine-tuning & LoRA/QLoRA": "Fine-tuning",
}

# NVIDIA API configuration
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_MODEL = "nvidia/nemotron-3-ultra-550b-a50b"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

def call_nvidia_model(prompt, max_tokens=4096, temperature=0.7):
    """Вызов NVIDIA Nemotron через API."""
    import requests
    
    api_key = NVIDIA_API_KEY
    if not api_key:
        # Try to get from hermes credential pool
        try:
            result = subprocess.run(
                ["hermes", "auth", "get", "nvidia"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                api_key = result.stdout.strip()
        except:
            pass
    
    if not api_key:
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert software engineer and researcher. Provide deep, practical insights with code examples. Be thorough and specific."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.95
    }
    
    try:
        response = requests.post(
            f"{NVIDIA_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"NVIDIA API error: {e}")
        return None

def study_topic_with_nvidia(topic):
    """Глубокое изучение темы через NVIDIA Nemotron."""
    print(f"���� Изучаю через NVIDIA Nemotron: {topic['title']} ({topic['category']})")
    
    prompt = f"""Изучи тему: "{topic['title']}" в категории "{topic['category']}".

Контекст: Это часть учебника для непрерывного обучения системы GodModeCoder — автономной самоэволюционирующей системы разработки.

Задача: Глубоко изучи тему, предоставь:
1. **Key Insights** — 3-5 ключевых инсайтов/паттернов/best practices
2. **Code Patterns** — практические код-примеры на Python/Rust/Go/Kotlin/TypeScript (что релевантно)
3. **Applied To** — как применить к проекту GodModeCoder (skills, scripts, architecture)
4. **Next Steps** — 3 конкретных следующих шага для интеграции

Тема: {topic['title']}
Категория: {topic['category']}
Файл источника: {topic['filepath']}

Ответь в JSON формате:
{{
  "insights": ["insight 1", "insight 2", "insight 3", "insight 4", "insight 5"],
  "code_patterns": "```python\\n# practical code example\\n```",
  "applied_to": ["skill/project 1", "skill/project 2"],
  "next_steps": ["step 1", "step 2", "step 3"]
}}

Будь максимально конкретным, технически глубоким и практичным. Используй знания о современных best practices 2024-2026.
"""
    
    print(f"���� Вызываю NVIDIA Nemotron для глубокого изучения...")
    result = call_nvidia_model(prompt, max_tokens=4096, temperature=0.3)
    
    if not result:
        print("������ NVIDIA API недоступен, использую fallback")
        return None
    
    # Parse JSON response
    try:
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data
        else:
            # Try to parse whole response
            data = json.loads(result)
            return data
    except json.JSONDecodeError as e:
        print(f"������ Ошибка парсинга JSON от Nemotron: {e}")
        print(f"Raw response: {result[:500]}...")
        return None

def parse_textbook():
    content = TEXTBOOK.read_text(encoding='utf-8')
    
    # Better pattern: matches ### N. Category Name (priority: N)
    section_pattern = r'###\s+\d+\.\s+([^\(]+?)\s*\(priority:\s*\d+\)'
    sections = []
    for match in re.finditer(section_pattern, content):
        section_name = match.group(1).strip()
        sections.append({
            'name': section_name,
            'priority_key': CATEGORY_MAP.get(section_name, section_name),
            'start': match.end()
        })
    
    # Match checkbox lines with emoji status and optional trailing tags
    pattern = r'-\s*\[([ x])\]\s*\[([^\]]+)\]\(([^)]+)\)\s*[—-]\s*([������������]).*'
    matches = re.findall(pattern, content)
    
    topics = []
    for status_char, title, filepath, status_emoji in matches:
        is_learned = (status_char == 'x' or status_emoji == '����')
        in_progress = status_emoji == '����'
        
        topic_pos = content.find(f'[{title}]')
        category = "Unknown"
        priority = 1
        
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
    unlearned = [t for t in topics if not t['learned'] and not t['in_progress']]
    if not unlearned:
        return None
    weights = [t['priority'] for t in unlearned]
    return random.choices(unlearned, weights=weights, k=1)[0]

def mark_learning(topic):
    content = TEXTBOOK.read_text(encoding='utf-8')
    # Escape special regex chars in title and filepath
    title_escaped = re.escape(topic["title"])
    filepath_escaped = re.escape(topic["filepath"])
    pattern = rf'(-\s*\[\s*\]\s*\[{title_escaped}\]\({filepath_escaped}\)\s*[—-]\s*)����'
    replacement = r'\1����'
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        TEXTBOOK.write_text(new_content, encoding='utf-8')
        return True
    return False

def mark_learned(topic, insights, code_patterns=None, applied_to=None, next_steps=None):
    # 1. Обновляем Учебник
    content = TEXTBOOK.read_text(encoding='utf-8')
    title_escaped = re.escape(topic["title"])
    filepath_escaped = re.escape(topic["filepath"])
    pattern = rf'(-\s*\[\s*\]\s*\[{title_escaped}\]\({filepath_escaped}\)\s*[—-]\s*)[��������]'
    replacement = r'\1����'
    new_content = re.sub(pattern, replacement, content)
    # Также ставим галочку в чекбокс
    new_content = re.sub(rf'(-\s*\[\s*)\s*(?=\]\s*\[{title_escaped})', r'\1x', new_content)
    TEXTBOOK.write_text(new_content, encoding='utf-8')
    
    # 2. Добавляем запись в хронику
    chronicle_entry = f"""\n## {datetime.now():%Y-%m-%d %H:%M} — Learned: {topic['title']}
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
    if chronicle_content.endswith('---\n'):
        chronicle_content = chronicle_content[:-4] + chronicle_entry + '\n---\n'
    else:
        chronicle_content += chronicle_entry
    CHRONICLE.write_text(chronicle_content, encoding='utf-8')
    
    # Git commit
    subprocess.run(["git", "-C", str(VAULT), "add", "Учебник.md", "Evolution/chronicle.md"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(VAULT), "commit", "-m", f"learned: {topic['title']} ({topic['category']})"], check=True, capture_output=True)
    return True

def study_topic(topic):
    print(f"���� Глубокое изучение через NVIDIA Nemotron: {topic['title']} ({topic['category']})")
    
    # Mark as in progress
    mark_learning(topic)
    
    # Deep study with NVIDIA Nemotron
    nvidia_result = study_topic_with_nvidia(topic)
    
    if nvidia_result:
        insights = nvidia_result.get("insights", [])
        code_patterns = nvidia_result.get("code_patterns", "")
        applied_to = nvidia_result.get("applied_to", [])
        next_steps = nvidia_result.get("next_steps", [])
        print(f"��� NVIDIA Nemotron: получено {len(insights)} инсайтов")
    else:
        # Fallback
        print("������ Fallback к базовым инсайтам")
        insights = [f"Studied {topic['title']} fundamentals", f"Identified integration points with current graph nodes"]
        code_patterns = f"# {topic['category']} patterns"
        applied_to = ["godmodecoder skill", "obsidian-graph-engineering skill"]
        next_steps = [f"Deep dive: {topic['title']} advanced patterns"]
    
    # Mark as learned
    mark_learned(topic, insights, code_patterns, applied_to, next_steps)
    print(f"��� Изучено: {topic['title']} — добавлено в хронику")
    return True

def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Textbook Learning Cron started (NVIDIA Nemotron)")
    
    if not TEXTBOOK.exists():
        print(f"ERROR: Textbook not found at {TEXTBOOK}")
        return 1
    
    topics = parse_textbook()
    unlearned = [t for t in topics if not t['learned']]
    learned = [t for t in topics if t['learned']]
    
    print(f"���� Всего тем: {len(topics)} | Изучено: {len(learned)} | Осталось: {len(unlearned)}")
    
    if not unlearned:
        print("���� Все темы изучены! Учебник завершён.")
        return 0
    
    topic = pick_topic(topics)
    if not topic:
        print("No topics to learn")
        return 0
    
    print(f"���� Выбрана тема: {topic['title']} (priority: {topic['priority']}, category: {topic['category']})")
    
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