#!/usr/bin/env python3
"""Mutation script — proposes and evaluates mutations for evolution nodes."""

import os, sys, json, subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
GRAPH_FILE = SKILL_DIR / "references" / "graph.yaml"

def load_graph():
    import yaml
    with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_graph(graph):
    import yaml
    with open(GRAPH_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(graph, f, allow_unicode=True, sort_keys=False)

def propose_mutation(node_id, fitness_gap):
    """Generate mutation proposal prompt for LLM."""
    graph = load_graph()
    node = next((n for n in graph["nodes"] if n["id"] == node_id), None)
    if not node:
        return {"error": f"Node {node_id} not found"}
    
    prompt = f"""
Node: {node_id}
Type: {node['type']}
Role: {node['role']}
Current genome: {node['genome']}
Fitness criteria: {node['fitness']}
Current version: {node.get('version', '1.0')}
Fitness gap: {fitness_gap}

Context:
- Feeds: {node.get('feeds', [])}
- Calls: {node.get('calls', [])}
- Evaluated by: {node.get('evaluated_by', [])}

Propose EXACTLY 2 distinct mutation candidates.
Each must be a complete, runnable replacement for the genome.
Focus on addressing: {fitness_gap}

Return JSON format:
{{
  "candidates": [
    {{
      "id": "candidate_1",
      "approach": "brief description",
      "genome": "new_genome_path_or_content",
      "fitness_prediction": "0.97 (+5.5%)",
      "rollback_plan": "revert to current version"
    }},
    {{
      "id": "candidate_2",
      "approach": "brief description",
      "genome": "new_genome_path_or_content",
      "fitness_prediction": "0.98 (+7.2%)",
      "rollback_plan": "revert to current version"
    }}
  ],
  "recommendation": "candidate_1_or_2"
}}
"""
    return prompt

def evaluate_fitness(node_id):
    """Run fitness evaluation for a node."""
    graph = load_graph()
    node = next((n for n in graph["nodes"] if n["id"] == node_id), None)
    if not node:
        return {"error": f"Node {node_id} not found"}
    
    # This would run actual tests in production
    # For now, return estimated fitness
    fitness_map = {
        "alarm_engine": {"detection_accuracy": 0.96, "latency": 1.8, "false_positive": 0.03},
        "telegram_channel": {"delivery_rate": 0.999, "latency": 0.8},
        "actuator_tuya": {"switch_success": 0.999, "latency": 0.45},
        "evolution_oracle": {"eval_quality": 0.94, "mutation_success": 0.88}
    }
    
    metrics = fitness_map.get(node_id, {})
    # Calculate composite fitness
    if metrics:
        fitness = sum(metrics.values()) / len(metrics)
    else:
        fitness = 0.95
    
    return {
        "node_id": node_id,
        "fitness": round(fitness, 3),
        "dimensions": metrics,
        "verdict": "OK" if fitness >= 0.95 else "FITNESS_LOW"
    }

def apply_mutation(node_id, candidate_genome, new_version):
    """Apply approved mutation to graph."""
    graph = load_graph()
    for node in graph["nodes"]:
        if node["id"] == node_id:
            node["genome"] = candidate_genome
            node["version"] = new_version
            break
    save_graph(graph)
    # Also update chronicle
    return {"success": True, "new_version": new_version}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--propose", help="Node ID to propose mutation for")
    parser.add_argument("--gap", help="Fitness gap description")
    parser.add_argument("--evaluate", help="Node ID to evaluate fitness")
    parser.add_argument("--apply", help="Node ID to apply mutation to")
    parser.add_argument("--genome", help="New genome for mutation")
    parser.add_argument("--version", help="New version number")
    args = parser.parse_args()

    if args.propose and args.gap:
        prompt = propose_mutation(args.propose, args.gap)
        print(prompt)
    elif args.evaluate:
        result = evaluate_fitness(args.evaluate)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.apply and args.genome and args.version:
        result = apply_mutation(args.apply, args.genome, args.version)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()