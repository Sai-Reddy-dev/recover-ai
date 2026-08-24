# RecoverAI Recovery Workflow v1

## Primary Recovery Scenario

A customer has a ₹2,499 monthly subscription.

The payment fails because of insufficient funds.

RecoverAI should automatically manage the recovery process.

## Workflow

### 1. Payment Event

A payment failure event enters the system.

```text
payment.failed
```

### 2. Recovery Case

The backend creates a recovery case.

```text
Case: RC-1001
Customer: Rahul
Amount: ₹2,499
Status: ACTIVE
```

### 3. Revenue Risk

The system calculates:

```text
Revenue at Risk = ₹2,499
```

### 4. Investigation

The AI receives:

* Payment information
* Failure reason
* Customer history
* Subscription information
* Previous recovery attempts

### 5. Decision

The AI produces a structured recovery recommendation.

Example:

```text
Root Cause: Insufficient Funds
Confidence: 0.91
Action: WAIT_AND_RETRY
```

### 6. Policy Validation

The policy engine checks whether the proposed action is allowed.

Example:

```text
Current retries: 0
Maximum retries: 3
Action: WAIT_AND_RETRY
Result: APPROVED
```

### 7. Execution

The executor performs the approved action.

```text
Retry Payment
```

### 8. Observation

The payment simulator returns:

```text
FAILED
```

### 9. Re-evaluation

The agent receives the new result and evaluates the case again.

If another retry is allowed, the agent can recommend another retry.

### 10. Successful Recovery

The next payment attempt succeeds.

```text
PAYMENT SUCCESS
```

### 11. Stop

The recovery case is closed.

```text
Status: RECOVERED
```

### 12. Revenue Measurement

The system records:

```text
Revenue at Risk: ₹2,499
Revenue Recovered: ₹2,499
```

### 13. Audit Trail

All major events and decisions are stored for later inspection.

## Failure Path

If the maximum retry limit is reached:

```text
Retry #1 → FAILED
Retry #2 → FAILED
Retry #3 → FAILED
        ↓
ESCALATE
        ↓
STOP
```

The system must never retry indefinitely.
