import uuid
from datetime import datetime, timezone, timedelta

import psycopg
from faker import Faker

from synthetic_data_generator import DB_CONFIG

fake = Faker()

EVENTS_PER_METHOD = 100

PAYMENT_METHODS = [
    "upi",
    "card",
    "wallet",
    "bank_transfer",
]

# Baseline success rates
BASELINE_RATES = {
    "upi": 0.95,
    "card": 0.90,
    "wallet": 0.92,
    "bank_transfer": 0.88,
}

# Current-period success rates
# UPI intentionally degrades significantly.
CURRENT_RATES = {
    "upi": 0.75,
    "card": 0.89,
    "wallet": 0.91,
    "bank_transfer": 0.87,
}

FAILURE_SCENARIOS = [
    ("expired_card", "card_expired"),
    ("insufficient_funds", "insufficient_funds"),
    ("temporary_bank_failure", "bank_temporary_failure"),
    ("payment_gateway_failure", "gateway_error"),
    ("hard_decline", "do_not_retry"),
    ("soft_decline", "temporary_decline"),
    ("authentication_failure", "authentication_required"),
]


def generate_controlled_events(connection):
    """Generate isolated Day 4 degradation events."""

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
        raise RuntimeError("No usable subscriptions found.")

    # Fixed dates so the analytics query is deterministic.
    baseline_date = datetime(2026, 8, 22, tzinfo=timezone.utc)
    current_date = datetime(2026, 8, 23, tzinfo=timezone.utc)

    payments = []

    for payment_method in PAYMENT_METHODS:

        # --------------------------------
        # Baseline period
        # --------------------------------

        for _ in range(EVENTS_PER_METHOD):

            subscription_id, amount, currency = fake.random_element(
                subscriptions
            )

            success = (
                fake.random_int(1, 100)
                <= BASELINE_RATES[payment_method] * 100
            )

            if success:
                status = "success"
                failure_reason = None
                decline_code = None
            else:
                failure_reason, decline_code = fake.random_element(
                    FAILURE_SCENARIOS
                )
                status = "failed"

            attempted_at = baseline_date + timedelta(
                minutes=fake.random_int(0, 1439)
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
                    "attempt_number": fake.random_int(1, 3),
                    "attempted_at": attempted_at,
                }
            )

        # --------------------------------
        # Current period
        # --------------------------------

        for _ in range(EVENTS_PER_METHOD):

            subscription_id, amount, currency = fake.random_element(
                subscriptions
            )

            success = (
                fake.random_int(1, 100)
                <= CURRENT_RATES[payment_method] * 100
            )

            if success:
                status = "success"
                failure_reason = None
                decline_code = None
            else:
                failure_reason, decline_code = fake.random_element(
                    FAILURE_SCENARIOS
                )
                status = "failed"

            attempted_at = current_date + timedelta(
                minutes=fake.random_int(0, 1439)
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
                    "attempt_number": fake.random_int(1, 3),
                    "attempted_at": attempted_at,
                }
            )

    with connection.cursor() as cursor:

        for payment in payments:

            cursor.execute(
                """
                INSERT INTO payment_attempts (
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
                VALUES (
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
        f"Generated {len(payments)} controlled Day 4 events."
    )


if __name__ == "__main__":
    with psycopg.connect(**DB_CONFIG) as connection:
        generate_controlled_events(connection)