from payment_degradation_detector import detect_payment_degradation

def get_recent_audit_events(
    connection,
    limit=10,
):
    query = """
        SELECT
            event_type,
            actor,
            message,
            metadata,
            created_at
        FROM audit_logs
        ORDER BY created_at DESC
        LIMIT %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (limit,),
        )

        rows = cursor.fetchall()

    events = []

    for row in rows:
        events.append(
            {
                "event_type": row[0],
                "actor": row[1],
                "message": row[2],
                "metadata": row[3],
                "created_at": row[4].isoformat(),
            }
        )

    return events


def get_dashboard_metrics(connection):
    """
    Calculate real RecoverAI dashboard metrics
    from PostgreSQL recovery data.
    """

    # -----------------------------------------
    # 1. Revenue at risk + active cases
    # -----------------------------------------

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                COUNT(*) AS active_cases,
                COALESCE(
                    SUM(revenue_at_risk),
                    0
                ) AS revenue_at_risk
            FROM recovery_cases
            WHERE status = 'active';
            """
        )

        row = cursor.fetchone()

        active_cases = row[0]
        revenue_at_risk = float(row[1])

    # -----------------------------------------
    # 2. Recovered cases + recovered revenue
    # -----------------------------------------

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                COUNT(*) AS recovered_cases,
                COUNT(DISTINCT subscription_id) AS recovered_subscriptions,
                COALESCE(
                    SUM(revenue_at_risk),
                    0
                ) AS revenue_recovered
            FROM recovery_cases
            WHERE status = 'recovered';
            """
        )

        row = cursor.fetchone()

        recovered_cases = row[0]
        recovered_subscriptions = row[1]
        revenue_recovered = float(row[2])

    # -----------------------------------------
    # 3. Failed cases
    # -----------------------------------------

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM recovery_cases
            WHERE status = 'failed';
            """
        )

        failed_cases = cursor.fetchone()[0]

    # -----------------------------------------
    # 4. Stopped / escalated cases
    # -----------------------------------------

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM recovery_cases
            WHERE status = 'escalated';
            """
        )

        stopped_workflows = cursor.fetchone()[0]

    # -----------------------------------------
    # 5. Recovery by action
    # -----------------------------------------

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                action_type,
                COUNT(*) AS recovered_count,
                COALESCE(
                    SUM(rc.revenue_at_risk),
                    0
                ) AS revenue_recovered
            FROM recovery_actions ra
            JOIN recovery_cases rc
                ON ra.recovery_case_id = rc.id
            WHERE
                ra.status = 'success'
                AND ra.result = 'payment_recovered'
            GROUP BY action_type
            ORDER BY revenue_recovered DESC;
            """
        )

        rows = cursor.fetchall()

    recovery_by_action = []

    for row in rows:

        recovery_by_action.append(
            {
                "action": row[0],
                "recovered_cases": row[1],
                "revenue_recovered": float(row[2]),
            }
        )

    # -----------------------------------------
    # 6. Recovery rate
    # -----------------------------------------

    total_revenue = (
        revenue_at_risk +
        revenue_recovered
    )

    if total_revenue > 0:

        recovery_rate = (
            revenue_recovered /
            total_revenue
        ) * 100

    else:

        recovery_rate = 0

    # -----------------------------------------
    # 7. Payment degradation
    # -----------------------------------------

    degradation_results = detect_payment_degradation(
        connection
    )

    degraded_methods = [
        result
        for result in degradation_results
        if result["status"] == "DEGRADED"
    ]

    affected_subscriptions = sum(
        result["affected_subscriptions"]
        for result in degraded_methods
    )

    degradation_revenue_at_risk = sum(
        result["revenue_at_risk"]
        for result in degraded_methods
    )

    recent_audit_events = get_recent_audit_events(
        connection
    )

    return {
        "summary": {
            "revenue_at_risk": round(
                revenue_at_risk,
                2,
            ),
            "revenue_recovered": round(
                revenue_recovered,
                2,
            ),
            "recovery_rate": round(
                recovery_rate,
                2,
            ),
            "recovered_subscriptions": (
                recovered_subscriptions
            ),
            "recovered_cases": recovered_cases,
        },

        "cases": {
            "active": active_cases,
            "failed": failed_cases,
            "stopped": stopped_workflows,
        },

        "recovery_by_action": (
            recovery_by_action
        ),

        "payment_degradation": {
            "degraded_methods": len(
                degraded_methods
            ),
            "affected_subscriptions": (
                affected_subscriptions
            ),
            "revenue_at_risk": round(
                degradation_revenue_at_risk,
                2,
            ),
        },

        "recent_audit_events": recent_audit_events,
    }