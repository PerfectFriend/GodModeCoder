Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, graph-engineering, evaluation, llm-eval]
source: textbook
status: learned
date: 2026-08-10
priority: 10
---

# Graph Evaluation Over Prompt Testing

## Summary
Graph-based evaluation frameworks provide more structured, deterministic, and comprehensive assessment of LLM outputs compared to traditional prompt-based testing. Instead of single-turn prompt evaluation, graph evaluation decomposes assessment into a directed acyclic graph (DAG) of evaluation steps with explicit criteria, branching logic, and weighted scoring.

## Key Concepts

### 1. DAG-Based Evaluation (DeepEval DAGMetric)
- **Root nodes**: Task extraction (e.g., "extract all headings")
- **Judgement nodes**: Binary (yes/no) or Non-binary (multi-level) criteria
- **Verdict nodes**: Score assignments based on judgement outcomes
- **Edges**: Define evaluation flow and dependencies

### 2. Evaluation Layers (Arize)
| Layer | Purpose | Example |
|-------|---------|---------|
| Code checks | Deterministic validation | JSON schema, regex, type checking |
| LLM-as-Judge | Rubric-based scoring | Faithfulness, relevance, hallucination |
| Human review | Ground truth calibration | Expert annotation on sampled outputs |
| Production signals | Real-world feedback | User ratings, retry rates, latency |

### 3. Graph Evaluation Advantages
- **Deterministic**: Same input → same evaluation path
- **Composable**: Reuse subgraphs across evaluations
- **Explainable**: Trace exactly why a score was given
- **Scalable**: Parallel evaluation of independent branches
- **Versionable**: Git-trackable evaluation graphs

## Practical Implementation

### DeepEval DAGMetric Example
```python
from deepeval.metrics.dag import DeepAcyclicGraph, TaskNode, BinaryJudgementNode, NonBinaryJudgementNode, VerdictNode
from deepeval.metrics import DAGMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

# Define evaluation graph
extract_headings = TaskNode(
    instructions="Extract all headings in actual_output",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
    output_label="Summary headings"
)

has_all_sections = BinaryJudgementNode(
    criteria="Does the summary contain intro, body, conclusion?",
    children=[
        VerdictNode(verdict=False, score=0),
        VerdictNode(verdict=True, child=correct_order_node)
    ]
)

correct_order = NonBinaryJudgementNode(
    criteria="Are headings in correct order: intro → body → conclusion?",
    children=[
        VerdictNode(verdict="Yes", score=10),
        VerdictNode(verdict="Two out of order", score=4),
        VerdictNode(verdict="All out of order", score=2)
    ]
)

dag = DeepAcyclicGraph(root_nodes=[extract_headings])
metric = DAGMetric(name="Format Correctness", dag=dag)
```

### LangGraph Agent Evaluation (2026)
- **Graph topology = evaluation honesty**: Tracer captures node_id spans
- **Conditional-edge routing**: Evaluate decision nodes separately
- **Span-based evaluation**: Each graph node produces evaluatable span

## Application to Our Stack

### 1. GodModeCoder Evolution Fitness Gates
Replace simple pass/fail with DAG-based fitness:
- Node: Code compiles → Verdict: 0/1
- Node: Tests pass → Verdict: 0/1  
- Node: Complexity < threshold → Score 0-10
- Node: Documentation coverage → Score 0-5
- **Aggregate**: Weighted sum → fitness score

### 2. Radio ArmsgeddonFM Quality Control
- **Song generation DAG**: Structure → Lyrics → Melody → Mix → Master
- **Each node**: LLM-as-Judge with specific rubric
- **Failure branches**: Auto-retry with corrected prompt

### 3. Paranoidx/Sovereign Systems Verification
- **Security audit graph**: Static analysis → Dependency check → Runtime test → Penetration test
- **Each step**: Deterministic tool + LLM review
- **Evidence chain**: Cryptographic proof of each evaluation step

### 4. Textbook Learning Validation
- **Self-evaluation DAG**: 
  1. Extract key concepts from learned material
  2. Verify concept coverage vs source
  3. Generate application example
  4. Test example executes
  5. Score: 0-100% mastery

## Tools & Frameworks
| Tool | Strength | Use Case |
|------|----------|----------|
| **DeepEval DAGMetric** | Structured LLM eval | Prompt quality, output format |
| **LangGraph + LangSmith** | Agent graph tracing | Multi-step agent evaluation |
| **Promptfoo** | A/B prompt testing | Prompt optimization |
| **Opik** | Experiment tracking | LLM eval experiment mgmt |
| **Evidently AI** | Production monitoring | Drift detection, data quality |

## Next Steps for Implementation
1. **Add DAG fitness to `pulse.py`** — replace boolean alive/dead with scored fitness
2. **Create `evaluation_graphs/` folder** — store DAG definitions as YAML/JSON
3. **Integrate with `evolution_cycle.py`** — mutation acceptance based on graph score delta
4. **Build evaluation dashboard in Obsidian** — Dataview queries over evaluation results
5. **Add to textbook learning loop** — self-evaluation after each topic

## References
- DeepEval DAGMetric: https://github.com/confident-ai/deepeval
- LangGraph Evaluation: https://futureagi.com/blog/langgraph-agent-evaluation-2026/
- Arize LLM Evaluation Guide: https://arize.com/resources/llm-evaluation/
- Graph Reasoning Benchmark: https://arxiv.org/html/2402.01805v4