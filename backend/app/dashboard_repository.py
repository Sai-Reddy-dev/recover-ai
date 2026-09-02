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


def get_ai_decision_control(connection, limit=10):
    query = """
        SELECT
            rc.id AS recovery_case_id,
            rc.revenue_at_risk,

            ad.root_cause,
            ad.confidence,
            ad.risk_level,
            ad.recommended_action,
            ad.reason,

            ge.guardrail_action,
            ge.guardrail_approved,
            ge.guardrail_reason,

            ra.action_type AS executed_action,
            ra.status AS execution_status,
            ra.result AS execution_result,
            ra.attempt_number,
            ra.executed_at

        FROM agent_decisions ad

        JOIN recovery_cases rc
            ON rc.id = ad.recovery_case_id

        LEFT JOIN LATERAL (
            SELECT
                metadata ->> 'action' AS guardrail_action,
                (metadata ->> 'approved')::boolean AS guardrail_approved,
                metadata ->> 'reason' AS guardrail_reason,
                created_at
            FROM audit_logs
            WHERE
                recovery_case_id = ad.recovery_case_id
                AND event_type = 'guardrail_evaluated'
            ORDER BY created_at DESC
            LIMIT 1
        ) ge ON TRUE

        LEFT JOIN recovery_actions ra
            ON ra.agent_decision_id = ad.id

        ORDER BY
            COALESCE(
                ra.executed_at,
                ge.created_at,
                ad.created_at
            ) DESC

        LIMIT %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()

    return [
        {
            "recovery_case_id": str(row[0]),
            "revenue_at_risk": float(row[1] or 0),

            "root_cause": row[2],
            "confidence": float(row[3]) if row[3] is not None else None,
            "risk_level": row[4],
            "recommended_action": row[5],
            "reason": row[6],

            "guardrail_action": row[7],
            "guardrail_approved": row[8],
            "guardrail_reason": row[9],

            "executed_action": row[10],
            "execution_status": row[11],
            "execution_result": row[12],
            "attempt_number": row[13],
            "executed_at": (
                row[14].isoformat()
                if row[14] is not None
                else None
            ),
        }
        for row in rows
    ]



def get_recovery_cases(connection, limit=20):
    query = """
        SELECT
            rc.id AS recovery_case_id,
            c.name AS customer_name,
            c.email AS customer_email,

            rc.revenue_at_risk,
            rc.status,
            rc.priority,
            rc.retry_count,
            rc.opened_at,
            rc.closed_at,

            p.failure_reason,
            p.decline_code,
            p.payment_method,

            ad.root_cause,
            ad.confidence,
            ad.recommended_action

        FROM recovery_cases rc

        JOIN customers c
            ON c.id = rc.customer_id

        LEFT JOIN payment_attempts p
            ON p.id = rc.trigger_payment_id

        LEFT JOIN LATERAL (
            SELECT
                root_cause,
                confidence,
                recommended_action
            FROM agent_decisions
            WHERE recovery_case_id = rc.id
            ORDER BY created_at DESC
            LIMIT 1
        ) ad ON TRUE

        ORDER BY
            rc.opened_at DESC

        LIMIT %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()

    return [
        {
            "recovery_case_id": str(row[0]),
            "customer_name": row[1],
            "customer_email": row[2],

            "revenue_at_risk": float(row[3] or 0),
            "status": row[4],
            "priority": row[5],
            "retry_count": row[6],

            "opened_at": (
                row[7].isoformat()
                if row[7] is not None
                else None
            ),

            "closed_at": (
                row[8].isoformat()
                if row[8] is not None
                else None
            ),

            "failure_reason": row[9],
            "decline_code": row[10],
            "payment_method": row[11],

            "root_cause": row[12],
            "confidence": (
                float(row[13])
                if row[13] is not None
                else None
            ),
            "recommended_action": row[14],
        }
        for row in rows
    ]


def get_ai_recommendation_distribution(connection):
    query = """
        SELECT
            recommended_action,
            COUNT(*) AS decision_count
        FROM agent_decisions
        WHERE recommended_action IS NOT NULL
        GROUP BY recommended_action
        ORDER BY decision_count DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    return [
        {
            "action": row[0],
            "decision_count": row[1],
        }
        for row in rows
    ]


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
    ai_decision_control = get_ai_decision_control(
        connection
    )

    recovery_cases = get_recovery_cases(
        connection
    )

    ai_recommendation_distribution = (
        get_ai_recommendation_distribution(
            connection
        )
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

        "ai_decision_control": ai_decision_control,

        "recovery_cases": recovery_cases,

        "ai_recommendation_distribution": (
            ai_recommendation_distribution
        ),
    }