Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, mcp, resources, tools, prompts, patterns, mcp-protocol, agent-workflows]
source: textbook
status: learned
date: 2026-08-10
priority: 9
---

# MCP Resource/Tool/Prompt Patterns

## Summary
MCP (Model Context Protocol) defines three primitives that AI agents can use: **Tools** (model-controlled actions), **Resources** (application-controlled data), and **Prompts** (user-controlled reusable workflows). Understanding when and how to use each primitive is critical for building robust, maintainable agent systems.

## The Three MCP Primitives

### 1. Tools — Model-Controlled Actions
**Purpose**: Execute actions with side effects (write, compute, call APIs).
**Control**: The model decides **when** and **how** to call.
**Schema**: JSON Schema for input validation.

```json
{
  "name": "kb_search",
  "description": "Search knowledge base",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string"},
      "limit": {"type": "integer", "default": 10}
    },
    "required": ["query"]
  }
}
```

**Best for**: Mutations, external API calls, computations, file operations.

### 2. Resources — Application-Controlled Data
**Purpose**: Expose structured data (files, DB rows, API responses) that the application controls.
**Control**: The application decides **what** data is available; model can only read.
**URI-based**: `resource://scheme/path?params`

```json
{
  "uri": "kb://notes/decisions/001",
  "name": "ADR-001: Container Orchestration",
  "mimeType": "text/markdown",
  "description": "Architecture decision record"
}
```

**Best for**: Static/reference data, large documents, database views, file contents.

### 3. Prompts — User-Controlled Reusable Workflows
**Purpose**: Parameterized templates that guide the model through multi-step workflows.
**Control**: The **user** (or agent orchestration layer) invokes them explicitly.
**Template**: String with `{{parameter}}` placeholders.

```json
{
  "name": "create-decision-record",
  "description": "Create a new Architecture Decision Record",
  "arguments": [
    {"name": "topic", "description": "Decision topic", "required": true},
    {"name": "options", "description": "JSON array of options", "required": true}
  ]
}
```

**Best for**: Standardized procedures, onboarding, complex multi-tool sequences.

## Comparison Matrix

| Aspect | Tools | Resources | Prompts |
|--------|-------|-----------|---------|
| **Who controls** | Model | Application | User/Orchestrator |
| **Side effects** | Yes (write) | No (read-only) | Indirect (via tools) |
| **Data size** | Small (args) | Large (docs, blobs) | Medium (templates) |
| **Discovery** | `list_tools` | `list_resources` | `list_prompts` |
| **Invocation** | `call_tool` | `read_resource` | `get_prompt` → then execute |

## Design Patterns

### Pattern 1: Resource as Context Provider
```python
# Agent starts run by reading key resources
async def load_context(agent):
    # Read static reference data (no tool call needed)
    conventions = await agent.mcp.read_resource("kb://conventio
C:\Vault\MCP Resource Tool Prompt Patterns.md


ns/coding-style")
    decisions = await agent.mcp.read_resource("kb://decisions/current")
    
    # Then use tools for dynamic queries
    relevant = await agent.mcp.call_tool("kb_search", {"query": goal})
    return {"conventions": conventions, "decisions": decisions, "search": relevant}
```

### Pattern 2: Prompt as Workflow Orchestrator
```json
{
  "name": "evolution-cycle",
  "description": "Run one GodModeCoder evolution cycle",
  "arguments": [
    {"name": "generation", "type": "integer", "required": true},
    {"name": "focus_area", "type": "string", "enum": ["fitness", "diversity", "extinction"]}
  ]
}
```

**Prompt Template** (returned by `get_prompt`):
```
You are running GodModeCoder evolution generation {{generation}} with focus on {{focus_area}}.

Follow this exact sequence:
1. SENSE: Call kb_search for "current evolution state" and pulse check
2. THINK: Analyze gaps using analyze_gaps tool
3. MUTATE: Propose code changes via write_tool
4. FITNESS: Run hermes-verify-all.py via terminal tool
5. COMMIT: If fitness passes, git commit with message "gen-{{generation}}: ..."
6. MEMORY: Create decision record in kb://decisions/gen-{{generation}}.md
7. EVOLVE: Update graph.yaml if topology changed

Use ONLY these tools: kb_search, pulse_check, analyze_gaps, terminal, git.
Report each step result before proceeding.
```

### Pattern 3: Resource Templates for Parameterized Access
```json
{
  "uriTemplate": "kb://notes/{folder}/{id}",
  "name": "Knowledge Base Note",
  "mimeType": "text/markdown",
  "description": "Access any note by folder and ID"
}
```

**Usage**: Agent reads `kb://notes/decisions/001` → gets ADR-001 content.

## Anti-Patterns & Fixes

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Tool for everything** | Model overwhelmed, no structure | Use Resources for static data, Prompts for workflows |
| **Huge tool schemas** | Validation errors, confusion | Split into focused tools + resource templates |
| **Prompt does too much** | Brittle, hard to debug | Decompose into smaller prompts + tools |
| **Resource for dynamic data** | Stale data | Use Tools for real-time queries |
| **No prompt versioning** | Breaking changes silently | Version prompts: `create-decision-record/v2` |

## MCP Server Implementation Patterns

