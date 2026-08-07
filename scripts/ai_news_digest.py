#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI Engineering News Cron — ежедневно в 8:00 ищет новости AI Engineering,
отбирает полезное, классифицирует и добавляет в хронику/навыки."""
import sys
import json
import re
from datetime import datetime
from pathlib import Path
import subprocess

VAULT = Path(r"C:\Vault")
CHRONICLE = VAULT / "Evolution" / "chronicle.md"
NEWS_CACHE = VAULT / ".ai_news_cache.json"

# Источники (RSS/API)
SOURCES = [
    ("HuggingFace Daily Papers", "https://huggingface.co/api/daily_papers"),
    ("Papers with Code Latest", "https://paperswithcode.com/api/v1/papers/?page=1&page_size=20"),
    ("ArXiv AI cs.AI", "http://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=20"),
    ("ArXiv ML cs.LG", "http://export.arxiv.org/api/query?search_query=cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=20"),
    ("ArXiv CL cs.CL", "http://export.arxiv.org/api/query?search_query=cat:cs.CL&sortBy=submittedDate&sortOrder=descending&max_results=20"),
]

# Ключевые слова для фильтрации полезного
USEFUL_KEYWORDS = [
    "agent", "tool use", "function calling", "mcp", "graph rag", "knowledge graph",
    "fine-tuning", "qlora", "lora", "quantization", "gguf", "gptq", "awq",
    "inference optimization", "speculative decoding", "kv cache", "flash attention",
    "long context", "context window", "retrieval", "rerank", "embedding",
    "multimodal", "vision-language", "video understanding", "speech",
    "code generation", "code review", "automated testing", "agentic",
    "llm serving", "vllm", "tgi", "ollama", "llama.cpp", "exllama",
    "moe", "mixture of experts", "sparse", "distillation", "alignment",
    "rlhf", "dpo", "ppo", "constitutional ai", "safety",
    "benchmark", "eval", "mmlu", "gpqa", "humaneval", "mbpp",
    "small language model", "slm", "phi", "gemma", "qwen", "llama",
    "open weights", "open source", "apache 2.0", "mit license",
    "onnx", "tensorrt", "triton", "cuda", "rocm", "directml",
    "edge deployment", "mobile", "wasm", "webgpu",
]

CATEGORIES = {
    "Agent/Tool Use": ["agent", "tool use", "function calling", "mcp", "agentic"],
    "Graph/RAG": ["graph rag", "knowledge graph", "retrieval", "rerank", "embedding"],
    "Fine-tuning/PEFT": ["fine-tuning", "qlora", "lora", "distillation"],
    "Quantization/Inference": ["quantization", "gguf", "gptq", "awq", "speculative decoding", "kv cache", "flash attention", "vllm", "ollama", "llama.cpp"],
    "Long Context/Context Window": ["long context", "context window"],
    "Multimodal": ["multimodal", "vision-language", "video", "speech"],
    "Code Generation/Testing": ["code generation", "code review", "automated testing", "humaneval", "mbpp"],
    "Model Architectures": ["moe", "mixture of experts", "sparse", "small language model", "slm"],
    "Alignment/Safety": ["alignment", "rlhf", "dpo", "ppo", "constitutional ai", "safety"],
    "Benchmarks/Evaluation": ["benchmark", "eval", "mmlu", "gpqa", "humaneval", "mbpp"],
    "Models": ["phi", "gemma", "qwen", "llama", "open weights", "open source"],
    "Deployment/Hardware": ["onnx", "tensorrt", "triton", "cuda", "rocm", "directml", "edge", "mobile", "wasm", "webgpu"],
    "Deployment/Edge": ["edge deployment", "mobile", "wasm", "webgpu"],
}

def load_cache():
    if NEWS_CACHE.exists():
        return json.loads(NEWS_CACHE.read_text(encoding="utf-8"))
    return {"seen_ids": [], "last_run": None}

def save_cache(cache):
    NEWS_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

def classify(title, summary):
    text = (title + " " + summary).lower()
    cats = []
    for cat, keywords in CATEGORIES.items():
        if any(kw in text for kw in keywords):
            cats.append(cat)
    return cats if cats else ["General"]

def is_useful(title, summary):
    text = (title + " " + summary).lower()
    return any(kw in text for kw in USEFUL_KEYWORDS)

def fetch_source(name, url):
    try:
        import urllib.request
        import xml.etree.ElementTree as ET
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        if name.startswith("ArXiv"):
            root = ET.fromstring(data)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = []
            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns).text.strip()
                summary = entry.find("atom:summary", ns).text.strip() if entry.find("atom:summary", ns) is not None else ""
                link = entry.find("atom:id", ns).text.strip()
                items.append({"id": link, "title": title, "summary": summary, "url": link, "source": name})
            return items
        else:
            data_json = json.loads(data.decode("utf-8"))
            if name == "HuggingFace Daily Papers":
                items = []
                for p in data_json.get("papers", [])[:20]:
                    items.append({
                        "id": p.get("paper", {}).get("id", ""),
                        "title": p.get("paper", {}).get("title", ""),
                        "summary": p.get("paper", {}).get("summary", ""),
                        "url": f"https://arxiv.org/abs/{p.get('paper', {}).get('id', '')}",
                        "source": name
                    })
                return items
            elif name == "Papers with Code Latest":
                items = []
                for p in data_json.get("results", [])[:20]:
                    items.append({
                        "id": p.get("id", ""),
                        "title": p.get("title", ""),
                        "summary": p.get("abstract", ""),
                        "url": f"https://paperswithcode.com{p.get('url', '')}",
                        "source": name
                    })
                return items
            return []
    except Exception as e:
        print(f"  [{name}] Error: {e}")
        return []

def main():
    cache = load_cache()
    seen = set(cache.get("seen_ids", []))
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] AI Engineering News scan started")
    
    all_items = []
    for name, url in SOURCES:
        items = fetch_source(name, url)
        print(f"  [{name}] {len(items)} items")
        all_items.extend(items)
    
    # Фильтруем: новые, полезные
    new_useful = []
    for item in all_items:
        if item["id"] in seen:
            continue
        if not is_useful(item["title"], item["summary"]):
            continue
        cats = classify(item["title"], item["summary"])
        item["categories"] = cats
        new_useful.append(item)
        seen.add(item["id"])
    
    print(f"  New useful items: {len(new_useful)}")
    
    if not new_useful:
        print("  No new useful AI engineering news today")
        cache["last_run"] = today
        save_cache(cache)
        return 0
    
    # Группируем по категориям
    by_cat = {}
    for item in new_useful:
        for cat in item["categories"]:
            by_cat.setdefault(cat, []).append(item)
    
    # Добавляем в хронику
    chronicle_content = CHRONICLE.read_text(encoding="utf-8")
    entry = f"\n## {datetime.now():%Y-%m-%d %H:%M} — AI Engineering News Digest\n"
    entry += f"**Date:** {today}\n"
    entry += f"**Sources scanned:** {len(SOURCES)} | New useful: {len(new_useful)}\n\n"
    
    for cat, items in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        entry += f"### {cat} ({len(items)} items)\n"
        for item in items[:5]:  # топ-5 в категории
            entry += f"- **{item['title']}** ({item['source']}) — {item['url']}\n"
            if len(item['summary']) > 50:
                entry += f"  > {item['summary'][:200]}...\n"
        if len(items) > 5:
            entry += f"  ... and {len(items)-5} more\n"
        entry += "\n"
    
    entry += "---\n"
    
    if chronicle_content.endswith("---\n"):
        chronicle_content = chronicle_content[:-4] + entry + "\n---\n"
    else:
        chronicle_content += entry
    CHRONICLE.write_text(chronicle_content, encoding="utf-8")
    
    # Обновляем кэш
    cache["seen_ids"] = list(seen)[-5000:]  # храним последние 5000
    cache["last_run"] = today
    save_cache(cache)
    
    # Git commit
    subprocess.run(["git", "-C", str(VAULT), "add", "Evolution/chronicle.md"], capture_output=True)
    subprocess.run(["git", "-C", str(VAULT), "commit", "-m", f"news: AI Engineering digest {today} ({len(new_useful)} items)"], capture_output=True)
    
    print(f"  Added {len(new_useful)} items to chronicle across {len(by_cat)} categories")
    return 0

if __name__ == "__main__":
    sys.exit(main())