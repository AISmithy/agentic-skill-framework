# Agentic Skill Framework

A modular, enterprise-grade platform that enables intelligent agents to **discover, orchestrate, and execute reusable skills** with built-in governance, observability, and resilience.

---

## Architecture Overview

The framework follows a **Microkernel + Service-Oriented** architecture pattern. A central orchestration core manages planning, routing, policy enforcement, and execution coordination, while independently deployable skills act as plug-ins.

```
+----------------------------------------------------------------------------------+
|                              EXPERIENCE LAYER                                    |
|            Web UI  |  Chat Interface  |  API / SDK / CLI                        |
+-------------------------------------+--------------------------------------------+
                                      |
                                      v
+----------------------------------------------------------------------------------+
|                         AGENT ORCHESTRATION LAYER                                |
|   Goal Interpreter | Planner | Skill Router | Workflow Engine | Context Manager  |
|                     Reflection / Retry / Recovery Manager                        |
+-----------------------------+-----------------------------+----------------------+
                              |                             |
                              v                             v
+------------------------------------------------+ +---------------------------+
|            SKILL LIBRARY LAYER                 | |  KNOWLEDGE & MEMORY LAYER |
|  Registry | Metadata Catalog | Versions | Tags | |  Session | Vector | KB    |
|  Dependencies | Skill Definitions | Owners      | |  History | Artifacts     |
+-----------------------------+------------------+ +-------------+-------------+
                              |                             |
                              +-------------------+---------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------+
|                           SKILL RUNTIME LAYER                                    |
|      Executor | Sandbox | Connectors | Validators | Timeout | Retry | CB        |
+----------------------------------------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------+
|                    ENTERPRISE SYSTEMS / EXTERNAL SERVICES                        |
|          Databases | APIs | SaaS | Files | Messaging | Business Applications     |
+----------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------+
|          CROSS-CUTTING: GOVERNANCE | SECURITY | AUDIT | OBSERVABILITY            |
|      AuthN/AuthZ | Policy Engine | Approval | Audit Logs | Metrics | Traces      |
+----------------------------------------------------------------------------------+
```

---

## Project Structure

