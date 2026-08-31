import uuid

from psycopg.types.json import Jsonb


def log_audit_event(
    connection,
    recovery_case_id,
    event_type,
    actor,
    message,
    metadata=None,
):
    query = """
        INSERT INTO audit_logs (
            id,
            recovery_case_id,
            event_type,
            actor,
            message,
            metadata,
            created_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            NOW()
        );
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                uuid.uuid4(),
                recovery_case_id,
                event_type,
                actor,
                message,
                Jsonb(metadata or {}),
            ),
        )

    connection.commit()

if __name__ == "__main__":

    from app.database import get_connection

    connection = get_connection()

    try:
        recovery_case_id = (
            "ae453878-527b-498c-9b2e-bf3a801526d9"
        )

        log_audit_event(
            connection=connection,
            recovery_case_id=recovery_case_id,
            event_type="day9_test",
            actor="system",
            message="Day 9 audit logger test.",
            metadata={
                "test": True,
                "source": "guardrails",
            },
        )

        print("Audit event inserted successfully.")

    finally:
        connection.close()