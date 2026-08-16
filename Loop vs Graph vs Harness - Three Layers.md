Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, graph-engineering, agent-architecture, loop-graph-harness]

C:\Vault\Loop vs Graph vs Harness - Three Layers.md


source: textbook
status: learned
date: 2026-08-10
priority: 10
---

# Loop vs Graph vs Harness — Three Layers

## Summary
The three-layer architecture for AI agent systems (LOOP → GRAPH → HARNESS) provides a structured way to reason about agent complexity, failure modes, and production readiness. Each layer adds capabilities and addresses specific failure patterns.

## The Three Layers

### 1. LOOP — The Control Loop (Innermost)
**Core**: `while not done: plan → act → observe → reflect`

**Characteristics**:
- Single-threaded execution around the LLM
- Bounded by: max steps, token budget, $ cap, progress check
- **Failure mode**: Infinite loops, runaway costs, no stop condition
- **Fix**: Hard stop conditions (max steps, budget, progress)

**When to use**: Simple single-task agents, prototypes, deterministic workflows

### 2. GRAPH — The Execution Graph (Middle)
**Core**: Explicit state machine with nodes (LLM calls, tools, conditionals) and edges (transitions, branching)

**Characteristics**:
- Multi-path execution, conditional routing, parallel branches
- State externalized and resumable (LangGraph, AutoGen)
- **Failure mode**: Unbounded graph growth, deadlocks, state explosion
- **Fix**: Graph depth limits, cycle detection, state serialization

**When to use**: Multi-step workflows, branching logic, human-in-the-loop, resumable processes

### 3. HARNESS — The Production Scaffold (Outermost)
**Core**: Six-layer wrapper around the graph/loop

**Six Harness Layers** (CareerStack):
| Layer | Purpose | Key Mechanisms |
|-------|---------|----------------|
| **Budget & Limits** | Resource bounding | Max steps, tokens, $, timeout, progress check |
| **Guardrails** | Safety & policy | Input/output checks, PII, injection, human gate |
| **Memory & State** | Externalized state | Short-term buffer + long-term store, resumable |
| **Tool Router** | Validated tool execution | Schema validation, sandbox, least-privilege |
| **Reliability** | Fault tolerance | Retry+backoff, circuit breaker, fallback→honesty |
| **Observability** | Debugging & replay | Full trace, deterministic replay, cost tracking |

**Failure mode**: Silent failures, unreproducible bugs, security breaches, cost overruns
**Fix**: Every layer mandatory in production

## Layer Relationships

```
HARNESS (production scaffold)
  └── GRAPH (execution topology)
        └── LOOP (control cycle)
              └── LLM (reasoning core)
```

**Key insight**: Most agent bugs are diagnosed one layer too low.
- If it never stops → LOOP bug (missing stop condition)
- If it takes wrong path → GRAPH bug (routing logic)
- If it leaks data/crashes → HARNESS bug (missing guardrail/budget)

## Practical Mapping to Our Systems

### GodModeCoder Evolution Cycle
| Layer | Implementation |
|-------|----------------|
| **LOOP** | `evolution_cycle.py`: SENSE→THINK→MUTATE→FITNESS→COMMIT→MEMORY→EVOLVE |
| **GRAPH** | `Graph.yaml`: Nodes (gardener, oracle, paranoidx...) + edges (dependencies, triggers) |
| **HARNESS** | `pulse.py` (health), `key_health.py` (budget), cron (scheduling), git (state), Obsidian (observability) |

### Radio ArmsgeddonFM
| Layer | Implementation |
|-------|----------------|
| **LOOP** | Generation cycle: Query → Generate → Mix → Evaluate → Consolidate |
| **GRAPH** | Pipeline: semantic (prompts) → procedural (recipes) → episodic (cycles) |
| **HARNESS** | USB backups, version badges A00→A01, PlugMem consolidation, human gate on deploy |

### Paranoidx / Sovereign Systems
| Layer | Implementation |
|-------|----------------|
| **LOOP** | Registration flow: BIP39 → Invite → Register |
| **GRAPH** | 5-container topology: SMP ↔ Coturn ↔ V2Ray ↔ Tor ↔ XFTP |
| **HARNESS** | License server ($50/mo), SimpleX MQ, Onion services, human gate on camera access |

## Diagnostic Checklist

### When debugging, ask:
1. **LOOP level**: Does it have a hard stop? Max steps? Budget? Progress check?
2. **GRAPH level**: Is routing deterministic? Are cycles detected? Is state serializable?
3. **HARNESS level**: Are all six layers present? Budget? Guardrails? Memory? Router? Reliability? Observability?

### Production readiness = HARNESS complete
- ✅ Budget & limits (max steps, tokens, $)
- ✅ Guardrails (input/output validation, human gate)
- ✅ Memory & state (externalized, resumable)
- ✅ Tool router (schema validation, sandbox)
- ✅ Reliability (retry, circuit breaker, fallback)
- ✅ Observability (full trace, replay, cost)

## Implementation Patterns

### LOOP Pattern (Python)
```python
def bounded_loop(max_steps=10, token_budget=10000, progress_check=True):
    for step in range(max_steps):
        if token_budget <= 0: break
        plan = llm.plan()
        act = llm.act(plan)
        observe = execute(act)
        reflect = llm.reflect(observe)
        if progress_check and not made_progress(reflect): break
        token_budget -= count_tokens(plan, act, observe, reflect)
    return result
```

### GRAPH Pattern (LangGraph)
```python
from langgraph.graph import StateGraph

workflow = StateGraph(AgentState)
workflow.add_node("plan", planner)
workflow.add_node("act", executor)
workflow.add_node("observe", observer)
workflow.add_node("reflect", reflector)
workflow.add_edge("plan", "act")
workflow.add_edge("act", "observe")
workflow.add_edge("observe", "reflect")
workflow.add_conditional_edges("reflect", should_continue)
workflow.set_entry_point("plan")
```

### HARNESS Pattern (Decorator)
```python
@harness(
    budget={"max_steps": 10, "max_tokens": 10000, "max_usd": 5.0},
    guardrails=[InjectionCheck(), PIICheck(), PolicyCheck()],
    memory=ExternalStore(),
    tool_router=SchemaValidatedRouter(sandbox=True),
    reliability=[Retry(backoff=True), CircuitBreaker(), FallbackHonesty()],
    observability=FullTracer(replayable=True)
)
def agent_run(goal):
    # loop/graph logic here
    pass
```

## Anti-Patterns to Avoid

| Anti-Pattern | Layer | Fix |
|--------------|-------|-----|
| Unbounded while loop | LOOP | Add hard stop conditions |
| Free-text multi-agent chatter | GRAPH | Structured graph with typed edges |
| Tools called without validation | HARNESS | Schema-validated router + sandbox |
| State only in prompt | HARNESS | Externalized, resumable store |
| No trace/replay | HARNESS | Full trajectory logging |
| Confident guess on failure | HARNESS | Degrade toward honesty/human |

## References
- CareerStack: [Agent Harness Engineering](https://careerstack.dev/agent-harness-engineering.html)
- CareerStack: [Loop vs Graph vs Harness Engineering](https://careerstack.dev/loop-vs-graph-vs-harness-engineering)
- rari (@0xwhrrari): X posts on three-layer architecture
- LangGraph docs: Explicit graph + state management