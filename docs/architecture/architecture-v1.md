# RecoverAI Architecture v1

## Overview

RecoverAI is designed as an AI-driven revenue recovery system for subscription businesses.

The architecture separates AI decision making from deterministic policy enforcement and action execution.

## High-Level Components

```text
React Dashboard
       |
       v
FastAPI Backend
       |
       v
Recovery Orchestrator
       |
       +------------------+
       |                  |
       v                  v
AI Recovery Agent    PostgreSQL
       |
       v
Policy / Guardrail Engine
       |
       v
Action Executor
       |
       +--------------------+
       |                    |
       v                    v
Payment Simulator     Notification / Escalation
       |
       v
Result Observer
       |
       v
Recovery Orchestrator
       |
       v
Revenue Measurement
       |
       v
PostgreSQL
```

## Core Components

### React Dashboard

Provides visibility into:

* Revenue at risk
* Revenue recovered
* Recovery rate
* Active recovery cases
* Agent decisions
* Recovery timelines
* Audit logs

### FastAPI Backend

Responsible for:

* Receiving payment events
* Exposing application APIs
* Coordinating recovery workflows
* Reading and writing application data

### Recovery Orchestrator

Controls the recovery lifecycle:

```text
Detect
→ Investigate
→ Decide
→ Validate
→ Execute
→ Observe
→ Decide Again
```

### AI Recovery Agent

Responsible for intelligent reasoning:

* Root-cause analysis
* Risk assessment
* Recovery strategy selection
* Re-evaluation after failed actions

### Policy Engine

Provides deterministic safety controls:

* Maximum retries
* Allowed actions
* Recovery window
* Escalation rules

### Action Executor

Executes only actions approved by the policy engine.

### Payment Simulator

Provides a controlled environment for the buildathon MVP.

It can simulate payment outcomes such as:

* Success
* Insufficient funds
* Expired card
* Bank decline
* Temporary failure

### Result Observer

Processes the result of recovery actions and feeds the outcome back into the recovery orchestrator.

### PostgreSQL

Stores:

* Customers
* Subscriptions
* Payments
* Recovery cases
* Agent decisions
* Actions
* Results
* Audit logs

## Safety Principle

The AI agent does not directly control payment operations.

The execution path is:

```text
AI Decision
    ↓
Policy Validation
    ↓
Approved Action
    ↓
Executor
```

This provides bounded autonomy.

## Buildathon MVP

The first implementation will prioritize a single complete recovery loop over broad functionality.

The primary demonstration is:

```text
Payment Failure
→ AI Investigation
→ Recovery Decision
→ Policy Validation
→ Retry
→ Observe
→ Re-evaluate
→ Successful Recovery
→ Revenue Measurement
```
