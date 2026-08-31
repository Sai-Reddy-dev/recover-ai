from typing import Any


def retry_payment(amount: float) -> dict[str, Any]:
    """
    Simulate a payment retry.
    """

    return {
        "execution_status": "COMPLETED",
        "payment_status": "SUCCESS",
        "amount_recovered": amount,
        "message": "Payment retry succeeded.",
    }


def send_payment_link() -> dict[str, Any]:
    """
    Simulate sending a payment link to the customer.
    """

    return {
        "execution_status": "COMPLETED",
        "payment_status": "PENDING",
        "amount_recovered": 0,
        "message": "Payment link sent to customer.",
    }


def send_reminder() -> dict[str, Any]:
    """
    Simulate sending a payment reminder.
    """

    return {
        "execution_status": "COMPLETED",
        "payment_status": "PENDING",
        "amount_recovered": 0,
        "message": "Payment reminder sent to customer.",
    }


def schedule_retry() -> dict[str, Any]:
    """
    Simulate scheduling a future payment retry.
    """

    return {
        "execution_status": "SCHEDULED",
        "payment_status": "PENDING",
        "amount_recovered": 0,
        "message": "Payment retry scheduled.",
    }


def escalate_to_human() -> dict[str, Any]:
    """
    Simulate escalation to a human recovery team.
    """

    return {
        "execution_status": "ESCALATED",
        "payment_status": "NOT_ATTEMPTED",
        "amount_recovered": 0,
        "message": "Case escalated to human review.",
    }


def execute_recovery_action(
    action: str,
    amount: float,
) -> dict:
    """
    Execute the recovery action approved by the policy layer.

    The AI does not execute actions directly.
    This function only executes actions that have already
    been selected by the recovery policy.
    """

    if action == "RETRY_NOW":
        result = retry_payment(amount)

    elif action == "RETRY_LATER":
        result = schedule_retry()

    elif action == "UPDATE_PAYMENT_METHOD":
        result = {
            "execution_status": "WAITING_FOR_CUSTOMER",
            "payment_status": "PENDING",
            "amount_recovered": 0,
            "message": "Customer must update the payment method.",
        }

    elif action == "SEND_PAYMENT_LINK":
        result = send_payment_link()

    elif action == "SEND_REMINDER":
        result = send_reminder()

    elif action == "ESCALATE":
        result = escalate_to_human()

    elif action == "STOP":
        result = {
            "execution_status": "STOPPED",
            "payment_status": "NOT_ATTEMPTED",
            "amount_recovered": 0,
            "message": "Recovery action stopped by policy.",
        }

    else:
        # Unknown actions are never executed.
        result = escalate_to_human()

    return {
        "action": action,
        **result,
    }


if __name__ == "__main__":
    
    test_actions = [
        ("RETRY_NOW", 4999),
        ("RETRY_LATER", 4999),
        ("UPDATE_PAYMENT_METHOD", 4999),
        ("SEND_PAYMENT_LINK", 4999),
        ("SEND_REMINDER", 4999),
        ("ESCALATE", 4999),
        ("STOP", 4999),
    ]

    print("\nRecovery Workflow Tests")
    print("=" * 60)

    for action, amount in test_actions:

        result = execute_recovery_action(
            action=action,
            amount=amount,
        )

        print(f"\nAction: {action}")
        print(result)
    

    