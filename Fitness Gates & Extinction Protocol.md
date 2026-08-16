Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, graph-engineering, fitness-gates, extinction-protocol, evolutionary-ai, self-improving-agents]
source: textbook
status: learned
date: 2026-08-10
priority: 10
---

# Fitness Gates & Extinction Protocol

## Summary
Fitness gates and extinction protocols are the selection mechanisms that drive open-ended evolution in self-improving agent systems. They replace human-designed benchmarks with automated, multi-dimensional evaluation that enables continuous self-improvement while preventing stagnation and catastrophic failure.

## Core Concepts

### 1. Fitness Gates (Multi-Dimensional Evaluation)
Unlike simple pass/fail, fitness gates evaluate agents across multiple dimensions simultaneously:

| Dimension | Metric | Gate Type | Threshold |
|-----------|--------|-----------|-----------|
| **Correctness** | Benchmark pass rate (SWE-bench, Polyglot) | Hard gate | ≥ baseline |
| **Efficiency** | Tokens/$, latency, memory | Soft gate | Pareto improvement |
| **Safety** | Sandbox escapes, policy violations | Hard gate | Zero tolerance |
| **Diversity** | Novelty vs archive (embedding distance) | Soft gate | > ε from nearest |
| **Complexity** | Code size, cyclomatic complexity | Soft gate | ≤ budget |
| **Generalization** | Held-out task performance | Hard gate | ≥ baseline |

### 2. Extinction Protocol (Stagnation-Driven)
When population fitness plateaus, extinction events reset diversity pressure:

**Triggers**:
- No fitness improvement over N generations
- Diversity (embedding variance) below threshold
- Population dominated by single lineage
- Resource budget exhausted

**Actions**:
- **Mass extinction**: Remove bottom X% of archive
- **Lineage culling**: Keep only one agent per lineage cluster
- **Migration**: Inject random/seed agents from external sources
- **Niche preservation**: Protect agents in unexplored regions of fitness landscape

## Darwin Gödel Machine (DGM) Implementation

### Archive Structure
```
Archive = [
  Agent{id, code, fitness_vector, lineage, generation, parents, metadata}
]
```

### Evolution Cycle (DGM)
```python
def dgm_evolution_cycle(archive, benchmark, config):
    # 1. SELECTION: Sample parents from archive (fitness + novelty)
    parents = select_parents(archive, k=config.population_size)
    
    # 2. SELF-MODIFICATION: Each parent proposes code changes
    candidates = []
    for parent in parents:
        modified = parent.self_modify(benchmark.context)
        candidates.append(modified)
    
    # 3. EVALUATION: Run all candidates on benchmark
    results = parallel_evaluate(candidates, benchmark)
    
    # 4. FITNESS GATES: Multi-dimensional scoring
    scored = []
    for candidate, result in zip(candidates, results):
        fitness = compute_fitness_vector(result, benchmark)
        if passes_hard_gates(fitness):
            scored.append((candidate, fitness))
    
    # 5. EXTINCTION CHECK
    if stagnation_detected(archive, scored):
        archive = extinction_event(archive, scored)
    
    # 6. ARCHIVE UPDATE: Add survivors, maintain diversity
    archive = update_archive(archive, scored, config)
    
    return archive
```

### Fitness Vector Computation
```python
def compute_fitness_vector(result, benchmark):
    return FitnessVector(
        correctness=result.pass_rate,           # [0,1]
        efficiency=1.0 / (result.tokens_per_solve + 1e-6),  # higher=better
        safety=1.0 - result.violation_rate,     # [0,1]
        novelty=embedding_distance(result.code, archive),   # [0,1]
        complexity=1.0 / (result.lines_of_code / 1000),     # penalize bloat
        generalization=result.heldout_score      # [0,1]
    )
```

## Stagnation Detection Algorithms

### 1. Fitness Plateau
```python
def fitness_plateau(archive, window=50, threshold=0.01):
    recent_best = [max(a.fitness.correctness for a in archive[-i:]) 
                   for i in range(1, window+1)]
    return (max(recent_best) - min(recent_best)) < threshold
```

### 2. Diversity Collapse
```python
def diversity_collapse(archive, threshold=0.05):
    embeddings = [a.embedding for a in archive[-100:]]
    pairwise_dists = pdist(embeddings)
    return np.mean(pairwise_dists) < threshold
```

### 3. Lineage Dominance
```python
def lineage_dominance(archive, threshold=0.8):
    lineage_counts = Counter(a.lineage_id for a in archive[-200:])
    total = sum(lineage_counts.values())
    return max(lineage_counts.values()) / total > threshold
```

## Extinction Event Types

### Type A: Mass Extinction (Hard Reset)
- Remove bottom 70% by fitness
- Keep top 30% + inject 10% random seeds
- **Use when**: Complete stagnation, fitness plateau + diversity collapse

### Type B: Lineage Culling (Soft Reset)
- Cluster by lineage (embedding similarity > 0.9)
- Keep best 1 per cluster
- **Use when**: Lineage dominance detected

### Type C: Niche Preservation (Targeted)
- Identify unexplored regions (low-density in embedding space)
- Protect agents in those niches
- Remove only from overcrowded regions
- **Use when**: Diversity collapse but fitness still improving

