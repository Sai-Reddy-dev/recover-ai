import psycopg

from synthetic_data_generator import DB_CONFIG


DEGRADATION_THRESHOLD = 10.0

BASELINE_DATE = "2026-08-22"
CURRENT_DATE = "2026-08-23"


def get_degradation_stats(connection):
    query = """
        WITH period_stats AS (
            SELECT
                payment_method,

                COUNT(*) FILTER (
                    WHERE DATE(attempted_at) = %s
                ) AS previous_attempts,

                COUNT(*) FILTER (
                    WHERE DATE(attempted_at) = %s
                ) AS current_attempts,

                COUNT(*) FILTER (
                    WHERE DATE(attempted_at) = %s
                    AND status = 'success'
                ) AS previous_successes,

                COUNT(*) FILTER (
                    WHERE DATE(attempted_at) = %s
                    AND status = 'success'
                ) AS current_successes

            FROM payment_attempts

            WHERE DATE(attempted_at) IN (%s, %s)

            GROUP BY payment_method
        )

        SELECT
            payment_method,

            previous_attempts,
            current_attempts,

            ROUND(
                100.0 * previous_successes
                / NULLIF(previous_attempts, 0),
                2
            ) AS previous_success_rate,

            ROUND(
                100.0 * current_successes
                / NULLIF(current_attempts, 0),
                2
            ) AS current_success_rate

        FROM period_stats

        ORDER BY payment_method;
    """

    params = (
        BASELINE_DATE,
        CURRENT_DATE,
        BASELINE_DATE,
        CURRENT_DATE,
        BASELINE_DATE,
        CURRENT_DATE,
    )

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def get_affected_subscriptions(connection, payment_method):
    query = """
        WITH latest_failures AS (
            SELECT DISTINCT ON (p.subscription_id)
                p.subscription_id,
                s.amount AS revenue_at_risk,
                p.failure_reason,
                p.attempted_at

            FROM payment_attempts p

            JOIN subscriptions s
                ON p.subscription_id = s.id

            WHERE p.payment_method = %s
              AND p.status = 'failed'
              AND s.status = 'active'
              AND DATE(p.attempted_at) = %s

            ORDER BY
                p.subscription_id,
                p.attempted_at DESC
        )

        SELECT
            COUNT(*) AS affected_subscriptions,
            COALESCE(
                SUM(revenue_at_risk),
                0
            ) AS revenue_at_risk

        FROM latest_failures;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                payment_method,
                CURRENT_DATE,
            ),
        )

        return cursor.fetchone()


def detect_payment_degradation(connection):

    rows = get_degradation_stats(connection)

    results = []

    for row in rows:

        (
            payment_method,
            previous_attempts,
            current_attempts,
            previous_success_rate,
            current_success_rate,
        ) = row

        previous_rate = float(
            previous_success_rate or 0
        )

        current_rate = float(
            current_success_rate or 0
        )

        degradation = round(
            previous_rate - current_rate,
            2,
        )

        if degradation >= DEGRADATION_THRESHOLD:

            status = "DEGRADED"

            affected_count, revenue_at_risk = (
                get_affected_subscriptions(
                    connection,
                    payment_method,
                )
            )

        else:

            status = "NORMAL"

            affected_count = 0
            revenue_at_risk = 0

        results.append(
            {
                "payment_method": payment_method,
                "previous_success_rate": previous_rate,
                "current_success_rate": current_rate,
                "degradation_percentage_points": degradation,
                "status": status,
                "affected_subscriptions": affected_count,
                "revenue_at_risk": float(
                    revenue_at_risk or 0
                ),
            }
        )

    return results


def main():

    with psycopg.connect(**DB_CONFIG) as connection:

        results = detect_payment_degradation(
            connection
        )

        print("\nPayment Degradation Detection")
        print("=" * 65)

        for result in results:

            print(
                f"\nPayment Method: "
                f"{result['payment_method']}"
            )

            print(
                f"Previous Success Rate: "
                f"{result['previous_success_rate']}%"
            )

            print(
                f"Current Success Rate: "
                f"{result['current_success_rate']}%"
            )

            print(
                f"Degradation: "
                f"{result['degradation_percentage_points']} "
                f"percentage points"
            )

            print(
                f"Status: "
                f"{result['status']}"
            )

            print(
                f"Affected Subscriptions: "
                f"{result['affected_subscriptions']}"
            )

            print(
                f"Revenue at Risk: "
                f"₹{result['revenue_at_risk']:,.2f}"
            )


if __name__ == "__main__":
    main()