MAX_RETRIES = 2
MAX_MESSAGES_PER_WEEK = 2
COOLDOWN_MINUTES = 30

STOP_ROOT_CAUSES = {
    "hard_decline",
}

COMMUNICATION_ACTIONS = {
    "SEND_PAYMENT_LINK",
    "SEND_REMINDER",
}

from datetime import datetime, timedelta, timezone


from pydantic import BaseModel


class GuardrailResult(BaseModel):
    approved: bool
    action: str
    reason: str

def check_retry_limit(
    action: str,
    retry_count: int,
) -> GuardrailResult:

    if action not in {"RETRY_NOW", "RETRY_LATER"}:
        return GuardrailResult(
            approved=True,
            action=action,
            reason="Action does not require retry validation.",
        )

    if retry_count >= MAX_RETRIES:
        return GuardrailResult(
            approved=False,
            action="STOP",
            reason="Maximum retry limit reached.",
        )

    return GuardrailResult(
        approved=True,
        action=action,
        reason="Retry is within the allowed retry limit.",
    )

def check_stop_conditions(
    action: str,
    root_cause: str,
    payment_recovered: bool,
    customer_opted_out: bool,
) -> GuardrailResult:

    if payment_recovered:
        return GuardrailResult(
            approved=False,
            action="STOP",
            reason="Payment already recovered.",
        )

    if customer_opted_out:
        return GuardrailResult(
            approved=False,
            action="STOP",
            reason="Customer has opted out.",
        )

    if root_cause in STOP_ROOT_CAUSES:
        return GuardrailResult(
            approved=False,
            action="ESCALATE",
            reason="Hard decline requires escalation or stopping recovery.",
        )

    return GuardrailResult(
        approved=True,
        action=action,
        reason="No stop condition detected.",
    )

def get_retry_count(connection, subscription_id):
    query = """
        SELECT COUNT(*)
        FROM payment_attempts
        WHERE subscription_id = %s
            AND status = 'failed';
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (subscription_id,),
        )

        row = cursor.fetchone()

    return row[0]

def get_last_payment_attempt(connection, subscription_id):
    query = """
        SELECT
            status,
            attempted_at
        FROM payment_attempts
        WHERE subscription_id = %s
        ORDER BY attempted_at DESC
        LIMIT 1;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (subscription_id,),
        )

        return cursor.fetchone()

def get_recovery_case_id(connection, subscription_id):
    query = """
        SELECT id
        FROM recovery_cases
        WHERE subscription_id = %s
          AND status = 'active'
        ORDER BY opened_at DESC
        LIMIT 1;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (subscription_id,),
        )

        row = cursor.fetchone()

    if not row:
        raise RuntimeError(
            f"No active recovery case found for subscription "
            f"{subscription_id}"
        )

    return row[0]


def get_or_create_recovery_case(
    connection,
    subscription_id,
    revenue_at_risk,
    priority,
):
    """
    Return the existing active recovery case.

    If no active recovery case exists, create a new one
    using the latest failed payment attempt.
    """

    # 1. Check for an existing active case
    query = """
        SELECT id
        FROM recovery_cases
        WHERE subscription_id = %s
          AND status = 'active'
        ORDER BY opened_at DESC
        LIMIT 1;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (subscription_id,),
        )

        row = cursor.fetchone()

    if row:
        return row[0]

    # 2. Find the latest failed payment
    query = """
        SELECT id
        FROM payment_attempts
        WHERE subscription_id = %s
          AND status = 'failed'
        ORDER BY attempted_at DESC
        LIMIT 1;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (subscription_id,),
        )

        payment_row = cursor.fetchone()

    if not payment_row:
        raise RuntimeError(
            f"No failed payment found for subscription "
            f"{subscription_id}"
        )

    trigger_payment_id = payment_row[0]

    # 3. Create a new recovery case
    query = """
        INSERT INTO recovery_cases (
            id,
            customer_id,
            subscription_id,
            trigger_payment_id,
            revenue_at_risk,
            status,
            priority,
            retry_count,
            opened_at
        )
        SELECT
            gen_random_uuid(),
            s.customer_id,
            s.id,
            %s,
            %s,
            'active',
            %s,
            0,
            NOW()
        FROM subscriptions s
        WHERE s.id = %s
        RETURNING id;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                trigger_payment_id,
                revenue_at_risk,
                priority.lower(),
                subscription_id,
            ),
        )

        new_case = cursor.fetchone()

    if not new_case:
        raise RuntimeError(
            f"Unable to create recovery case for subscription "
            f"{subscription_id}"
        )

    connection.commit()

    return new_case[0]