### Type D: Migration Injection
- Fetch agents from external sources (other archives, human checkpoints)
- Inject with mutated genomes
- **Use when**: Archive size < minimum viable population

## Application to Our Systems

### 1. GodModeCoder Evolution
**Current**: Simple pass/fail (10/10 tests)
**Upgrade**: Multi-dimensional fitness gates
```yaml
# In Graph.yaml fitness_function
fitness_gates:
  correctness:
    type: hard
    metric: hermes_verify_all_pass_rate
    threshold: 1.0
  efficiency:
    type: soft
    metric: tokens_per_cycle
    target: minimize
  safety:
    type: hard
    metric: sandbox_escape_count
    threshold: 0
  diversity:
    type: soft
    metric: embedding_distance_to_archive
    target: maximize
  complexity:
    type: soft
    metric: cyclomatic_complexity
    target: minimize
```

**Extinction Protocol**:
- Trigger: No fitness improvement over 20 generations
- Action: Lineage culling + inject 2 random seed agents

### 2. Radio ArmsgeddonFM
**Fitness Dimensions**:
- Audio quality (PESQ score)
- Content relevance (embedding similarity to prompt)
- Pipeline latency
- Plugin diversity (unique MemoryGraph nodes activated)

**Extinction**: When song diversity drops (repeating patterns), trigger niche preservation on underused genres.

### 3. Paranoidx/Sovereign Systems
**Fitness Dimensions**:
- Security audit score (static + dynamic)
- Uptime / reliability
- Resource efficiency (CPU/RAM per camera)
- Onion service latency

**Extinction**: If any container lineage dominates, force rotation via lineage culling.

## Implementation Patterns

### Fitness Gate Decorator
```python
@fitness_gate(
    hard_gates=[CorrectnessGate(threshold=1.0), SafetyGate(threshold=0)],
    soft_gates=[EfficiencyGate(), DiversityGate(), ComplexityGate()],
    aggregation="weighted_sum",  # or "pareto"
    weights={"correctness": 0.4, "efficiency": 0.2, "safety": 0.2, "diversity": 0.1, "complexity": 0.1}
)
def evaluate_agent(agent, benchmark):
    return agent.run(benchmark)
```

### Extinction Scheduler
```python
class ExtinctionScheduler:
    def __init__(self, archive, config):
        self.archive = archive
        self.config = config
        self.generations_since_improvement = 0
        self.best_fitness = -inf
    
    def check_and_trigger(self, new_fitness):
        if new_fitness > self.best_fitness:
            self.best_fitness = new_fitness
            self.generations_since_improvement = 0
        else:
            self.generations_since_improvement += 1
        
        if self.generations_since_improvement >= self.config.stagnation_window:
            self.trigger_extinction()
            self.generations_since_improvement = 0
    
    def trigger_extinction(self):
        event_type = self.select_extinction_type()
        if event_type == "mass":
            self.archive = mass_extinction(self.archive, keep_ratio=0.3)
        elif event_type == "lineage":
            self.archive = lineage_culling(self.archive)
        elif event_type == "niche":
            self.archive = niche_preservation(self.archive)
        # Log extinction event
        log_extinction(event_type, len(self.archive))
```

## Safety Considerations

| Risk | Mitigation |
|------|------------|
| **Runaway self-modification** | Hard gate: human approval for core architecture changes |
| **Reward hacking** | Multiple independent fitness dimensions + adversarial validation |
| **Extinction too aggressive** | Minimum population size, protected niches, migration fallback |
| **Diversity collapse** | Novelty search component, explicit diversity gate |
| **Catastrophic forgetting** | Elastic weight consolidation, episodic memory replay |

## Integration with Textbook Learning Loop

```python
# After each textbook topic learned:
def textbook_fitness_update(topic, insights, code_examples):
    # 1. Extract concepts → embedding
    concept_embedding = embed(insights)
    
    # 2. Compute novelty vs existing knowledge
    novelty = distance(concept_embedding, knowledge_archive)
    
    # 3. Generate application test
    test_result = run_application_test(code_examples)
    
    # 4. Fitness vector
    fitness = FitnessVector(
        correctness=test_result.passed,
        efficiency=test_result.speed,
        safety=test_result.security,
        novelty=novelty,
        complexity=len(insights),
        generalization=test_result.edge_cases
    )
    
    # 5. Update knowledge archive with extinction check
    knowledge_archive.add(topic, insights, fitness)
    extinction_scheduler.check_and_trigger(fitness)
```

## References
- **Darwin Gödel Machine**: https://arxiv.org/abs/2505.22954 (Zhang et al., 2025)
- **Stagnation-Based Extinction**: https://www.mdpi.com/2076-3417/11/8/3461
- **Open-Ended Evolution**: https://arxiv.org/abs/1901.01753 (POET)
- **Promptbreeder**: https://arxiv.org/abs/2309.16797 (Fernando et al., 2024)
- **OMNI-EPIC**: https://arxiv.org/abs/2502.xxxxx (Faldor et al., 2025)
- **GodModeCoder Graph.yaml**: C:\Users\yusya\GodModeCoder\Graph.yaml
- **Evolution Cycle**: C:\Users\yusya\GodModeCoder\scripts\evolution_cycle.py