Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
#!/usr/bin/env python3
"""
Radio ArmsgeddonFM — PlugMem Client Wrapper
Plug-and-play long-term memory for radio evolution cycles.
"""

from __future__ import annotations

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

from plugmem.core.memory_graph import MemoryGraph
from plugmem.config import PlugMemConfig
from plugmem.storage.chroma import ChromaStorage
from plugmem.clients.embedding import EmbeddingClient, LocalDeterministicEmbeddingClient
from plugmem.clients.llm import LLMClient, OpenAICompatibleLLMClient
from plugmem.clients.llm_router import LLMRouter
from plugmem.core.value_functions import (
    SemanticRelevant, ProceduralRelevant, TagRelevant,
    SubgoalRelevant, SemanticEqual, ProceduralEqual,
)

logger = logging.getLogger(__name__)

# Radio-specific constants
RADIO_GRAPH_ID = "radio_armsgeddonfm"
DEFAULT_STORAGE_PATH = Path(r"D:\backups\radio_armsgeddonfm\plugmem")


@dataclass
class RadioSemanticData:
    """Structured semantic memory for radio."""
    node_type: str  # prompt_preset, music_params, tts_profile, feed_quality
    key: str        # e.g., "morning_energetic", "musicgen_morning"
    value: Dict[str, Any]
    confidence: float = 0.8
    source: str = "radio_pipeline"
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = [self.node_type, "radio"]


@dataclass
class RadioProceduralData:
    """Structured procedural memory for radio."""
    node_type: str  # pipeline_config, generation_recipe, debug_fix
    key: str
    value: Dict[str, Any]
    return_value: float = 1.0  # success metric
    confidence: float = 0.9
    source: str = "radio_pipeline"
    session_id: Optional[str] = None

    def __post_init__(self):
        if self.session_id is None:
            self.session_id = f"radio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


@dataclass
class RadioEpisodicData:
    """Structured episodic memory for radio."""
    cycle_badge: str      # e.g., "A07"
    slot: str             # morning, day, evening, night
    duration_sec: int
    quality_scores: Dict[str, float]
    issues: List[str]
    human_rating: Optional[float] = None
    listener_feedback: Optional[Dict[str, Any]] = None


# Dummy LLM client for when no LLM service is available
class DummyLLMClient(LLMClient):
    """Dummy LLM client that returns empty responses."""
    def complete(self, messages, temperature=0, top_p=1.0, max_tokens=4096) -> str:
        return ""


