---
type: index
---

# 🧬 Эволюционный Граф — Индекс

> [!abstract] Живой граф проектов Гримуара
> Узлов: **35** · Рёбер: **75** · 🟢 ЖИВ: **24** · 🟡 БОЛЕН: **0** · 🔴 МЁРТВ: **11** · ⚪ неизвестно: **0**

## Карта узлов

| Узел | Тип | Пульс | Роль |
|---|---|---|---|
| 🟢 [[oracle]] | 🧑‍🔬 HUMAN | ЖИВ | Мастер Инквизитор — видение, критерии fitness, одо |
| 🔴 [[gardener]] | 🤖 AGENT | МЁРТВ | Hermes Agent — пульс, отбор, мутации, экстинкции |
| 🟢 [[chronicle]] | 🗄️ MEMORY | ЖИВ | Летопись: рождения, мутации, экстинкции, открытия |
| 🟢 [[archive]] | 🗄️ MEMORY | ЖИВ | Могильник: полные геномы вымерших узлов + причина |
| 🟢 [[ai_eng_daily]] | 📜 SKILL | ЖИВ | Ежедневный研究 AI Engineering: vLLM/SGLang, speculat |
| 🟢 [[vllm_optimization]] | 📜 SKILL | ЖИВ | vLLM inference optimization: paged attention, cont |
| 🟢 [[sglang_serving]] | 📜 SKILL | ЖИВ | SGLang high-performance serving: omni-modal pipeli |
| 🟢 [[quantization_eval]] | 📜 SKILL | ЖИВ | Quantization evaluation: nonlinear knowledge loss  |
| 🟢 [[gpu_cluster_mgmt]] | 📜 SKILL | ЖИВ | GPU cluster management: GPUStack unified vLLM/SGLa |
| 🔴 [[depthchart]] | 📜 SKILL | МЁРТВ | Context-aware speculative decoding: (B, ctx) K sch |
| 🔴 [[nexus_rag]] | ⚙️ PIPELINE | МЁРТВ | Air-gapped RAG for Kubernetes: document ingestion  |
| 🔴 [[tools_registry]] | 📜 SKILL | МЁРТВ | Shared skill/secret vault for agent teams: tools-r |
| 🔴 [[auto_round]] | 📜 SKILL | МЁРТВ | SOTA quantization for CPU/XPU/CUDA: Intel AutoRoun |
| 🔴 [[club_3090]] | 🗄️ MEMORY | МЁРТВ | Community recipes for RTX 3090/4090/5090 serving:  |
| 🔴 [[runnburn]] | 📜 SKILL | МЁРТВ | Run 295B MoE from 98GB GGUF on 64GB RAM: extreme m |
| 🟢 [[rag_pipeline]] | 📜 SKILL | ЖИВ | RAG pipelines: hybrid search, reranking, graph RAG |
| 🟢 [[fine_tuning_pipeline]] | 📜 SKILL | ЖИВ | LoRA/QLoRA fine-tuning with Unsloth for small mode |
| 🟢 [[pd_disaggregation]] | 📜 SKILL | ЖИВ | PD Disaggregation inference: Prefill/Decode separa |
| 🟢 [[dflash_speculative]] | 📜 SKILL | ЖИВ | DFlash speculative decoding: 16-token block drafte |
| 🟢 [[muse_glimmer]] | ⚙️ PIPELINE | ЖИВ | Meta Muse Glimmer 30B: Apache 2.0 open-weight agen |
| 🟢 [[needle2_edge]] | ⚙️ PIPELINE | ЖИВ | Needle 2: 14MB agentic LLM (45M params, 2-bit) for |
| 🟢 [[inferbench]] | 📜 SKILL | ЖИВ | InferBench: vLLM/FastAPI benchmarking framework fo |
| 🟢 [[backpressure]] | 📜 SKILL | ЖИВ | Backpressure: Load simulator for system design and |
| 🔴 [[alfred_intelligence]] | 🤖 AGENT | МЁРТВ | AIfred-Intelligence: Self-hosted Multi-Agent Assis |
| 🟢 [[hyperprobe]] | 📜 SKILL | ЖИВ | HyperProbe: Production debugging via MCP — virtual |
| 🟢 [[gauntlet_loop]] | 📜 SKILL | ЖИВ | Gauntlet Loop: AI Loop Engineering methodology — s |
| 🔴 [[pmc_retrieval]] | 📜 SKILL | МЁРТВ | PMC: Build-Time Per-Modality Centroid Correction f |
| 🟢 [[honeyhive_eval]] | 📜 SKILL | ЖИВ | HoneyHive: Unified evaluation & monitoring platfor |
| 🔴 [[ai_inference_platform]] | ⚙️ PIPELINE | МЁРТВ | ai-inference-platform: Enterprise Agent/RAG + Open |
| 🟢 [[autonomous_ai_agents]] | 📜 SKILL | ЖИВ | Autonomous AI Agents: Spawning and orchestrating a |
| 🟢 [[godmode_coder]] | 📜 SKILL | ЖИВ | GodModeCoder Cathedral: Complete Windows dev works |
| 🟢 [[paranoidx]] | ⚙️ PIPELINE | ЖИВ | ФЛАГМАН: ParanoidX + IsleProject — Sovereign Go-се |
| 🔴 [[isle_client]] | 🤖 AGENT | МЁРТВ | Клиенты The-Isle / Royal-Isle: Flutter-приложения  |
| 🟢 [[superguard]] | ⚙️ PIPELINE | ЖИВ | КОММЕРЧЕСКИЙ: AISuperGuard — AI-охрана периметра/к |
| 🟢 [[watchdog]] | 🩺 WATCHDOG | ЖИВ | Пульс графа: health-чек узлов, статусы ЖИВ/БОЛЕН/М |

