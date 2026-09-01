from decimal import Decimal


def calculate_risk_score(
    latest_attempt_number: int,
    failed_attempt_count: int,
    subscription_amount: Decimal,
) -> tuple[int, str, list[str]]:

    score = 40
    signals = ["failed_payment"]

    # Repeated failures
    if failed_attempt_count >= 2:
        score += 20
        signals.append("repeated_failures")

    # Retry exhaustion
    if latest_attempt_number >= 3:
        score += 20
        signals.append("retry_exhausted")

    # High-value subscription
    if subscription_amount >= Decimal("5000"):
        score += 20
        signals.append("high_value_subscription")

    score = min(score, 100)

    if score >= 90:
        severity = "CRITICAL"
    elif score >= 70:
        severity = "HIGH"
    elif score >= 40:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    return score, severity, signals

def detect_revenue_risk(connection):
    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                s.id AS subscription_id,
                s.plan_name,
                s.amount AS subscription_amount,
                COUNT(*) AS failed_attempt_count,
                MAX(p.attempt_number) AS latest_attempt_number,
                MAX(p.attempted_at) AS latest_attempt_at
            FROM subscriptions s
            JOIN payment_attempts p
                ON s.id = p.subscription_id
            WHERE
                s.status = 'active'
                AND p.status = 'failed'

                -- Do not detect a subscription that already
                -- has a successful payment after the failure.
                AND NOT EXISTS (
                    SELECT 1
                    FROM payment_attempts successful_payment
                    WHERE successful_payment.subscription_id = s.id
                      AND successful_payment.status = 'success'
                      AND successful_payment.attempted_at > p.attempted_at
                )

            GROUP BY
                s.id,
                s.plan_name,
                s.amount
            ORDER BY
                latest_attempt_at DESC;
            """
        )

        rows = cursor.fetchall()

    cases = []

    for row in rows:
        (
            subscription_id,
            plan_name,
            subscription_amount,
            failed_attempt_count,
            latest_attempt_number,
            latest_attempt_at,
        ) = row

        risk_score, severity, signals = calculate_risk_score(
            latest_attempt_number=latest_attempt_number,
            failed_attempt_count=failed_attempt_count,
            subscription_amount=subscription_amount,
        )

        cases.append(
            {
                "subscription_id": str(subscription_id),
                "plan_name": plan_name,
                "revenue_at_risk": float(subscription_amount),
                "risk_score": risk_score,
                "severity": severity,
                "failed_attempt_count": failed_attempt_count,
                "latest_attempt_number": latest_attempt_number,
                "latest_attempt_at": latest_attempt_at.isoformat(),
                "signals": signals,
            }
        )

    return cases