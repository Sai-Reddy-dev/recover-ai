from pydantic import BaseModel, Field

class RecoveryAction(BaseModel):
    action: str
    reasoning: str
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


ALLOWED_ACTIONS = {
    "RETRY_NOW",
    "RETRY_LATER",
    "UPDATE_PAYMENT_METHOD",
    "SEND_PAYMENT_LINK",
    "SEND_REMINDER",
    "ESCALATE",
    "STOP",
}

ALLOWED_ROOT_CAUSES = {
    "expired_card",
    "insufficient_funds",
    "temporary_bank_failure",
    "payment_gateway_failure",
    "hard_decline",
    "soft_decline",
    "authentication_failure",
}

def apply_recovery_policy(
    root_cause: str,
    failure_type: str,
    recovery_probability: float,
    failed_attempt_count: int,
    latest_attempt_number: int,
) -> tuple[str, str]:

    # Hard declines should not be automatically retried.
    if root_cause == "hard_decline":
        if failed_attempt_count >= 2:
            return (
                "ESCALATE",
                "Repeated hard decline requires escalation "
                "instead of automatic retry.",
            )

        return (
            "STOP",
            "Hard decline should not be automatically retried.",
        )

    # Expired cards require payment-method correction.
    if root_cause == "expired_card":
        return (
            "UPDATE_PAYMENT_METHOD",
            "The customer's card has expired, so the "
            "payment method should be updated.",
        )

    # Temporary technical failures can be retried later.
    if root_cause in {
        "temporary_bank_failure",
        "payment_gateway_failure",
    }:
        if latest_attempt_number >= 3:
            return (
                "ESCALATE",
                "The temporary failure has already reached "
                "the retry limit.",
            )

        return (
            "RETRY_LATER",
            "The failure appears temporary, so retrying later "
            "is safer than immediate escalation.",
        )

    # Soft declines can usually be retried.
    if root_cause == "soft_decline":
        if latest_attempt_number >= 3:
            return (
                "ESCALATE",
                "The soft decline has reached the retry limit.",
            )

        return (
            "RETRY_NOW",
            "A soft decline is potentially recoverable, "
            "so an immediate retry is appropriate.",
        )

    # Authentication failures usually require customer action.
    if root_cause == "authentication_failure":
        return (
            "SEND_PAYMENT_LINK",
            "Authentication failed, so the customer should "
            "complete payment through a secure payment link.",
        )

    # Insufficient funds should generally be retried later.
    if root_cause == "insufficient_funds":
        return (
            "RETRY_LATER",
            "The payment may succeed later after funds become "
            "available.",
        )

    # Unknown conditions are never automatically executed.
    return (
        "ESCALATE",
        "The failure condition is not covered by the "
        "approved recovery policy.",
    )

def validate_action(action: str) -> str:
    if action not in ALLOWED_ACTIONS:
        return "ESCALATE"

    return action

def decide_recovery_action(
    root_cause: str,
    failure_type: str,
    recovery_probability: float,
    confidence: float,
    failed_attempt_count: int,
    latest_attempt_number: int,
) -> RecoveryAction:

    action, reasoning = apply_recovery_policy(
        root_cause=root_cause,
        failure_type=failure_type,
        recovery_probability=recovery_probability,
        failed_attempt_count=failed_attempt_count,
        latest_attempt_number=latest_attempt_number,
    )

    action = validate_action(action)

    # Reduce confidence when the policy does not recognize
    # the situation.
    if action == "ESCALATE" and root_cause not in ALLOWED_ROOT_CAUSES:
        confidence = min(confidence, 0.5)

    return RecoveryAction(
        action=action,
        reasoning=reasoning,
        confidence=confidence,
    )

if __name__ == "__main__":

    test_cases = [
        {
            "name": "Expired Card",
            "root_cause": "expired_card",
            "failure_type": "CUSTOMER_PAYMENT_METHOD",
            "recovery_probability": 0.40,
            "confidence": 0.95,
            "failed_attempt_count": 1,
            "latest_attempt_number": 1,
        },
        {
            "name": "Temporary Bank Failure",
            "root_cause": "temporary_bank_failure",
            "failure_type": "TECHNICAL_FAILURE",
            "recovery_probability": 0.85,
            "confidence": 0.95,
            "failed_attempt_count": 1,
            "latest_attempt_number": 1,
        },
        {
            "name": "Repeated Hard Decline",
            "root_cause": "hard_decline",
            "failure_type": "HARD_DECLINE",
            "recovery_probability": 0.05,
            "confidence": 0.95,
            "failed_attempt_count": 3,
            "latest_attempt_number": 3,
        },
        {
            "name": "Soft Decline",
            "root_cause": "soft_decline",
            "failure_type": "SOFT_DECLINE",
            "recovery_probability": 0.85,
            "confidence": 0.95,
            "failed_attempt_count": 1,
            "latest_attempt_number": 1,
        },
        {
            "name": "Authentication Failure",
            "root_cause": "authentication_failure",
            "failure_type": "AUTHENTICATION_FAILURE",
            "recovery_probability": 0.70,
            "confidence": 0.95,
            "failed_attempt_count": 1,
            "latest_attempt_number": 1,
        },
        {
            "name": "Hard Decline - Single Attempt",
            "root_cause": "hard_decline",
            "failure_type": "HARD_DECLINE",
            "recovery_probability": 0.90,
            "confidence": 0.95,
            "failed_attempt_count": 1,
            "latest_attempt_number": 1,
        },
        {
            "name": "Hard Decline - High AI Probability",
            "root_cause": "hard_decline",
            "failure_type": "HARD_DECLINE",
            "recovery_probability": 0.99,
            "confidence": 0.99,
            "failed_attempt_count": 3,
            "latest_attempt_number": 3,
        },
        {
            "name": "Temporary Failure - Retry Exhausted",
            "root_cause": "temporary_bank_failure",
            "failure_type": "TECHNICAL_FAILURE",
            "recovery_probability": 0.95,
            "confidence": 0.95,
            "failed_attempt_count": 3,
            "latest_attempt_number": 3,
        },
        {
            "name": "Unknown Root Cause",
            "root_cause": "unknown_failure",
            "failure_type": "UNKNOWN",
            "recovery_probability": 0.80,
            "confidence": 0.90,
            "failed_attempt_count": 1,
            "latest_attempt_number": 1,
        },
    ]

    for test in test_cases:

        result = decide_recovery_action(
            root_cause=test["root_cause"],
            failure_type=test["failure_type"],
            recovery_probability=test["recovery_probability"],
            confidence=test["confidence"],
            failed_attempt_count=test["failed_attempt_count"],
            latest_attempt_number=test["latest_attempt_number"],
        )

        print(f"\n{test['name']}")
        print("-" * 50)
        print(result.model_dump_json(indent=2))