def get_message_count_last_week(
    connection,
    recovery_case_id,
):
    query = """
        SELECT COUNT(*)
        FROM audit_logs
        WHERE recovery_case_id = %s
          AND event_type IN (
              'SEND_PAYMENT_LINK',
              'SEND_REMINDER'
          )
          AND created_at >= %s;
    """

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                recovery_case_id,
                cutoff,
            ),
        )

        row = cursor.fetchone()

    return row[0]

def check_communication_limit(
    connection,
    recovery_case_id,
    action,
) -> GuardrailResult:

    if action not in COMMUNICATION_ACTIONS:
        return GuardrailResult(
            approved=True,
            action=action,
            reason="Action does not require communication validation.",
        )

    message_count = get_message_count_last_week(
        connection,
        recovery_case_id,
    )

    if message_count >= MAX_MESSAGES_PER_WEEK:
        return GuardrailResult(
            approved=False,
            action="STOP",
            reason="Weekly communication limit reached.",
        )

    return GuardrailResult(
        approved=True,
        action=action,
        reason=(
            f"Communication allowed. "
            f"{message_count}/{MAX_MESSAGES_PER_WEEK} "
            f"messages sent in the last 7 days."
        ),
    )

def check_cooldown(
    connection,
    subscription_id,
    action,
) -> GuardrailResult:

    if action not in {"RETRY_NOW", "RETRY_LATER"}:
        return GuardrailResult(
            approved=True,
            action=action,
            reason="Action does not require cooldown validation.",
        )

    last_attempt = get_last_payment_attempt(
        connection,
        subscription_id,
    )

    if not last_attempt:
        return GuardrailResult(
            approved=True,
            action=action,
            reason="No previous payment attempt found.",
        )

    status, attempted_at = last_attempt

    now = datetime.now(timezone.utc)

    elapsed = now - attempted_at

    cooldown = timedelta(
        minutes=COOLDOWN_MINUTES
    )

    if elapsed < cooldown:
        return GuardrailResult(
            approved=False,
            action="STOP",
            reason=(
                "Payment retry is within the cooldown period."
            ),
        )

    return GuardrailResult(
        approved=True,
        action=action,
        reason=(
            "Cooldown period has elapsed; retry is allowed."
        ),
    )

def validate_recovery_action(
    connection,
    subscription_id,
    recovery_case_id,
    action,
    root_cause,
    retry_count,
    payment_recovered=False,
    customer_opted_out=False,
) -> GuardrailResult:

    # 1. Stop conditions
    result = check_stop_conditions(
        action=action,
        root_cause=root_cause,
        payment_recovered=payment_recovered,
        customer_opted_out=customer_opted_out,
    )

    if not result.approved:
        return result

    # 2. Retry limit
    result = check_retry_limit(
        action=action,
        retry_count=retry_count,
    )

    if not result.approved:
        return result

    # 3. Communication limit
    result = check_communication_limit(
        connection=connection,
        recovery_case_id=recovery_case_id,
        action=action,
    )

    if not result.approved:
        return result

    # 4. Cooldown
    result = check_cooldown(
        connection=connection,
        subscription_id=subscription_id,
        action=action,
    )

    if not result.approved:
        return result

    return GuardrailResult(
        approved=True,
        action=action,
        reason="Recovery action passed all guardrail checks.",
    )



if __name__ == "__main__":

    from app.database import get_connection

    connection = get_connection()

    try:
        subscription_id = (
            "abb4d858-dca5-444c-8a04-af38d6992483"
        )

        recovery_case_id = get_recovery_case_id(
            connection,
            subscription_id,
        )

        print(
            "Subscription:",
            subscription_id,
        )

        print(
            "Recovery case:",
            recovery_case_id,
        )

    finally:
        connection.close()