## Рёбра

| От | Тип | К |
|---|---|---|
| [[oracle]] | 👁️ VISION | [[paranoidx]] |
| [[oracle]] | 👁️ VISION | [[superguard]] |
| [[oracle]] | 👁️ VISION | [[gardener]] |
| [[oracle]] | ✅ APPROVAL | [[gardener]] |
| [[gardener]] | 🧠 CONTROLS | [[paranoidx]] |
| [[gardener]] | 🧠 CONTROLS | [[superguard]] |
| [[gardener]] | ⚖️ EVALUATES | [[isle_client]] |
| [[gardener]] | ⚖️ EVALUATES | [[ai_eng_daily]] |
| [[paranoidx]] | 🤝 CALLS | [[isle_client]] |
| [[superguard]] | 🍽️ FEEDS | [[watchdog]] |
| [[paranoidx]] | 🍽️ FEEDS | [[watchdog]] |
| [[gardener]] | 🧠 CONTROLS | [[watchdog]] |
| [[gardener]] | 🍽️ FEEDS | [[chronicle]] |
| [[gardener]] | 🍽️ FEEDS | [[archive]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[vllm_optimization]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[sglang_serving]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[quantization_eval]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[gpu_cluster_mgmt]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[depthchart]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[nexus_rag]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[tools_registry]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[auto_round]] |
| [[vllm_optimization]] | 🍽️ FEEDS | [[depthchart]] |
| [[vllm_optimization]] | 🍽️ FEEDS | [[club_3090]] |
| [[vllm_optimization]] | 🍽️ FEEDS | [[runnburn]] |
| [[gpu_cluster_mgmt]] | 🍽️ FEEDS | [[club_3090]] |
| [[quantization_eval]] | 🍽️ FEEDS | [[auto_round]] |
| [[quantization_eval]] | 🍽️ FEEDS | [[runnburn]] |
| [[gardener]] | ⚖️ EVALUATES | [[tools_registry]] |
| [[paranoidx]] | 🤝 CALLS | [[nexus_rag]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[rag_pipeline]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[fine_tuning_pipeline]] |
| [[nexus_rag]] | 🍽️ FEEDS | [[rag_pipeline]] |
| [[quantization_eval]] | 🍽️ FEEDS | [[fine_tuning_pipeline]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[pd_disaggregation]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[dflash_speculative]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[muse_glimmer]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[needle2_edge]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[inferbench]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[backpressure]] |
| [[vllm_optimization]] | 🍽️ FEEDS | [[pd_disaggregation]] |
| [[vllm_optimization]] | 🍽️ FEEDS | [[dflash_speculative]] |
| [[vllm_optimization]] | 🍽️ FEEDS | [[backpressure]] |
| [[sglang_serving]] | 🍽️ FEEDS | [[pd_disaggregation]] |
| [[sglang_serving]] | 🍽️ FEEDS | [[dflash_speculative]] |
| [[quantization_eval]] | 🍽️ FEEDS | [[needle2_edge]] |
| [[quantization_eval]] | 🍽️ FEEDS | [[inferbench]] |
| [[fine_tuning_pipeline]] | 🍽️ FEEDS | [[needle2_edge]] |
| [[gpu_cluster_mgmt]] | 🍽️ FEEDS | [[backpressure]] |
| [[pd_disaggregation]] | 🍽️ FEEDS | [[muse_glimmer]] |
| [[dflash_speculative]] | 🍽️ FEEDS | [[muse_glimmer]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[alfred_intelligence]] |
| [[autonomous_ai_agents]] | 🍽️ FEEDS | [[alfred_intelligence]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[hyperprobe]] |
| [[superguard]] | 🍽️ FEEDS | [[hyperprobe]] |
| [[paranoidx]] | 🍽️ FEEDS | [[hyperprobe]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[gauntlet_loop]] |
| [[godmode_coder]] | 🍽️ FEEDS | [[gauntlet_loop]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[pmc_retrieval]] |
| [[quantization_eval]] | 🍽️ FEEDS | [[pmc_retrieval]] |
| [[rag_pipeline]] | 🍽️ FEEDS | [[pmc_retrieval]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[honeyhive_eval]] |
| [[rag_pipeline]] | 🍽️ FEEDS | [[honeyhive_eval]] |
| [[fine_tuning_pipeline]] | 🍽️ FEEDS | [[honeyhive_eval]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[ai_inference_platform]] |
| [[vllm_optimization]] | 🍽️ FEEDS | [[ai_inference_platform]] |
| [[rag_pipeline]] | 🍽️ FEEDS | [[ai_inference_platform]] |
| [[gpu_cluster_mgmt]] | 🍽️ FEEDS | [[ai_inference_platform]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[autonomous_ai_agents]] |
| [[gardener]] | 🍽️ FEEDS | [[autonomous_ai_agents]] |
| [[ai_eng_daily]] | 🍽️ FEEDS | [[godmode_coder]] |
| [[gardener]] | 🍽️ FEEDS | [[godmode_coder]] |
| [[gauntlet_loop]] | 🍽️ FEEDS | [[godmode_coder]] |
| [[hyperprobe]] | 🍽️ FEEDS | [[superguard]] |
| [[hyperprobe]] | 🍽️ FEEDS | [[paranoidx]] |