### 1. Tool Registration (Python SDK)
```python
from mcp import Server, Tool

server = Server("knowledge-base")

@server.tool()
async def kb_search(query: str, limit: int = 10) -> list[dict]:
    """Search knowledge base notes"""
    return await search_notes(query, limit)

@server.tool()
async def kb_create(path: str, content: str, overwrite: bool = False) -> dict:
    """Create new note"""
    return await create_note(path, content, overwrite)
```

### 2. Resource Registration
```python
from mcp import Resource

@server.resource("kb://notes/{folder}/{id}")
async def get_note(folder: str, id: str) -> Resource:
    content = await read_note(folder, id)
    return Resource(
        uri=f"kb://notes/{folder}/{id}",
        mimeType="text/markdown",
        text=content
    )

@server.resource("kb://conventions/{name}")
async def get_convention(name: str) -> Resource:
    content = await read_convention(name)
    return Resource(uri=f"kb://conventions/{name}", text=content)
```

### 3. Prompt Registration
```python
from mcp import Prompt

@server.prompt()
async def create_decision_record(topic: str, options: list[dict]) -> Prompt:
    return Prompt(
        name="create-decision-record",
        description="Create ADR with structured template",
        arguments=[
            {"name": "topic", "required": True},
            {"name": "options", "required": True}
        ],
        messages=[
            {"role": "user", "content": f"""
Create an Architecture Decision Record for: {topic}

Options:
{json.dumps(options, indent=2)}

Use this template:
---
id: "adr-{{next_id}}"
type: "decision"
status: "proposed"
tags: [architecture, {{topic_tags}}]
created: "{{today}}"
---

# Decision: {{topic}}

## Context
...

## Decision
...

## Rationale
...

## Consequences
...
"""}]
    )
```

## Integration with Our Systems

### GodModeCoder MCP Server
```python
# mcp_servers/godmodecoder/server.py
server = Server("godmodecoder")

# TOOLS
@server.tool()
async def pulse_check() -> dict: ...

@server.tool()
async def evolution_cycle(generation: int, focus: str) -> dict: ...

@server.tool()
async def analyze_gaps() -> dict: ...

@server.tool()
async def git_commit(message: str) -> dict: ...

# RESOURCES
@server.resource("gm://graph/current")
async def get_graph() -> Resource: ...

@server.resource("gm://fitness/current")
async def get_fitness() -> Resource: ...

@server.resource("gm://archive/{generation}")
async def get_archive(generation: int) -> Resource: ...

# PROMPTS
@server.prompt()
async def run_evolution_cycle(generation: int, focus: str) -> Prompt: ...

@server.prompt()
async def diagnose_stagnation() -> Prompt: ...

@server.prompt()
async def propose_extinction(extinction_type: str) -> Prompt: ...
```

### Radio ArmsgeddonFM MCP Server
```python
server = Server("radio-armsgeddonfm")

# TOOLS
@server.tool()
async def generate_song(prompt: str, style: str) -> dict: ...

@server.tool()
async def evaluate_song(audio_path: str) -> dict: ...

@server.tool()
async def consolidate_memory(cycle_data: dict) -> dict: ...

# RESOURCES
@server.resource("radio://prompts/{style}")
async def get_prompt_template(style: str) -> Resource: ...

@server.resource("radio://catalog/{song_id}")
async def get_song_metadata(song_id: str) -> Resource: ...

@server.resource("radio://plugmem/state")
async def get_plugmem_state() -> Resource: ...

# PROMPTS
@server.prompt()
async def daily_generation_cycle(date: str) -> Prompt: ...

@server.prompt()
async def evaluate_and_consolidate(cycle: int) -> Prompt: ...
```

## Best Practices

| Practice | Reason |
|----------|--------|
| **Name consistently** | `namespace://resource-type/{param}` |
| **Version prompts** | `workflow/v2`, `workflow/v3` |
| **Document schemas** | OpenAPI-style descriptions for tools |
| **Limit resource size** | Chunk large docs, use pagination |
| **Cache resources** | Reduce vault I/O |
| **Validate tool inputs** | JSON Schema + custom validators |
| **Log all invocations** | Audit trail for agent actions |

## Testing MCP Primitives

```python
async def test_mcp_primitives():
    client = MCPClient("knowledge-base")
    
    # Test Tools
    tools = await client.list_tools()
    assert "kb_search" in [t.name for t in tools]
    
    result = await client.call_tool("kb_search", {"query": "fitness gates"})
    assert len(result) > 0
    
    # Test Resources
    resources = await client.list_resources()
    assert any(r.uri.startswith("kb://conventions/") for r in resources)
    
    note = await client.read_resource("kb://conventions/coding-style")
    assert "coding-style" in note.text
    
    # Test Prompts
    prompts = await client.list_prompts()
    assert "create-decision-record" in [p.name for p in prompts]
    
    prompt = await client.get_prompt("create-decision-record", {
        "topic": "Test Decision",
        "options": [{"id": "a", "desc": "Option A"}]
    })
    assert "ADR" in prompt.messages[0].content
```

## References
- **MCP Spec**: https://modelcontextprotocol.io/specification
- **Zuplo MCP Prompts**: https://zuplo.com/blog/mcp-server-prompts
- **AWS Heroes**: https://dev.to/aws-heroes/mcp-prompts-and-resources-the-primitives-youre-not-using-3oo1
- **Medium**: https://medium.com/@laurentkubaski/mcp-prompts-explained-including-how-to-actually-use-them-9db13d69d7e2
- **Codesignal**: https://codesignal.com/learn/courses/developing-and-integrating-a-mcp-server-in-python