class RadioPlugMemClient:
    """
    Radio-specific wrapper around PlugMem MemoryGraph.
    
    Provides high-level methods for:
    - Storing/retrieving prompt presets, music params, TTS profiles
    - Storing/retrieving pipeline configs, recipes, debug fixes
    - Logging cycle runs with quality metrics
    - Querying best configurations for a time slot
    """
    
    def __init__(
        self,
        storage_path: Path = DEFAULT_STORAGE_PATH,
        graph_id: str = RADIO_GRAPH_ID,
        llm_client: Optional[LLMClient] = None,
        embedding_client: Optional[EmbeddingClient] = None,
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.graph_id = graph_id
        
        # Initialize PlugMem config
        self.config = PlugMemConfig(
            chroma_mode="persistent",
            chroma_path=str(self.storage_path / "chroma"),
            llm_base_url="",
            llm_api_key="",
            llm_model="",
            embedding_base_url="",
            embedding_model="nvidia/NV-Embed-v2",
            embedding_api_key="",
        )
        
        # Initialize clients (use defaults if not provided)
        self.embedder = embedding_client or LocalDeterministicEmbeddingClient(dim=384)
        self.llm = llm_client or DummyLLMClient()
        self.router = LLMRouter.from_single_client(self.llm)
        
        # Initialize ChromaDB client
        import chromadb
        chroma_client = chromadb.PersistentClient(path=str(self.storage_path / "chroma"))
        
        # Initialize storage with chromadb client
        self.storage = ChromaStorage(
            client=chroma_client,
            embedding_client=self.embedder,
        )
        
        # Create/get graph
        self.graph = MemoryGraph(
            graph_id=self.graph_id,
            storage=self.storage,
            llm=self.router,
            embedder=self.embedder,
        )
        
        # Create graph collections if they don't exist
        if not self.storage.graph_exists(self.graph_id):
            self.storage.create_graph(self.graph_id)
            logger.info(f"Created new graph: {self.graph_id}")
        
        # Load existing graph
        stats = self.graph.load()
        logger.info(f"Radio PlugMem graph '{self.graph_id}' loaded: {stats}")
    
    # =====================================================================
    # SEMANTIC MEMORY: Prompts, Params, Profiles
    # =====================================================================
    
    def store_prompt_preset(
        self,
        slot: str,           # morning, day, evening, night
        style: str,          # energetic, chill, news, mixed
        prompt: str,
        confidence: float = 0.8,
    ) -> int:
        """Store a music/voice prompt preset for a time slot."""
        data = RadioSemanticData(
            node_type="prompt_preset",
            key=f"{slot}_{style}",
            value={"slot": slot, "style": style, "prompt": prompt},
            confidence=confidence,
            tags=["prompt_preset", "radio", slot, style],
        )
        return self._store_semantic(data)
    
    def store_music_params(
        self,
        model: str,          # musicgen-small, riffusion, etc.
        slot: str,
        params: Dict[str, Any],
        quality_score: float,
        confidence: float = 0.85,
    ) -> int:
        """Store music generation parameters that worked well."""
        data = RadioSemanticData(
            node_type="music_params",
            key=f"{model}_{slot}",
            value={"model": model, "slot": slot, "params": params, "quality": quality_score},
            confidence=confidence,
            tags=["music_params", "radio", model, slot],
        )
        return self._store_semantic(data)
    
    def store_tts_profile(
        self,
        voice: str,          # qwen_custom_voice, edge_dmitry, etc.
        slot: str,
        profile: Dict[str, Any],
        confidence: float = 0.9,
    ) -> int:
        """Store TTS voice profile for a time slot."""
        data = RadioSemanticData(
            node_type="tts_profile",
            key=f"{voice}_{slot}",
            value={"voice": voice, "slot": slot, "profile": profile},
            confidence=confidence,
            tags=["tts_profile", "radio", voice, slot],
        )
        return self._store_semantic(data)
    
    def store_feed_quality(
        self,
        feed_name: str,
        metrics: Dict[str, float],
        confidence: float = 0.85,
    ) -> int:
        """Store RSS feed quality metrics."""
        data = RadioSemanticData(
            node_type="feed_quality",
            key=feed_name,
            value={"feed": feed_name, "metrics": metrics},
            confidence=confidence,
            tags=["feed_quality", "radio", feed_name],
        )
        return self._store_semantic(data)
    
    def _store_semantic(self, data: RadioSemanticData) -> int:
        """Internal: store semantic node."""
        # Build memory dict directly (bypassing Memory class which requires LLM)
        mem_dict = {
            "goal": f"store_{data.node_type}_{data.key}",
            "episodic": [[]],  # empty trajectory
            "semantic": [{
                "semantic_memory": json.dumps(data.value, ensure_ascii=False),
                "tags": data.tags,
                "source": data.source,
                "confidence": data.confidence,
                "trajectory_num": 0,
                "turn_num": 0,
                "session_id": f"radio_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            }],
            "procedural": [],
        }
        
        # Generate embeddings
        sem_emb = self.embedder.embed(json.dumps(data.value))
        tag_embs = [self.embedder.embed(tag) for tag in data.tags]
        
        mem_embedding = {
            "semantic": [{
                "semantic_memory": sem_emb,
                "tags": tag_embs,
            }],
            "procedural": [],
        }
        
        # Create a minimal Memory-like object
        class SimpleMemory:
            def __init__(self, memory, memory_embedding):
                self.memory = memory
                self.memory_embedding = memory_embedding
        
        simple_mem = SimpleMemory(mem_dict, mem_embedding)
        self.graph.insert(simple_mem)
        logger.info(f"Stored semantic: {data.node_type}/{data.key}")
        return len(self.graph.semantic_nodes) - 1
    
    def retrieve_best_prompt(self, slot: str, style: str = None) -> Optional[str]:
        """Retrieve best prompt preset for a slot/style."""
        query = f"best prompt for {slot}"
        if style:
            query += f" {style} style"
        
        result = self.graph.retrieve_and_reason(
            observation=query,
            task_type="radio_generation",
            mode="semantic_memory",
        )
        return result
    
    def retrieve_best_music_params(self, slot: str, model: str = None) -> Optional[Dict]:
        """Retrieve best music generation params for a slot."""
        query = f"best music generation parameters for {slot}"
        if model:
            query += f" using {model}"
        
        result = self.graph.retrieve_and_reason(
            observation=query,
            task_type="radio_generation",
            mode="semantic_memory",
        )
        return result
    
    def retrieve_best_tts_profile(self, slot: str, voice: str = None) -> Optional[Dict]:
        """Retrieve best TTS profile for a slot."""
        query = f"best TTS voice profile for {slot}"
        if voice:
            query += f" using {voice}"
        
        result = self.graph.retrieve_and_reason(
            observation=query,
            task_type="radio_generation",
            mode="semantic_memory",
        )
        return result
    
    # =====================================================================
    # PROCEDURAL MEMORY: Pipeline configs, recipes, fixes
    # =====================================================================
    
    def store_pipeline_config(
        self,
        name: str,
        config: Dict[str, Any],
        success_rate: float = 1.0,
    ) -> int:
        """Store a working pipeline configuration."""
        data = RadioProceduralData(
            node_type="pipeline_config",
            key=name,
            value=config,
            return_value=success_rate,
            confidence=0.95,
        )
        return self._store_procedural(data)
    
    def store_generation_recipe(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        success_rate: float = 1.0,
    ) -> int:
        """Store a generation recipe (step-by-step procedure)."""
        data = RadioProceduralData(
            node_type="generation_recipe",
            key=name,
            value={"steps": steps},
            return_value=success_rate,
            confidence=0.9,
        )
        return self._store_procedural(data)
    
    def store_debug_fix(
        self,
        symptom: str,
        root_cause: str,
        fix: str,
        confidence: float = 0.95,
    ) -> int:
        """Store a debug fix for a known issue."""
        data = RadioProceduralData(
            node_type="debug_fix",
            key=symptom[:50],  # Use symptom as key
            value={"symptom": symptom, "root_cause": root_cause, "fix": fix},
            return_value=1.0,
            confidence=confidence,
        )
        return self._store_procedural(data)
    
    def _store_procedural(self, data: RadioProceduralData) -> int:
        """Internal: store procedural node."""
        # Build memory dict directly - PlugMem expects subgoal + procedural_memory
        mem_dict = {
            "goal": f"store_{data.node_type}_{data.key}",
            "episodic": [[]],
            "semantic": [],
            "procedural": [{
                "subgoal": f"radio_{data.node_type}_{data.key}",  # Required by PlugMem
                "procedural_memory": json.dumps(data.value, ensure_ascii=False),
                "return": data.return_value,
                "source": data.source,
                "confidence": data.confidence,
                "trajectory_num": 0,
                "session_id": data.session_id,
            }],
        }
        
        proc_emb = self.embedder.embed(json.dumps(data.value))
        subgoal_emb = self.embedder.embed(f"radio_{data.node_type}_{data.key}")
        
        mem_embedding = {
            "semantic": [],
            "procedural": [{
                "subgoal": subgoal_emb,
                "procedural_memory": proc_emb,
            }],
        }
        
        class SimpleMemory:
            def __init__(self, memory, memory_embedding):
                self.memory = memory
                self.memory_embedding = memory_embedding
        
        simple_mem = SimpleMemory(mem_dict, mem_embedding)
        self.graph.insert(simple_mem)
        logger.info(f"Stored procedural: {data.node_type}/{data.key}")
        return len(self.graph.procedural_nodes) - 1
    
    def retrieve_pipeline_config(self, slot: str) -> Optional[Dict]:
        """Retrieve best pipeline config for a time slot."""
        result = self.graph.retrieve_and_reason(
            observation=f"pipeline configuration for {slot} radio slot",
            task_type="radio_generation",
            mode="procedural_memory",
        )
        return result
    
    def retrieve_debug_fix(self, symptom: str) -> Optional[str]:
        """Retrieve fix for a known issue."""
        result = self.graph.retrieve_and_reason(
            observation=f"fix for: {symptom}",
            task_type="radio_debug",
            mode="procedural_memory",
        )
        return result
    
    # =====================================================================
    # EPISODIC MEMORY: Cycle runs, quality scores, feedback
    # =====================================================================
    
    def log_cycle_run(
        self,
        cycle_badge: str,      # A07, A08, etc.
        slot: str,             # morning, day, evening, night
        duration_sec: int,
        quality_scores: Dict[str, float],
        issues: List[str] = None,
        human_rating: float = None,
        listener_feedback: Dict = None,
    ) -> int:
        """Log a complete cycle execution as episodic memory."""
        data = RadioEpisodicData(
            cycle_badge=cycle_badge,
            slot=slot,
            duration_sec=duration_sec,
            quality_scores=quality_scores,
            issues=issues or [],
            human_rating=human_rating,
            listener_feedback=listener_feedback,
        )
        
        # Build memory dict directly
        mem_dict = {
            "goal": f"cycle_run_{cycle_badge}_{slot}",
            "episodic": [[{
                "observation": f"Cycle {cycle_badge} {slot} completed. Quality: {quality_scores}",
                "action": "generate_radio_block",
                "time": int(datetime.now().timestamp()),
                "subgoal": f"generate_{slot}_block",
                "state": json.dumps(data.__dict__, default=str),
                "reward": str(sum(quality_scores.values()) / len(quality_scores)) if quality_scores else "0",
            }]],
            "semantic": [{
                "semantic_memory": json.dumps(data.__dict__, ensure_ascii=False, default=str),
                "tags": ["cycle_run", "radio", cycle_badge, slot],
                "source": "radio_pipeline",
                "confidence": 1.0,
                "trajectory_num": 0,
                "turn_num": 0,
                "session_id": cycle_badge,
            }],
            "procedural": [],
        }
        
        # Generate embeddings
        sem_emb = self.embedder.embed(json.dumps(data.__dict__, default=str))
        tag_embs = [self.embedder.embed(t) for t in ["cycle_run", "radio", cycle_badge, slot]]
        
        mem_embedding = {
            "semantic": [{
                "semantic_memory": sem_emb,
                "tags": tag_embs,
            }],
            "procedural": [],
        }
        
        class SimpleMemory:
            def __init__(self, memory, memory_embedding):
                self.memory = memory
                self.memory_embedding = memory_embedding
        
        simple_mem = SimpleMemory(mem_dict, mem_embedding)
        self.graph.insert(simple_mem)
        logger.info(f"Logged cycle run: {cycle_badge} {slot}")
        return len(self.graph.episodic_nodes) - 1
    
    def get_cycle_history(self, cycle_badge: str = None, slot: str = None) -> List[Dict]:
        """Retrieve cycle run history."""
        query = "radio cycle run history"
        if cycle_badge:
            query += f" {cycle_badge}"
        if slot:
            query += f" {slot}"
        
        result = self.graph.retrieve_and_reason(
            observation=query,
            task_type="radio_analysis",
            mode="episodic_memory",
        )
        return result
    
    def get_best_cycle_for_slot(self, slot: str) -> Optional[Dict]:
        """Get the highest-rated cycle for a time slot."""
        query = f"best quality radio cycle for {slot} slot"
        result = self.graph.retrieve_and_reason(
            observation=query,
            task_type="radio_analysis",
            mode="episodic_memory",
        )
        return result
    
    # =====================================================================
    # CONSOLIDATION & MAINTENANCE
    # =====================================================================
    
    def consolidate(self) -> Dict[str, int]:
        """Run semantic consolidation (merge similar nodes)."""
        stats = self.graph.update_semantic_subgraph(
            merge_threshold=0.75,
            max_merges_per_node=2,
            max_candidates_per_tag=100,
            max_total_candidates=500,
            min_credibility_to_keep_active=5,
        )
        logger.info(f"Consolidation complete: {stats}")
        return stats
    
    def get_stats(self) -> Dict[str, int]:
        """Get graph statistics."""
        return self.storage.get_graph_stats(self.graph_id)
    
    def list_graphs(self) -> List[str]:
        """List all available graphs."""
        return self.storage.list_graphs()
    
    def backup_graph(self, backup_path: Path) -> None:
        """Backup the ChromaDB to a directory."""
        import shutil
        backup_path = Path(backup_path)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # ChromaDB persists to storage_path
        src = self.storage_path / "chroma"
        if src.exists():
            shutil.copytree(src, backup_path / "chroma", dirs_exist_ok=True)
            logger.info(f"Graph backed up to {backup_path}")


# =====================================================================
# CONVENIENCE FUNCTIONS
# =====================================================================

def create_radio_plugmem(
    storage_path: Path = DEFAULT_STORAGE_PATH,
) -> RadioPlugMemClient:
    """Factory function to create a RadioPlugMemClient with defaults."""
    return RadioPlugMemClient(storage_path=storage_path)


def init_radio_memory() -> RadioPlugMemClient:
    """Initialize radio memory graph with default presets."""
    client = create_radio_plugmem()
    
    # Default prompt presets
    client.store_prompt_preset("morning", "energetic", 
        "upbeat electronic, 110 bpm, energetic, synthesizers, optimistic, driving rhythm")
    client.store_prompt_preset("morning", "news",
        "calm ambient background, 80 bpm, neutral, minimal, professional news bed")
    client.store_prompt_preset("day", "energetic",
        "upbeat pop-electronic, 120 bpm, catchy, melodic, positive energy")
    client.store_prompt_preset("day", "chill",
        "lo-fi hip hop, 85 bpm, relaxed, jazzy chords, nostalgic, study vibes")
    client.store_prompt_preset("evening", "chill",
        "downtempo electronic, 95 bpm, atmospheric, warm pads, reflective")
    client.store_prompt_preset("evening", "mixed",
        "melodic house, 118 bpm, emotional, progressive, sunset vibes")
    client.store_prompt_preset("night", "chill",
        "ambient drone, 60 bpm, dark, spacious, hypnotic, late night atmosphere")
    client.store_prompt_preset("night", "energetic",
        "dark techno, 125 bpm, driving, industrial, underground club energy")
    
    # Default pipeline config
    client.store_pipeline_config("dj_v2_morning", {
        "music_first": True,
        "crossfade_sec": 2.0,
        "ducking_db": -18,
        "target_lufs": -14,
        "normalize": True,
        "music_duration_sec": 1800,
        "news_items": 10,
    })
    
    # Default generation recipe
    client.store_generation_recipe("hour_block_standard", [
        {"step": "scrape_news", "slot": "morning", "max_items": 15},
        {"step": "filter_news", "min_relevance": 0.7, "max_items": 10},
        {"step": "gen_music", "duration_sec": 1800, "style": "energetic"},
        {"step": "gen_tts", "voice": "qwen_custom_voice", "preset": "Ryan"},
        {"step": "mix", "ducking_db": -18, "crossfade_sec": 2.0},
        {"step": "normalize", "target_lufs": -14},
        {"step": "validate", "min_duration_sec": 3500, "max_duration_sec": 3700},
    ])
    
    # Known debug fixes
    client.store_debug_fix(
        symptom="Voicebox TTS generation hangs indefinitely",
        root_cause="Model not fully loaded on first call",
        fix="Make a warmup call with short text before actual generation",
    )
    client.store_debug_fix(
        symptom="MusicGen output has clicks/pops at loop points",
        root_cause="Generated audio doesn't loop seamlessly",
        fix="Apply crossfade at loop points, use longer generation window",
    )
    client.store_debug_fix(
        symptom="DirectML out of memory on Radeon 780M",
        root_cause="VRAM fragmented, model too large for 512MB VRAM",
        fix="Use CPU offload, reduce batch size, clear cache between generations",
    )
    
    logger.info("Radio memory initialized with defaults")
    return client


if __name__ == "__main__":
    # Demo: initialize and test
    logging.basicConfig(level=logging.INFO)
    
    print("Initializing Radio PlugMem...")
    client = init_radio_memory()
    
    print(f"\nGraph stats: {client.get_stats()}")
    
    print("\nTesting retrieval...")
    result = client.retrieve_best_prompt("morning", "energetic")
    print(f"Best morning prompt: {result[:200]}...")
    
    print("\nDone!")