```
agentic-skill-framework/
├── main.py                              # App entry point — wires skills + creates FastAPI app
├── pyproject.toml                       # Project metadata and dependencies
├── .env.example                         # Environment variable template
│
├── src/agentic/
│   ├── core/                            # Cross-cutting primitives (no internal deps)
│   │   ├── constants.py                 # Enums: LifecycleStatus, RiskLevel, ExecutionMode ...
│   │   ├── exceptions.py                # Typed exception hierarchy
│   │   ├── result.py                    # Result[T] container for explicit error propagation
│   │   └── config.py                    # Pydantic Settings (env-driven)
│   │
│   ├── layer1_experience/               # Layer 1 — HTTP API Gateway
│   │   ├── app.py                       # FastAPI application factory + lifespan
│   │   ├── middleware/
│   │   │   ├── auth_middleware.py       # JWT extraction and identity injection
│   │   │   └── tracing_middleware.py    # Trace ID propagation per request
│   │   └── routes/
│   │       ├── health.py                # GET /health, /health/ready
│   │       ├── skills.py                # CRUD for /skills
│   │       ├── executions.py            # POST /executions (invoke a skill)
│   │       └── agents.py                # POST /agents/goal (submit a natural-language goal)
│   │
│   ├── layer2_orchestration/            # Layer 2 — Agent Orchestration
│   │   ├── goal_interpreter.py          # Natural language goal → GoalSpec
│   │   ├── planner.py                   # GoalSpec → ordered ExecutionPlan (steps)
│   │   ├── skill_router.py              # PlanStep → best-fit published skill
│   │   ├── workflow_engine.py           # Executes plan steps sequentially
│   │   ├── context_manager.py           # Merges session memory + prior outputs per step
│   │   └── reflection_manager.py        # Evaluates outcomes: ACCEPT / RETRY / REPLAN / ESCALATE
│   │
│   ├── layer3_skill_library/            # Layer 3 — Skill Catalog
│   │   ├── registry.py                  # Thread-safe in-memory skill registry (runtime)
│   │   ├── metadata_catalog.py          # SQLite-backed persistent catalog
│   │   ├── version_manager.py           # Semantic version resolution
│   │   ├── dependency_manager.py        # DAG validation, cycle detection, topo sort
│   │   └── models/
│   │       ├── skill.py                 # SkillDefinition — the canonical skill contract
│   │       └── lifecycle.py             # LifecycleTransition, ApprovalRecord models
│   │
│   ├── layer4_runtime/                  # Layer 4 — Skill Execution
│   │   ├── executor.py                  # Full execution pipeline (authz → policy → sandbox → audit)
│   │   ├── sandbox.py                   # Isolated skill execution wrapper
│   │   ├── connector_manager.py         # HTTP connector pool
│   │   ├── schema_validator.py          # JSON Schema validation for inputs and outputs
│   │   └── resilience/
│   │       ├── retry.py                 # Exponential backoff async retry decorator
│   │       ├── timeout.py               # Async execution timeout context manager
│   │       └── circuit_breaker.py       # Per-skill circuit breaker (Closed/Open/Half-Open)
│   │
│   ├── layer5_memory/                   # Layer 5 — Knowledge & Memory
│   │   ├── session_memory.py            # Scoped in-memory store per agent session
│   │   ├── long_term_memory.py          # SQLite-backed persistent key-value store
│   │   ├── vector_store.py              # In-process cosine similarity vector search
│   │   ├── knowledge_base.py            # Structured fact/triple store for agent reasoning
│   │   └── artifact_store.py            # Content-addressed binary artifact store
│   │
│   ├── layer6_governance/               # Layer 6 — Governance & Trust
│   │   ├── authn.py                     # JWT token verification, Identity extraction
│   │   ├── authz.py                     # RBAC permission engine
│   │   ├── policy_engine.py             # Rule evaluation → ALLOW / DENY / REQUIRE_APPROVAL
│   │   ├── safety_filters.py            # Input/output content safety gates
│   │   ├── approval_workflow.py         # Human-in-the-loop approval state machine
│   │   └── audit_log.py                 # Append-only structured audit trail (SQLite)
│   │
│   └── layer7_observability/            # Layer 7 — Observability & Operations
│       ├── logger.py                    # Structured JSON logger (structlog)
│       ├── tracer.py                    # OpenTelemetry-compatible span context (contextvars)
│       ├── metrics.py                   # In-process Counter / Gauge / Histogram registry
│       └── evaluator.py                 # Skill execution quality scorer
│
├── skills/                              # First-party skill plug-ins
│   ├── _base.py                         # BaseSkill ABC — all skills inherit from this
│   ├── summarizer/                      # Document Summarizer (risk: low)
│   ├── web_search/                      # Web Search (risk: low)
│   └── code_executor/                   # Python Code Executor (risk: medium)
│
├── tests/
│   ├── conftest.py                      # Shared fixtures
│   ├── unit/                            # Unit tests per module
│   ├── integration/                     # End-to-end execution pipeline tests
│   └── e2e/                             # HTTP-level API tests (FastAPI TestClient)
│
└── scripts/
    ├── seed_db.py                       # Load built-in skill manifests into SQLite
    └── run_dev.py                       # Uvicorn dev server launcher
```

---

## Seven Architecture Layers

| # | Layer | Responsibility |
|---|---|---|
| 1 | **Experience** | Receive requests, present outcomes — FastAPI gateway, JWT auth, tracing |
| 2 | **Agent Orchestration** | Interpret goals, plan tasks, route skills, manage workflow state |
| 3 | **Skill Library** | Store and expose reusable capabilities — registry, catalog, versioning |
| 4 | **Skill Runtime** | Execute skills safely — sandbox, validation, retry, timeout, circuit breaker |
| 5 | **Knowledge & Memory** | Context retention — session, long-term, vector store, artifacts |
| 6 | **Governance & Trust** | AuthN/AuthZ, policy enforcement, approvals, audit log |
| 7 | **Observability** | Logs, traces, metrics, quality evaluation |

---

## Skill Definition Standard

Every skill conforms to a standard contract (`SkillDefinition`):

```json
{
  "skill_id": "doc.summarize.v1",
  "name": "Document Summarizer",
  "description": "Summarizes uploaded or retrieved documents",
  "category": "knowledge-processing",
  "owner": "ai-platform-team",
  "version": "1.0.0",
  "input_schema": {
    "type": "object",
    "properties": {
      "text": { "type": "string" },
      "max_length": { "type": "integer" }
    },
    "required": ["text"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "summary": { "type": "string" },
      "key_points": { "type": "array" },
      "word_count": { "type": "integer" }
    }
  },
  "execution_mode": "local",
  "permissions": [],
  "risk_level": "low",
  "tags": ["summary", "document", "nlp"],
  "status": "published",
  "sla_targets": {
    "p50_ms": 200,
    "p99_ms": 1000,
    "timeout_ms": 5000
  },
  "audit_classification": "standard"
}
```

