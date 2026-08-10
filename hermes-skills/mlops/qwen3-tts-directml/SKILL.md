---
name: qwen3-tts-directml
description: Use when running Qwen3-TTS on AMD iGPU via torch-directml.
---

# Qwen3-TTS на AMD iGPU через torch-directml

Голосовой клон Qwen3-TTS 1.7B-Base на Radeon 780M (Windows, DirectML). Проверено на Beelink SER9 (Ryzen 7 255, 24 ГБ RAM, UMA=16 ГБ).

## Стенд (venv)

`C:\Users\tomas\tts-dml-env` — torch 2.4.1+cpu, torch-directml 0.2.5, transformers 4.57.3, qwen_tts (скопирован из распакованного PyInstaller Voicebox).

Запуск (ОБЯЗАТЕЛЬНО с очисткой PYTHONPATH, иначе подхватится чужой torch):
```bash
env -u PYTHONPATH -u VIRTUAL_ENV ./tts-dml-env/Scripts/python.exe script.py <ref.wav> <text>
```

Установка torch-directml (в PyPI его НЕТ, только MS-индекс):
```
pip install torch-directml --extra-index-url https://pkgs.dev.azure.com/dnceng/public/_packaging/directml/pypi/simple/
```

## Ключевые шаги запуска

1. Грузить модель **без device_map** (device_map="auto"/{"": dml} включает CUDA-путь → падает). Вместо этого: `from_pretrained()` → `model.to(dml)`.
2. Обёртка `Qwen3TTSModel` фиксирует `self.device` при создании — после `.to(dml)` **обязательно `tts.device = dml`**, иначе входные тензоры остаются на CPU и падает "unbox expects Dml tensor".
3. Для клона голоса: **Base-модель** (не CustomVoice!) + `create_voice_clone_prompt(ref_audio=..., x_vector_only_mode=True)` + `generate_voice_clone(text, language="russian", ...)`.
4. `language="russian"` — НЕ "ru" (иначе "Unsupported language").
5. fp16 НЕ работает: `replication_pad1d not implemented for 'Half'` (Mimi codec) — только fp32.

## Баги torch-directml и фиксы (критично!)

| Баг | Симптом | Фикс |
|---|---|---|
| `torch.inference_mode()` несовместим | "Cannot set version_counter for inference tensor" в conv1d | Заменить все `@torch.inference_mode()` → `@torch.no_grad()` в modeling_qwen3_tts.py и qwen3_tts_tokenizer.py |
| `torch.cat` с пустым тензором shape=(N,0) | UnicodeDecodeError "0xcf in position 0" | Обёртка torch.cat: фильтровать пустые по dim (см. gpu_tts_test.py) |
| `RepetitionPenaltyLogitsProcessor` gather на смешанных device | UnicodeDecodeError | repetition_penalty=1.0 (не добавляется в processor list) |
| device_map | CUDA-индексация при загрузке | грузить на CPU → .to(dml) |
| Два voicebox-server.exe | конфликт порта :8000 | держать один процесс |

## Производительность

- Загрузка модели: ~20-30 с (fp32, 6.8 ГБ)
- Синтез: ~60-160 с на фразу (короткая 3с-аудио ~15с; 12с-аудио ~85с) — т.е. ~5-6x медленнее реального времени
- Память: DML на iGPU = shared memory: WS ~2.4 ГБ / Private ~11.5 ГБ во время генерации; **после завершения процесса память полностью освобождается** → генерировать отдельным процессом, не держать модель в памяти (в отличие от Voicebox-сервера)

## Проверка

```bash
cd /c/Users/tomas
REF=$(ls /c/Users/tomas/Voicebox/data/profiles/ac9a52ff-*/15*.wav | head -1 | sed 's|^/c/|C:/|')
env -u PYTHONPATH -u VIRTUAL_ENV ./tts-dml-env/Scripts/python.exe ai-radio/scripts/gpu_tts_test.py "$REF" "Тест"
# ожидаем [synth] готово за Ns + [ok] path (WAV, 24000 Гц)
```
