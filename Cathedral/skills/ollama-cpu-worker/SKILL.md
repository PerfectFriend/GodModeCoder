---
name: ollama-cpu-worker
description: "Ollama CPU-only worker for code review and testing."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [ollama, cpu, local-llm, background-worker, code-review, testing, qwen3, gemma]
    related_skills: [comfyui, local-ai-stack, turbocoder, godmodecoder]
---

# Ollama CPU Worker — Локальные LLM для фоновых задач

Запуск Ollama на **CPU-only** (без GPU/Vulkan) для фоновых задач: код-ревью, генерация тестов, анализ логов, рефакторинг, документация.

---

## 🎯 Конфигурация для AMD Radeon 780M (Windows)

### Проблема
Ollama по умолчанию пытается использовать Vulkan на AMD iGPU → OOM ошибки:
```
alloc_tensor_range: failed to allocate Vulkan0 buffer of size 1070244864
error loading model: unable to allocate Vulkan0 buffer
```

### Решение — CPU-only конфигурация

```bash
# Переменные окружения (все обязательны!)
set OLLAMA_NUM_GPU=0
set OLLAMA_GPU_LAYERS=0
set OLLAMA_FLASH_ATTENTION=0
set OLLAMA_KV_CACHE_TYPE=f16
set OLLAMA_NO_VULKAN=1
set OLLAMA_CUDA=0
set OLLAMA_ROCM=0
set OLLAMA_METAL=0
set OLLAMA_LOW_VRAM=1
set OLLAMA_NUMA=true
```

### Запуск сервера
```bash
OLLAMA_NUM_GPU=0 OLLAMA_GPU_LAYERS=0 OLLAMA_FLASH_ATTENTION=0 OLLAMA_KV_CACHE_TYPE=f16 OLLAMA_NO_VULKAN=1 OLLAMA_CUDA=0 OLLAMA_ROCM=0 OLLAMA_METAL=0 OLLAMA_LOW_VRAM=1 ollama serve
```

### Проверка
```bash
curl -X POST http://localhost:11434/api/generate -d '{"model": "qwen3:8b", "prompt": "привет", "stream": false, "options": {"num_gpu": 0}}'
```

---

## 📋 Установленные модели

| Модель | Размер | Назначение |
|---|---|---|
| **qwen3:8b** | 5.2 GB | Быстрый код-ревью, генерация тестов, рефакторинг |
| **qwen3:14b** | 9.3 GB | Глубокий анализ архитектуры, сложный рефакторинг |
| **gemma4:12b** | 7.6 GB | Генерация тестов, документация, анализ багов |

---

## 🛠 Ollama Background Worker

### Роли для фоновых задач

```python
ROLES = {
    "code_reviewer": {
        "model": "qwen3:8b",
        "prompt": "Ты — senior code reviewer. Найди 3-5 проблем: безопасность, производительность, чистота кода. Дай исправленный код.",
        "options": {"num_gpu": 0, "num_ctx": 4096, "temperature": 0.1, "num_predict": 500}
    },
    "test_generator": {
        "model": "qwen3:8b",
        "prompt": "Ты — QA engineer. Напиши pytest тесты для данного кода: unit, edge cases, parametrize. Покрытие 90%+.",
        "options": {"num_gpu": 0, "num_ctx": 4096, "temperature": 0.2, "num_predict": 800}
    },
    "refactorer": {
        "model": "qwen3:14b",
        "prompt": "Ты — staff engineer. Рефактор: SOLID, DRY, паттерны, типизация. Сохрани API.",
        "options": {"num_gpu": 0, "num_ctx": 8192, "temperature": 0.1, "num_predict": 1500}
    },
    "bug_analyzer": {
        "model": "gemma4:12b",
        "prompt": "Ты — debugger. Найди root cause, предложи fix, напиши regression test.",
        "options": {"num_gpu": 0, "num_ctx": 4096, "temperature": 0.1, "num_predict": 800}
    },
    "doc_writer": {
        "model": "qwen3:8b",
        "prompt": "Ты — tech writer. Напиши docstring, README, ADR. Язык: русский/английский.",
        "options": {"num_gpu": 0, "num_ctx": 4096, "temperature": 0.3, "num_predict": 600}
    },
    "arch_reviewer": {
        "model": "qwen3:14b",
        "prompt": "Ты — software architect. Оцени: coupling, cohesion, scalability, security. Дай рекомендации.",
        "options": {"num_gpu": 0, "num_ctx": 8192, "temperature": 0.1, "num_predict": 1000}
    }
}
```