### Skill Lifecycle

```
Draft → Tested → Approved → Published → Deprecated → Retired
```

### Risk Classification

| Risk | Examples | Controls |
|---|---|---|
| **Low** | Summarization, search, classification | Standard auth, normal logging |
| **Medium** | Code execution, document creation | Enhanced logging, stronger validation |
| **High** | DB writes, financial actions, external comms | Approval workflow, detailed audit |

---

## Getting Started

### Prerequisites

- Python 3.11+

### Installation

```bash
git clone <repo-url>
cd agentic-skill-framework

pip install -e ".[dev]"
```

### Seed the database with built-in skills

```bash
py -3.12 scripts/seed_db.py
```

### Start the development server

```bash
py -3.12 -m uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

---

## API Reference

All endpoints (except `/health` and `/metrics`) require a `Bearer` token header.

For local development, use the built-in dev token:
```
Authorization: Bearer dev-token
```

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/health/ready` | Readiness check |
| `GET` | `/metrics` | Prometheus-format metrics |

### Skills

| Method | Path | Description |
|---|---|---|
| `GET` | `/skills` | List skills (filter by `category`, `tag`, `query`) |
| `GET` | `/skills/{skill_id}` | Get a specific skill |
| `POST` | `/skills` | Register a new skill |
| `DELETE` | `/skills/{skill_id}` | Remove a skill from the registry |

### Executions

| Method | Path | Description |
|---|---|---|
| `POST` | `/executions` | Invoke a skill directly by `skill_id` |

```bash
curl -X POST http://localhost:8000/executions \
  -H "Authorization: Bearer dev-token" \
  -H "Content-Type: application/json" \
  -d '{
    "skill_id": "doc.summarize.v1",
    "inputs": { "text": "Your document text here..." }
  }'
```

### Agents

| Method | Path | Description |
|---|---|---|
| `POST` | `/agents/goal` | Submit a natural-language goal for autonomous execution |

```bash
curl -X POST http://localhost:8000/agents/goal \
  -H "Authorization: Bearer dev-token" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Summarize the latest policy documents",
    "initial_inputs": { "text": "Policy document content..." }
  }'
```

---

## Writing a New Skill

1. Create a directory under `skills/`:

```
skills/
└── my_skill/
    ├── __init__.py
    ├── manifest.json      # Skill definition contract
    └── skill.py           # Implementation
```

2. Define the manifest (`manifest.json`):

```json
{
  "skill_id": "my.skill.v1",
  "name": "My Skill",
  "description": "Does something useful",
  "category": "general",
  "owner": "my-team",
  "version": "1.0.0",
  "input_schema": {
    "type": "object",
    "properties": { "query": { "type": "string" } },
    "required": ["query"]
  },
  "output_schema": {
    "type": "object",
    "properties": { "result": { "type": "string" } }
  },
  "risk_level": "low",
  "tags": ["general"],
  "status": "published"
}
```

3. Implement the skill (`skill.py`):

```python
import json
from pathlib import Path
from typing import Any
from agentic.layer3_skill_library.models.skill import SkillDefinition
from skills._base import BaseSkill

class MySkill(BaseSkill):
    manifest: SkillDefinition = SkillDefinition.model_validate(
        json.loads((Path(__file__).parent / "manifest.json").read_text())
    )

    async def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        query = inputs.get("query", "")
        return {"result": f"Processed: {query}"}
```

4. Register it in `main.py`:

```python
from skills.my_skill.skill import MySkill

my_skill = MySkill()
skill_instances = {
    my_skill.manifest.skill_id: my_skill,
    # ... other skills
}
```

---

## Governance Model

### Policy Engine

Every skill invocation passes through the policy engine before execution. The engine evaluates rules and returns one of three decisions:

| Decision | Meaning |
|---|---|
| `ALLOW` | Execution proceeds normally |
| `DENY` | Request blocked; `403` returned to caller |
| `REQUIRE_APPROVAL` | Routed to human approval queue; `202` returned |

Built-in rules:
- Retired skills are always denied
- Unpublished skills are denied in production
- High-risk skills require approval unless the caller has the `admin` role

### Roles

| Role | Permissions |
|---|---|
| `admin` | All permissions (`*`) |
| `developer` | `read:skills`, `invoke:skills`, `publish:skills` |
| `operator` | `read:skills`, `invoke:skills` |
| `viewer` | `read:skills` |

### Audit Log

