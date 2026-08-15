# DML Setup Fixes for Master-FM GPU-TTS (сессия 2026-08-05, обновлено 2026-08-05)

## Проблема: sys.path конфликт с Hermes venv

Если venv создаётся от Hermes python (`C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`), то `sys.path` зашивает пути Hermes site-packages, и tts-dml-env python их подхватывает несмотря на манипуляции в скрипте.

**Решение:** создавать venv ТОЛЬКО от системного/uv python:
```bash
C:\Users\tomas\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe -m venv C:\Users\tomas\tts-dml-env
```

## Полная установка зависимостей (рабочий набор)

```bash
# 1. torch + torch-directml (MS index)
C:\Users\tomas\tts-dml-env\Scripts\pip.exe install torch==2.4.1 torchvision==0.19.1 torch-directml --extra-index-url https://pkgs.dev.azure.com/dnceng/public/_packaging/directml/pypi/simple/

# 2. transformers с правильным tokenizers
C:\Users\tomas\tts-dml-env\Scripts\pip.exe install transformers==4.57.3

# 3. qwen-tts
C:\Users\tomas\tts-dml-env\Scripts\pip.exe install qwen-tts

# 4. Дополнительные зависимости для DML (обязательны! --target чтобы поставить в tts-dml-env, а не в Hermes)
C:\Users\tomas\tts-dml-env\Scripts\pip.exe install numpy scipy soundfile typing_extensions sympy pillow joblib requests urllib3 idna charset_normalizer certifi tqdm packaging filelock pyyaml regex safetensors huggingface-hub==0.36.2 tokenizers==0.22.2 --target C:\Users\tomas\tts-dml-env\Lib\site-packages

# 5. torchaudio совместимый с torch 2.4.1
C:\Users\tomas\tts-dml-env\Scripts\pip.exe install torchaudio==2.4.1 --target C:\Users\tomas\tts-dml-env\Lib\site-packages --extra-index-url https://pkgs.dev.azure.com/dnceng/public/_packaging/directml/pypi/simple/
```

## Патчи для qwen_tts (применять после установки)

### 1. torch.inference_mode() → torch.no_grad() (подтвержденные местоположения 2026-08-05)
```bash
# qwen_tts/inference/qwen3_tts_model.py строка 355: create_voice_clone_prompt
# qwen_tts/core/models/modeling_qwen3_tts.py строка 1940: extract_speaker_embedding
# qwen_tts/core/models/modeling_qwen3_tts.py строка 1956: generate_speaker_prompt
sed -i 's/@torch.inference_mode()/@torch.no_grad()/g' C:/Users/tomas/tts-dml-env/Lib/site-packages/qwen_tts/core/models/modeling_qwen3_tts.py C:/Users/tomas/tts-dml-env/Lib/site-packages/qwen_tts/inference/qwen3_tts_model.py C:/Users/tomas/tts-dml-env/Lib/site-packages/qwen_tts/inference/qwen3_tts_tokenizer.py
sed -i 's/with torch.inference_mode():/with torch.no_grad():/g' C:/Users/tomas/tts-dml-env/Lib/site-packages/qwen_tts/inference/qwen3_tts_tokenizer.py
```

### 2. torchaudio.compliance.kaldi → librosa fallback (speech_vq.py)
В `XVectorExtractor.extract_code` заменить `kaldi.fbank` на librosa-реализацию:
```python
import librosa
feat_np = librosa.feature.melspectrogram(
    y=norm_audio.squeeze().numpy(),
    sr=16000,
    n_mels=80,
    n_fft=400,
    hop_length=160,
    power=2.0,
)
feat_np = np.log(np.maximum(feat_np, 1e-5))
feat = torch.from_numpy(feat_np.T).float()
```

## RAM Constraint Discovery (2026-08-05) — КРИТИЧНО

**Проблема:** 1.7B модель (3.8 GB fp16, ~7.6 GB fp32) не загружается на машине с 7.8 GB total RAM (~1-2 GB available после ОС/процессов). `AutoModel.from_pretrained` с `low_cpu_mem_usage=True` segfaults (exit 139) при загрузке весов.

**Обходное решение:** использовать **0.6B модель** `Qwen3-TTS-12Hz-0.6B-Base` (~1.5 GB fp16, ~3 GB fp32), которая входит в доступную память.

```bash
# Скачать 0.6B модель вместо 1.7B
hf download Qwen/Qwen3-TTS-12Hz-0.6B-Base
```

**Текущий статус GPU-TTS (2026-08-05) — BROKEN для 1.7B:**
- Загрузка на CPU: работает (~20с)
- `.to(dml)`: segfault (exit 139)
- CPU inference: segfault в `create_voice_clone_prompt` / `generate_voice_clone`
- torch-directml базовые операции (tensor.to(dml), matmul): работают

**Вывод:** Проблема в несовместимости Qwen3-TTS 1.7B с torch-directml 0.2.5 / transformers 4.57.3 + нехватка RAM. Работает только 0.6B вариант.

## Проверка работоспособности (для 0.6B модели)

```bash
REF="C:/Users/tomas/Voicebox/data/profiles/ac9a52ff-0c1a-44c3-a378-959542178e06/156c65ec-7000-45cc-858b-daa368340c1a.wav"
C:/Users/tomas/tts-dml-env/Scripts/python.exe C:/Users/tomas/ai-radio/scripts/gpu_tts_test.py "$REF" "Тест"
# Ожидаем: [synth] готово за ~18s + [ok] path (WAV, 24000 Гц)
```