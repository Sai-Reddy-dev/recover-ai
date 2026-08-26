import os
import uuid

import psycopg
from dotenv import load_dotenv
from faker import Faker


load_dotenv()

fake = Faker("en_IN")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


CUSTOMER_COUNT = 300


def generate_customers(connection):
    customers = []

    for _ in range(CUSTOMER_COUNT):
        customer = {
            "id": uuid.uuid4(),
            "name": fake.name(),
            "email": fake.unique.email(),
            "status": "active",
            "created_at": fake.date_time_between(
                start_date="-2y",
                end_date="now",
            ),
        }

        customers.append(customer)

    with connection.cursor() as cursor:
        for customer in customers:
            cursor.execute(
                """
                INSERT INTO customers
                    (id, name, email, status, created_at)
                VALUES
                    (%(id)s, %(name)s, %(email)s, %(status)s, %(created_at)s)
                """,
                customer,
            )

    connection.commit()

    print(f"Generated {len(customers)} customers.")


SUBSCRIPTION_COUNT = 350

PLANS = [
    ("Basic", 499),
    ("Pro", 1499),
    ("Business", 4999),
    ("Enterprise", 9999),
]

BILLING_CYCLES = [
    "monthly",
    "quarterly",
    "yearly",
]


def generate_subscriptions(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM customers;")
        customer_ids = [row[0] for row in cursor.fetchall()]

    if not customer_ids:
        raise RuntimeError("No customers found. Generate customers first.")

    subscriptions = []

    for _ in range(SUBSCRIPTION_COUNT):
        customer_id = fake.random_element(customer_ids)

        plan_name, amount = fake.random_element(PLANS)

        billing_cycle = fake.random_element(BILLING_CYCLES)

        started_at = fake.date_time_between(
            start_date="-1y",
            end_date="now",
        )

        next_billing_date = fake.date_between(
            start_date="today",
            end_date="+90d",
        )

        status = fake.random_element(
            [
                "active",
                "active",
                "active",
                "past_due",
                "cancelled",
                "paused",
            ]
        )

        subscription = {
            "id": uuid.uuid4(),
            "customer_id": customer_id,
            "plan_name": plan_name,
            "amount": amount,
            "currency": "INR",
            "billing_cycle": billing_cycle,
            "status": status,
            "started_at": started_at,
            "next_billing_date": next_billing_date,
        }

        subscriptions.append(subscription)

    with connection.cursor() as cursor:
        for subscription in subscriptions:
            cursor.execute(
                """
                INSERT INTO subscriptions
                    (
                        id,
                        customer_id,
                        plan_name,
                        amount,
                        currency,
                        billing_cycle,
                        status,
                        started_at,
                        next_billing_date
                    )
                VALUES
                    (
                        %(id)s,
                        %(customer_id)s,
                        %(plan_name)s,
                        %(amount)s,
                        %(currency)s,
                        %(billing_cycle)s,
                        %(status)s,
                        %(started_at)s,
                        %(next_billing_date)s
                    )
                """,
                subscription,
            )

    connection.commit()

    print(f"Generated {len(subscriptions)} subscriptions.")

PAYMENT_ATTEMPT_COUNT = 750

PAYMENT_METHODS = [
    "card",
    "card",
    "card",
    "upi",
    "upi",
    "bank_transfer",
    "wallet",
]

FAILURE_SCENARIOS = [
    {
        "reason": "insufficient_funds",
        "decline_code": "INSUFFICIENT_FUNDS",
    },
    {
        "reason": "expired_card",
        "decline_code": "EXPIRED_CARD",
    },
    {
        "reason": "temporary_bank_failure",
        "decline_code": "BANK_TEMPORARY_FAILURE",
    },
    {
        "reason": "payment_gateway_failure",
        "decline_code": "GATEWAY_ERROR",
    },
    {
        "reason": "hard_decline",
        "decline_code": "HARD_DECLINE",
    },
    {
        "reason": "soft_decline",
        "decline_code": "SOFT_DECLINE",
    },
    {
        "reason": "authentication_failure",
        "decline_code": "AUTHENTICATION_REQUIRED",
    },
]


def generate_payment_attempts(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, amount, currency
            FROM subscriptions
            WHERE status != 'cancelled';
            """
        )

        subscriptions = cursor.fetchall()

    if not subscriptions:
        raise RuntimeError(
            "No usable subscriptions found."
        )

    payments = []

    for _ in range(PAYMENT_ATTEMPT_COUNT):
        subscription_id, amount, currency = fake.random_element(
            subscriptions
        )

        payment_method = fake.random_element(
            PAYMENT_METHODS
        )

        # Around 60% successful payments.
        is_success = fake.random_int(
            min=1,
            max=100,
        ) <= 60

        if is_success:
            status = "success"
            failure_reason = None
            decline_code = None
        else:
            status = "failed"

            failure = fake.random_element(
                FAILURE_SCENARIOS
            )

            failure_reason = failure["reason"]
            decline_code = failure["decline_code"]

        attempt_number = fake.random_int(
            min=1,
            max=3,
        )

        attempted_at = fake.date_time_between(
            start_date="-6m",
            end_date="now",
        )

        payment = {
            "id": uuid.uuid4(),
            "subscription_id": subscription_id,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method,
            "status": status,
            "failure_reason": failure_reason,
            "decline_code": decline_code,
            "attempt_number": attempt_number,
            "attempted_at": attempted_at,
        }

        payments.append(payment)

    with connection.cursor() as cursor:
        for payment in payments:
            cursor.execute(
                """
                INSERT INTO payment_attempts
                (
                    id,
                    subscription_id,
                    amount,
                    currency,
                    payment_method,
                    status,
                    failure_reason,
                    decline_code,
                    attempt_number,
                    attempted_at
                )
                VALUES
                (
                    %(id)s,
                    %(subscription_id)s,
                    %(amount)s,
                    %(currency)s,
                    %(payment_method)s,
                    %(status)s,
                    %(failure_reason)s,
                    %(decline_code)s,
                    %(attempt_number)s,
                    %(attempted_at)s
                )
                """,
                payment,
            )

    connection.commit()

    print(
        f"Generated {len(payments)} payment attempts."
    )

RECOVERY_CASE_COUNT = 200


def generate_recovery_cases(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                p.id,
                p.subscription_id,
                p.amount,
                s.customer_id
            FROM payment_attempts p
            JOIN subscriptions s
                ON p.subscription_id = s.id
            WHERE p.status = 'failed'
            ORDER BY RANDOM()
            LIMIT %s;
            """,
            (RECOVERY_CASE_COUNT,),
        )

        failed_payments = cursor.fetchall()

    if not failed_payments:
        raise RuntimeError(
            "No failed payments found."
        )

    recovery_cases = []

    for (
        payment_id,
        subscription_id,
        amount,
        customer_id,
    ) in failed_payments:

        failure_priority = fake.random_element(
            [
                "low",
                "medium",
                "medium",
                "high",
                "critical",
            ]
        )

        status = fake.random_element(
            [
                "active",
                "active",
                "recovered",
                "failed",
                "escalated",
            ]
        )

        retry_count = fake.random_int(
            min=0,
            max=3,
        )

        opened_at = fake.date_time_between(
            start_date="-30d",
            end_date="now",
        )

        closed_at = None

        if status in [
            "recovered",
            "failed",
            "escalated",
            "stopped",
        ]:
            closed_at = fake.date_time_between(
                start_date=opened_at,
                end_date="now",
            )

        recovery_case = {
            "id": uuid.uuid4(),
            "customer_id": customer_id,
            "subscription_id": subscription_id,
            "trigger_payment_id": payment_id,
            "revenue_at_risk": amount,
            "status": status,
            "priority": failure_priority,
            "retry_count": retry_count,
            "opened_at": opened_at,
            "closed_at": closed_at,
        }

        recovery_cases.append(
            recovery_case
        )

    with connection.cursor() as cursor:
        for case in recovery_cases:
            cursor.execute(
                """
                INSERT INTO recovery_cases
                (
                    id,
                    customer_id,
                    subscription_id,
                    trigger_payment_id,
                    revenue_at_risk,
                    status,
                    priority,
                    retry_count,
                    opened_at,
                    closed_at
                )
                VALUES
                (
                    %(id)s,
                    %(customer_id)s,
                    %(subscription_id)s,
                    %(trigger_payment_id)s,
                    %(revenue_at_risk)s,
                    %(status)s,
                    %(priority)s,
                    %(retry_count)s,
                    %(opened_at)s,
                    %(closed_at)s
                )
                """,
                case,
            )

    connection.commit()

    print(
        f"Generated {len(recovery_cases)} recovery cases."
    )

def generate_agent_decisions(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                rc.id,
                p.failure_reason
            FROM recovery_cases rc
            JOIN payment_attempts p
                ON rc.trigger_payment_id = p.id;
            """
        )

        cases = cursor.fetchall()

    if not cases:
        raise RuntimeError(
            "No recovery cases found."
        )

    decisions = []

    decision_rules = {
        "insufficient_funds": {
            "action": "wait_and_retry",
            "risk": "medium",
            "reason": (
                "Payment failure may be temporary. "
                "Wait before attempting another payment."
            ),
        },
        "expired_card": {
            "action": "request_payment_update",
            "risk": "high",
            "reason": (
                "The payment method appears to be expired. "
                "Customer payment method update is required."
            ),
        },
        "temporary_bank_failure": {
            "action": "wait_and_retry",
            "risk": "medium",
            "reason": (
                "Bank failure appears temporary. "
                "A controlled retry may recover the payment."
            ),
        },
        "payment_gateway_failure": {
            "action": "retry_payment",
            "risk": "medium",
            "reason": (
                "The gateway failure may be transient. "
                "A bounded retry is appropriate."
            ),
        },
        "hard_decline": {
            "action": "stop",
            "risk": "high",
            "reason": (
                "Hard declines should not be repeatedly retried. "
                "Stop automated recovery."
            ),
        },
        "soft_decline": {
            "action": "retry_payment",
            "risk": "medium",
            "reason": (
                "Soft decline may be temporary. "
                "A controlled retry is appropriate."
            ),
        },
        "authentication_failure": {
            "action": "request_payment_update",
            "risk": "high",
            "reason": (
                "Authentication is required before another "
                "successful payment can be expected."
            ),
        },
    }

    for case_id, failure_reason in cases:

        rule = decision_rules.get(
            failure_reason,
            {
                "action": "escalate",
                "risk": "high",
                "reason": (
                    "Unknown failure reason requires "
                    "manual review."
                ),
            },
        )

        confidence = round(
            fake.random.uniform(0.80, 0.98),
            4,
        )

        decision = {
            "id": uuid.uuid4(),
            "recovery_case_id": case_id,
            "root_cause": failure_reason,
            "confidence": confidence,
            "risk_level": rule["risk"],
            "recommended_action": rule["action"],
            "reason": rule["reason"],
        }

        decisions.append(decision)

    with connection.cursor() as cursor:
        for decision in decisions:
            cursor.execute(
                """
                INSERT INTO agent_decisions
                (
                    id,
                    recovery_case_id,
                    root_cause,
                    confidence,
                    risk_level,
                    recommended_action,
                    reason
                )
                VALUES
                (
                    %(id)s,
                    %(recovery_case_id)s,
                    %(root_cause)s,
                    %(confidence)s,
                    %(risk_level)s,
                    %(recommended_action)s,
                    %(reason)s
                )
                """,
                decision,
            )

    connection.commit()

    print(
        f"Generated {len(decisions)} agent decisions."
    )

def generate_recovery_actions(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                ad.id,
                ad.recovery_case_id,
                ad.recommended_action,
                rc.revenue_at_risk
            FROM agent_decisions ad
            JOIN recovery_cases rc
                ON ad.recovery_case_id = rc.id;
            """
        )

        decisions = cursor.fetchall()

    if not decisions:
        raise RuntimeError(
            "No agent decisions found."
        )

    actions = []

    for (
        decision_id,
        recovery_case_id,
        recommended_action,
        revenue_at_risk,
    ) in decisions:

        # Default values
        attempt_number = fake.random_int(
            min=1,
            max=3,
        )

        # Stop actions should never execute another payment retry.
        if recommended_action == "stop":

            action_status = "rejected"
            result = "automation_stopped"
            attempt_number = 1

        elif recommended_action == "request_payment_update":

            action_status = fake.random_element(
                [
                    "success",
                    "pending",
                    "failed",
                ]
            )

            if action_status == "success":
                result = "payment_method_update_requested"

            elif action_status == "pending":
                result = "awaiting_customer_update"

            else:
                result = "customer_update_failed"

        elif recommended_action in [
            "retry_payment",
            "wait_and_retry",
        ]:

            action_status = fake.random_element(
                [
                    "success",
                    "success",
                    "success",
                    "failed",
                ]
            )

            if action_status == "success":

                recovered = fake.random_int(
                    min=1,
                    max=100,
                ) <= 65

                if recovered:
                    result = "payment_recovered"
                else:
                    result = "payment_still_failed"

            else:
                result = "retry_execution_failed"

        else:

            action_status = "pending"
            result = "manual_review_required"

        executed_at = fake.date_time_between(
            start_date="-30d",
            end_date="now",
        )

        action = {
            "id": uuid.uuid4(),
            "recovery_case_id": recovery_case_id,
            "agent_decision_id": decision_id,
            "action_type": recommended_action,
            "status": action_status,
            "attempt_number": attempt_number,
            "executed_at": executed_at,
            "result": result,
        }

        actions.append(action)

    with connection.cursor() as cursor:
        for action in actions:

            cursor.execute(
                """
                INSERT INTO recovery_actions
                (
                    id,
                    recovery_case_id,
                    agent_decision_id,
                    action_type,
                    status,
                    attempt_number,
                    executed_at,
                    result
                )
                VALUES
                (
                    %(id)s,
                    %(recovery_case_id)s,
                    %(agent_decision_id)s,
                    %(action_type)s,
                    %(status)s,
                    %(attempt_number)s,
                    %(executed_at)s,
                    %(result)s
                )
                """,
                action,
            )

    connection.commit()

    print(
        f"Generated {len(actions)} recovery actions."
    )

def generate_audit_logs(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                rc.id,
                rc.revenue_at_risk,
                p.failure_reason,
                ad.recommended_action,
                ra.status,
                ra.result
            FROM recovery_cases rc
            JOIN payment_attempts p
                ON rc.trigger_payment_id = p.id
            LEFT JOIN agent_decisions ad
                ON rc.id = ad.recovery_case_id
            LEFT JOIN recovery_actions ra
                ON rc.id = ra.recovery_case_id;
            """
        )

        cases = cursor.fetchall()

    if not cases:
        raise RuntimeError(
            "No recovery cases found."
        )

    audit_events = []

    for (
        case_id,
        revenue_at_risk,
        failure_reason,
        recommended_action,
        action_status,
        action_result,
    ) in cases:

        base_time = fake.date_time_between(
            start_date="-30d",
            end_date="now",
        )

        events = [
            {
                "actor": "system",
                "event_type": "recovery_case_detected",
                "message": (
                    f"Payment failure detected. "
                    f"Revenue at risk: ₹{revenue_at_risk}."
                ),
                "metadata": {
                    "failure_reason": failure_reason,
                    "revenue_at_risk": float(
                        revenue_at_risk
                    ),
                },
            },
            {
                "actor": "ai_agent",
                "event_type": "root_cause_identified",
                "message": (
                    f"Root cause identified: "
                    f"{failure_reason}."
                ),
                "metadata": {
                    "root_cause": failure_reason,
                },
            },
            {
                "actor": "ai_agent",
                "event_type": "recovery_decision",
                "message": (
                    f"Recommended action: "
                    f"{recommended_action}."
                ),
                "metadata": {
                    "recommended_action": (
                        recommended_action
                    ),
                },
            },
            {
                "actor": "policy_engine",
                "event_type": "policy_evaluation",
                "message": (
                    "Recovery action evaluated "
                    "against execution policy."
                ),
                "metadata": {
                    "action": recommended_action,
                    "policy_result": (
                        "allowed"
                        if recommended_action != "stop"
                        else "blocked"
                    ),
                },
            },
            {
                "actor": "executor",
                "event_type": "action_executed",
                "message": (
                    f"Recovery action executed with "
                    f"status: {action_status}."
                ),
                "metadata": {
                    "action": recommended_action,
                    "status": action_status,
                },
            },
            {
                "actor": "system",
                "event_type": "recovery_result",
                "message": (
                    f"Recovery result: {action_result}."
                ),
                "metadata": {
                    "result": action_result,
                },
            },
        ]

        for index, event in enumerate(events):

            event_time = base_time

            audit_events.append(
                {
                    "id": uuid.uuid4(),
                    "recovery_case_id": case_id,
                    "event_type": event[
                        "event_type"
                    ],
                    "actor": event["actor"],
                    "message": event["message"],
                    "metadata": event["metadata"],
                    "created_at": event_time,
                }
            )

    with connection.cursor() as cursor:
        for event in audit_events:
            cursor.execute(
                """
                INSERT INTO audit_logs
                (
                    id,
                    recovery_case_id,
                    event_type,
                    actor,
                    message,
                    metadata,
                    created_at
                )
                VALUES
                (
                    %(id)s,
                    %(recovery_case_id)s,
                    %(event_type)s,
                    %(actor)s,
                    %(message)s,
                    %(metadata)s,
                    %(created_at)s
                )
                """,
                {
                    **event,
                    "metadata": psycopg.types.json.Jsonb(
                        event["metadata"]
                    ),
                },
            )

    connection.commit()

    print(
        f"Generated {len(audit_events)} audit log events."
    )

def generate_day4_degradation_events(connection):
    """
    Generate additional payment events specifically for
    Day 4 payment degradation detection.

    Existing Day 2/3 data is NOT modified.
    """

    from datetime import datetime, timedelta, timezone

    # Two periods:
    # Previous period = 2 days ago
    # Current period  = yesterday

    now = datetime.now(timezone.utc)

    previous_start = now - timedelta(days=2)
    current_start = now - timedelta(days=1)

    # Events per payment method per period
    events_per_method = 100

    # Previous-period success rates
    previous_success_rates = {
        "upi": 0.95,
        "card": 0.90,
        "wallet": 0.92,
        "bank_transfer": 0.88,
    }

    # Current-period success rates.
    # UPI deliberately degrades.
    current_success_rates = {
        "upi": 0.75,
        "card": 0.89,
        "wallet": 0.91,
        "bank_transfer": 0.87,
    }

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT id, amount, currency
            FROM subscriptions
            WHERE status != 'cancelled'
            """
        )

        subscriptions = cursor.fetchall()

    if not subscriptions:
        raise RuntimeError(
            "No usable subscriptions found."
        )

    payments = []

    for payment_method in previous_success_rates:

        # -------------------------
        # Previous period
        # -------------------------

        for _ in range(events_per_method):

            subscription_id, amount, currency = fake.random_element(
                subscriptions
            )

            success_rate = previous_success_rates[
                payment_method
            ]

            is_success = (
                fake.random_int(1, 100)
                <= success_rate * 100
            )

            if is_success:
                status = "success"
                failure_reason = None
                decline_code = None
            else:
                status = "failed"

                failure = fake.random_element(
                    FAILURE_SCENARIOS
                )

                failure_reason = failure["reason"]
                decline_code = failure["decline_code"]

            attempted_at = previous_start + timedelta(
                minutes=fake.random_int(
                    0,
                    1439,
                )
            )

            payments.append(
                {
                    "id": uuid.uuid4(),
                    "subscription_id": subscription_id,
                    "amount": amount,
                    "currency": currency,
                    "payment_method": payment_method,
                    "status": status,
                    "failure_reason": failure_reason,
                    "decline_code": decline_code,
                    "attempt_number": fake.random_int(
                        1,
                        3,
                    ),
                    "attempted_at": attempted_at,
                }
            )

        # -------------------------
        # Current period
        # -------------------------

        for _ in range(events_per_method):

            subscription_id, amount, currency = fake.random_element(
                subscriptions
            )

            success_rate = current_success_rates[
                payment_method
            ]

            is_success = (
                fake.random_int(1, 100)
                <= success_rate * 100
            )

            if is_success:
                status = "success"
                failure_reason = None
                decline_code = None
            else:
                status = "failed"

                failure = fake.random_element(
                    FAILURE_SCENARIOS
                )

                failure_reason = failure["reason"]
                decline_code = failure["decline_code"]

            attempted_at = current_start + timedelta(
                minutes=fake.random_int(
                    0,
                    1439,
                )
            )

            payments.append(
                {
                    "id": uuid.uuid4(),
                    "subscription_id": subscription_id,
                    "amount": amount,
                    "currency": currency,
                    "payment_method": payment_method,
                    "status": status,
                    "failure_reason": failure_reason,
                    "decline_code": decline_code,
                    "attempt_number": fake.random_int(
                        1,
                        3,
                    ),
                    "attempted_at": attempted_at,
                }
            )

    with connection.cursor() as cursor:

        for payment in payments:

            cursor.execute(
                """
                INSERT INTO payment_attempts
                (
                    id,
                    subscription_id,
                    amount,
                    currency,
                    payment_method,
                    status,
                    failure_reason,
                    decline_code,
                    attempt_number,
                    attempted_at
                )
                VALUES
                (
                    %(id)s,
                    %(subscription_id)s,
                    %(amount)s,
                    %(currency)s,
                    %(payment_method)s,
                    %(status)s,
                    %(failure_reason)s,
                    %(decline_code)s,
                    %(attempt_number)s,
                    %(attempted_at)s
                )
                """,
                payment,
            )

    connection.commit()

    print(
        f"Generated {len(payments)} Day 4 degradation events."
    )



def main():
    with psycopg.connect(**DB_CONFIG) as connection:
        print("Connected to RecoverAI database.")

        generate_audit_logs(connection)

        print("Audit log generation completed.")

if __name__ == "__main__":
    main()