## Критерии fitness

- **paranoidx:** `5 Docker-контейнеров живы (smp-server, coturn, v2ray, tor, xftp); API 200; TLS не протух`
- **isle_client:** `Flutter-сборки идут; encrypt AES работает; клиенты подключаются`
- **superguard:** `камера RTSP жива; детекция вор-электрик срабатывает; Telegram-алерт уходит; подписка активна`
- **depthchart:** `speculative decoding scheduler works for long-context agent loops; latency improvement measurable`
- **nexus_rag:** `air-gapped ingestion works; classification enforced; no data leaks`
- **tools_registry:** `agent skill/secret sharing functional; no key leaks; registry queryable`
- **auto_round:** `quantization quality validated; nonlinear loss <5% per model; 4-bit usable`
- **club_3090:** `recipes tested on AMD 780M; DirectML/ROCm configs documented; speedups recorded`
- **runnburn:** `295B MoE runs on 64GB RAM; GGUF loading works; inference latency acceptable`
- **rag_pipeline:** `hybrid search + reranking functional; air-gapped K8s deployment validated; hallucination detection integrated`
- **fine_tuning_pipeline:** `Unsloth LoRA pipeline works; Qwen2.5-0.5B 4-bit trains on edge; GGUF export validated`
- **pd_disaggregation:** `TileRT decode + vLLM/SGLang prefill separation functional; p95 TTFT/ITL improved`
- **dflash_speculative:** `16-token block drafter verified in parallel; 3.1x speedup on RTX 5090, 1.8x on M5-Max`
- **muse_glimmer:** `30B Apache 2.0 model runs on 24-32GB VRAM; 4-bit quantized <20GB; DFlash integrated; MCP Atlas 75.5`
- **needle2_edge:** `14MB binary runs 500 tok/s on RPi5; 2-bit quantization; schema extraction works; confidence scoring`
- **inferbench:** `vLLM/FastAPI benchmarks TTFT, ITL, throughput, GPU util; concurrent load testing functional`
- **backpressure:** `Load simulator stresses LLM serving; config tuning validated over hardware scaling`
- **alfred_intelligence:** `Multi-agent debate modes functional; voice STT/TTS working; RAG long-term memory persists; multi-backend routing operational`
- **hyperprobe:** `MCP virtual breakpoints capture runtime state in prod; Node/Java/Python SDKs functional; zero-redeploy debugging validated`
- **gauntlet_loop:** `Structured AI-assisted iteration cycles measurable; Plan→Code→Test→Review→Reflect phases tracked; velocity improved`
- **pmc_retrieval:** `Binary-quantized cross-modal retrieval quality matches FP32; centroid correction reduces quantization loss <3%`
- **honeyhive_eval:** `Offline evals + online monitoring unified; metrics docker env runs arbitrary Python/LLM evals; fine-tuning flywheel automated`
- **ai_inference_platform:** `Go gateway + vLLM + K8s deployment functional; agent/RAG pipelines serve production traffic; observability integrated`
- **autonomous_ai_agents:** `Independent agent processes spawn/complete tasks; parallel workstreams coordinate; delegation graph queryable`
- **godmode_coder:** `Windows dev workstation complete; Android/iOS/Web/Desktop/Embedded toolchains configured; registry persistent; cross-platform builds pass`

*Обновлено: 2026-08-12 23:21*
