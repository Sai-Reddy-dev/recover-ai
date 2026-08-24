# RecoverAI

## AI Revenue Recovery Agent

RecoverAI is an AI-powered revenue recovery agent for subscription businesses.

It detects failed subscription payments, calculates revenue at risk, investigates the likely root cause, chooses an appropriate recovery action within predefined guardrails, executes the action, observes the result, and measures the revenue recovered.

---

## Problem

Subscription businesses lose recurring revenue when customer payments fail.

Traditional recovery systems often depend on fixed retry rules. These rules do not consider the reason for failure, customer history, previous recovery attempts, or the potential revenue at risk.

RecoverAI aims to make payment recovery more intelligent and adaptive.

---

## Solution

RecoverAI uses an AI agent to:

1. Detect payment failures
2. Calculate revenue at risk
3. Investigate the likely root cause
4. Decide the next recovery action
5. Validate the action against safety guardrails
6. Execute the approved action
7. Observe the result
8. Retry, recover, escalate, or stop
9. Measure recovered revenue
10. Maintain an audit trail

---

## Core Workflow

Payment Event

↓

Detection

↓

Revenue at Risk

↓

Root-Cause Analysis

↓

AI Recovery Decision

↓

Policy / Guardrail Check

↓

Execute

↓

Observe Result

↓

Recover / Retry / Escalate

↓

Stop

↓

Measure Revenue Recovered

---

## Agent Architecture

RecoverAI separates intelligence from execution.

### AI Agent

Determines:

* Likely root cause
* Risk level
* Recommended recovery action
* Next action after observing a result

### Policy Engine

Determines:

* Whether the action is allowed
* Maximum retry attempts
* Recovery time window
* Other safety constraints

### Action Executor

Performs only approved actions.

This separation allows RecoverAI to combine AI-driven decision making with deterministic safety controls.

---

## MVP Features

* Payment event detection
* Revenue-at-risk calculation
* AI root-cause analysis
* AI recovery decision
* Bounded recovery actions
* Policy and guardrails
* Payment retry simulation
* Result observation
* Recovery loop
* Human escalation
* Revenue measurement
* Audit trail
* Recovery dashboard

---

## Technology Stack

### Frontend

* React

### Backend

* Python
* FastAPI

### Database

* PostgreSQL

### AI

* LLM-based agent

### Development

* VS Code
* Git
* GitHub
* Excalidraw / draw.io

---

## Project Structure

```text
recover-ai/
│
├── frontend/
│
├── backend/
│
├── docs/
│   ├── architecture/
│   ├── workflow/
│   └── decisions/
│
├── README.md
├── .gitignore
└── docker-compose.yml
```

---

## Buildathon MVP

The initial MVP will use a payment simulator to demonstrate the complete recovery loop without depending on a production payment environment.

Example:

```text
Payment Failed
      ↓
₹2,499 Revenue at Risk
      ↓
AI Root-Cause Analysis
      ↓
AI Decision: Wait + Retry
      ↓
Policy: Approved
      ↓
Retry #1 → Failed
      ↓
AI Re-evaluates
      ↓
Retry #2 → Success
      ↓
₹2,499 Revenue Recovered
```

---

## Safety Principles

RecoverAI does not allow the AI agent to directly perform unrestricted actions.

All recovery actions pass through deterministic policies and predefined guardrails.

The agent can only choose from approved recovery actions.

---

## Status

🚧 Currently in the architecture and foundation phase.

---

## Buildathon

Built for the Razorpay AI Revenue Recovery Buildathon.
