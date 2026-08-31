
def get_case_history_for_subscription(
    connection,
    subscription_id,
):
    query = """
        SELECT
            al.event_type,
            al.actor,
            al.message,
            al.metadata,
            al.created_at
        FROM audit_logs al
        JOIN recovery_cases rc
            ON al.recovery_case_id = rc.id
        WHERE rc.subscription_id = %s
        ORDER BY al.created_at ASC;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (subscription_id,),
        )

        rows = cursor.fetchall()

    history = []

    for row in rows:
        history.append(
            {
                "event_type": row[0],
                "actor": row[1],
                "message": row[2],
                "metadata": row[3],
                "created_at": row[4].isoformat(),
            }
        )

    return history