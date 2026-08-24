# RecoverAI Architecture Decisions

## ADR-001: Use FastAPI for the Backend

### Decision

Use Python FastAPI for the RecoverAI backend.

### Reason

The project heavily depends on AI/LLM orchestration, structured data processing, and Python-based agent logic.

---

## ADR-002: Use PostgreSQL

### Decision

Use PostgreSQL as the primary database.

### Reason

RecoverAI needs relational storage for customers, subscriptions, payments, recovery cases, actions, decisions, and audit logs.

---

## ADR-003: Separate AI from Execution

### Decision

The AI agent cannot directly execute payment actions.

### Reason

AI decisions must pass through deterministic safety policies before execution.

```text
AI
↓
Policy
↓
Executor
```

This provides bounded autonomy.

---

## ADR-004: Use a Payment Simulator for the MVP

### Decision

Use a payment simulator during the initial buildathon implementation.

### Reason

The simulator allows us to reliably demonstrate the complete recovery loop without depending on a production payment environment.

The executor interface can later be connected to real payment infrastructure.

---

## ADR-005: Prioritize One Complete Agent Loop

### Decision

Build one complete end-to-end recovery scenario before adding additional recovery strategies.

### Reason

The buildathon evaluation should clearly demonstrate autonomous investigation, decision making, bounded execution, observation, and recovery.

Breadth is less important than demonstrating a complete and reliable agent loop.