All invocations, policy decisions, and lifecycle transitions are recorded in an append-only SQLite audit log with `event_id`, `actor`, `skill_id`, `outcome`, `duration_ms`, `policy_decision`, and `trace_id`.

---

## Resilience Features

| Feature | Implementation |
|---|---|
| **Retry** | Exponential backoff with configurable max attempts and delay cap |
| **Timeout** | Per-skill `timeout_ms` from SLA targets, enforced via `asyncio.timeout` |
| **Circuit Breaker** | Per-skill Closed/Open/Half-Open state machine; opens after N failures |

Configure via environment variables:

```env
AGENTIC_DEFAULT_TIMEOUT_MS=30000
AGENTIC_DEFAULT_MAX_RETRIES=3
AGENTIC_CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
AGENTIC_CIRCUIT_BREAKER_RECOVERY_TIMEOUT_S=60
```

---

## Observability

### Structured Logging

All framework events emit structured JSON logs via `structlog`:

```json
{"event": "skill_executed", "skill_id": "doc.summarize.v1", "actor": "dev-user", "duration_ms": 12.4, "timestamp": "2026-03-16T10:00:00Z"}
```

### Tracing

OpenTelemetry-compatible spans are created for every skill execution using Python `contextvars`. Each span includes `trace_id`, `span_id`, `duration_ms`, and custom attributes. The `X-Trace-Id` header is propagated through all HTTP responses.

### Metrics

Available at `GET /metrics` in Prometheus text format:

| Metric | Type | Description |
|---|---|---|
| `skill_executions_total` | Counter | Total skill invocations |
| `skill_execution_duration_ms` | Histogram | Execution duration distribution |
| `circuit_breaker_state_<skill_id>` | Gauge | Circuit breaker state (0=closed, 1=open) |
| `active_sessions` | Gauge | Number of active agent sessions |
| `policy_decisions_total` | Counter | Total policy evaluations |

---

## Configuration

All settings are prefixed with `AGENTIC_` and can be set via environment variables or a `.env` file:

| Variable | Default | Description |
|---|---|---|
| `AGENTIC_DB_PATH` | `agentic.db` | SQLite database file path |
| `AGENTIC_SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `AGENTIC_JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `AGENTIC_ENVIRONMENT` | `development` | Runtime environment |
| `AGENTIC_LOG_LEVEL` | `INFO` | Logging level |
| `AGENTIC_DEFAULT_TIMEOUT_MS` | `30000` | Default skill execution timeout |
| `AGENTIC_DEFAULT_MAX_RETRIES` | `3` | Default retry attempts |
| `AGENTIC_CIRCUIT_BREAKER_FAILURE_THRESHOLD` | `5` | Failures before circuit opens |
| `AGENTIC_CIRCUIT_BREAKER_RECOVERY_TIMEOUT_S` | `60` | Seconds before half-open probe |
| `AGENTIC_APPROVAL_EXPIRY_HOURS` | `24` | Hours before approval request expires |

---

## Running Tests

```bash
# All unit tests
py -3.12 -m pytest tests/unit/ -v

# Integration tests (execution pipeline)
py -3.12 -m pytest tests/integration/ -v

# End-to-end API tests
py -3.12 -m pytest tests/e2e/ -v

# All tests
py -3.12 -m pytest tests/ -v
```

---

## Built-in Skills

| Skill ID | Name | Category | Risk | Description |
|---|---|---|---|---|
| `doc.summarize.v1` | Document Summarizer | knowledge-processing | low | Extracts summaries and key points from text |
| `web.search.v1` | Web Search | search | low | Searches the web and returns ranked results |
| `code.execute.v1` | Code Executor | code | medium | Executes sandboxed Python code snippets |

---

## Technology Stack

| Concern | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI |
| Database | SQLite via `aiosqlite` |
| Data validation | Pydantic v2, jsonschema |
| Security | `python-jose` (JWT), RBAC |
| HTTP connectors | `httpx` |
| Observability | `structlog`, in-process OTel-compatible tracer |
| Retry logic | `tenacity` |

---

## Architecture Principles

- **Separation of concerns** — planning, discovery, execution, memory, and governance are strictly separate layers
- **Contract-first skills** — every skill declares input/output schemas before it can run
- **Policy before action** — governance evaluation always precedes execution
- **Everything observable** — all decisions and actions emit telemetry and audit records
- **Version everything** — skills, policies, and connectors are versioned
- **Human-in-the-loop** — high-risk workflows require explicit human approval
- **Loose coupling, strong governance** — skills stay loosely coupled while governance remains centralized