### API Client (Python)

```python
import requests

class OllamaWorker:
    def __init__(self, base_url="http://localhost:11434", model="qwen3:8b"):
        self.base_url = base_url
        self.model = model
        self.default_options = {"num_gpu": 0, "num_ctx": 4096}
    
    def generate(self, prompt: str, model: str = None, options: dict = None) -> dict:
        opts = {**self.default_options, **(options or {})}
        payload = {"model": model or self.model, "prompt": prompt, "stream": False, "options": opts}
        resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=300)
        resp.raise_for_status()
        return resp.json()
    
    def code_review(self, code: str) -> str:
        prompt = f"Ты — senior code reviewer. Найди 3-5 проблем: безопасность, производительность, чистота. Дай исправленный код.\n```python\n{code}\n```"
        return self.generate(prompt, options={"num_gpu": 0, "num_ctx": 4096, "temperature": 0.1, "num_predict": 500})["response"]
    
    def generate_tests(self, code: str) -> str:
        prompt = f"Ты — QA engineer. Напиши pytest тесты: unit, edge cases, parametrize. Покрытие 90%+.\n```python\n{code}\n```"
        return self.generate(prompt, options={"num_gpu": 0, "num_ctx": 4096, "temperature": 0.2, "num_predict": 800})["response"]
    
    def refactor(self, code: str) -> str:
        prompt = f"Ты — staff engineer. Рефактор: SOLID, DRY, паттерны, типизация. Сохрани API.\n```python\n{code}\n```"
        return self.generate(prompt, model="qwen3:14b", options={"num_gpu": 0, "num_ctx": 8192, "temperature": 0.1, "num_predict": 1500})["response"]
    
    def analyze_bug(self, code: str, error: str) -> str:
        prompt = f"Ты — debugger. Найди root cause, предложи fix, напиши regression test.\nError: {error}\nCode:\n```python\n{code}\n```"
        return self.generate(prompt, model="gemma4:12b", options={"num_gpu": 0, "num_ctx": 4096, "temperature": 0.1, "num_predict": 800})["response"]

# Usage
worker = OllamaWorker()
print(worker.code_review("async def fetch(db, ids): ..."))
```

---

## ⚡ Cron Jobs (Фоновые задачи)

### Nightly Code Review
```bash
# ~/.config/hermes/cron/nightly_review.py
import subprocess, requests
from pathlib import Path

REPO = Path(r"C:\Users\tomas\the-grimoire")
MODEL = "qwen3:8b"

def review_changed_files():
    diff = subprocess.run(["git", "diff", "HEAD~1"], cwd=REPO, capture_output=True, text=True).stdout
    if not diff.strip(): return
    
    prompt = f"Code review для изменений:\n```diff\n{diff[:8000]}\n```\nНайди: security, performance, breaking changes."
    resp = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen3:8b", "prompt": prompt, "stream": False,
        "options": {"num_gpu": 0, "num_ctx": 4096, "temperature": 0.1, "num_predict": 500}
    }, timeout=180)
    
    report = resp.json()["response"]
    (REPO / "reviews" / f"review_{datetime.now():%Y%m%d_%H%M}.md").write_text(report)

if __name__ == "__main__": review_changed_files()
```

---

## 🔧 Интеграция с GodModeCoder / TurboCoder

### В `hermes-verify-all.py` добавить:
```python
def test_ollama_available():
    return run_test("Ollama CPU Worker", ["curl", "-sf", "http://localhost:11434/api/tags"], expect_exit=0, check_output="models")
```

---

## 📊 Производительность (CPU-only, Ryzen 7 255H)

| Модель | RAM | Скорость (tokens/s) | Качество |
|---|---|---|---|
| qwen3:8b | ~6 GB | 8-12 | Отличное для code review |
| qwen3:14b | ~10 GB | 4-6 | Глубокий анализ |
| gemma4:12b | ~8 GB | 5-7 | Тесты, баг-анализ |

---

## ⚠️ Питфоллы Windows

1. **Ollama сервер должен быть запущен** — `ollama serve` в фоне
2. **CPU-only режим обязателен** — иначе Vulkan OOM на AMD 780M
3. **Модели большие** — 8b=5GB, 14b=9GB, 12b=7GB RAM
4. **Таймауты** — генерация 30-120 сек, ставить `timeout=300` в requests
5. **Порт 11434** — только localhost, не открывать наружу