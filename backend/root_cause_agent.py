import os
import time


from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.database import get_connection

from pydantic import BaseModel, Field


class RootCauseAnalysis(BaseModel):
    root_cause: str
    failure_type: str
    recovery_probability: float = Field(
        ge=0.0,
        le=1.0,
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

ALLOWED_ROOT_CAUSES = {
    "expired_card",
    "insufficient_funds",
    "temporary_bank_failure",
    "payment_gateway_failure",
    "hard_decline",
    "soft_decline",
    "authentication_failure",
}


ALLOWED_FAILURE_TYPES = {
    "SOFT_DECLINE",
    "HARD_DECLINE",
    "TECHNICAL_FAILURE",
    "AUTHENTICATION_FAILURE",
    "CUSTOMER_PAYMENT_METHOD",
    "UNKNOWN",
}

def validate_analysis(result: RootCauseAnalysis) -> RootCauseAnalysis:
    if result.root_cause not in ALLOWED_ROOT_CAUSES:
        raise ValueError(
            f"Invalid root cause: {result.root_cause}"
        )

    if result.failure_type not in ALLOWED_FAILURE_TYPES:
        raise ValueError(
            f"Invalid failure type: {result.failure_type}"
        )

    return result

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.1-flash-lite"
MAX_RETRIES = 3
DEFAULT_RETRY_SECONDS = 40

def analyze_root_cause(payment_data: dict) -> RootCauseAnalysis:

    prompt = f"""
    You are the Root Cause Analysis component of RecoverAI,
    an AI subscription revenue recovery system.

    Your job is ONLY to analyze the payment failure evidence
    and recommend a root cause.

    You MUST NOT execute, trigger, or request any payment action.

    Analyze the following evidence:

    {payment_data}

    Allowed root causes:
    {sorted(ALLOWED_ROOT_CAUSES)}

    Allowed failure types:
    {sorted(ALLOWED_FAILURE_TYPES)}

    Rules:

    1. Use the provided payment failure reason as important evidence.
    2. Consider payment method and previous attempts.
    3. Do not invent facts that are not present.
    4. recovery_probability must be between 0 and 1.
    5. confidence must be between 0 and 1.
    6. Return only the structured analysis.
    """

    for attempt in range(MAX_RETRIES):

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RootCauseAnalysis,
                    temperature=0.1,
                ),
            )

            break

        except Exception as error:

            error_message = str(error)

            # Daily quota cannot be fixed by waiting 40 seconds.
            if (
                "GenerateRequestsPerDay" in error_message
                or "insufficient_quota" in error_message
            ):
                raise RuntimeError(
                    "GEMINI_QUOTA_EXHAUSTED"
                ) from error

            # Temporary rate limit.
            if "429" not in error_message and "503" not in error_message:
                raise

            if attempt == MAX_RETRIES - 1:
                raise

            if "503" in error_message:
                retry_seconds = 10

                print(
                    f"Gemini temporarily unavailable (503). "
                    f"Retrying in {retry_seconds} seconds..."
                )

            else:
                retry_seconds = DEFAULT_RETRY_SECONDS

                print(
                    f"Gemini rate limit reached (429). "
                    f"Retrying in {retry_seconds} seconds..."
                )

            time.sleep(retry_seconds)

    result = RootCauseAnalysis.model_validate_json(
    response.text
    )

    return validate_analysis(result)

def get_payment_evidence_for_subscription(
    connection,
    subscription_id,
):
    query = """
        SELECT
            p.id,
            p.status,
            p.amount,
            p.currency,
            p.payment_method,
            p.failure_reason,
            p.decline_code,
            p.attempt_number,
            p.attempted_at,

            c.id AS customer_id,
            c.name AS customer_name,
            c.email AS customer_email,

            s.id AS subscription_id,
            s.plan_name,
            s.amount AS subscription_amount,
            s.billing_cycle,
            s.status AS subscription_status,
            s.next_billing_date

        FROM payment_attempts p

        JOIN subscriptions s
            ON p.subscription_id = s.id

        JOIN customers c
            ON s.customer_id = c.id

        WHERE p.status = 'failed'
          AND s.status = 'active'
          AND s.id = %s

        ORDER BY p.attempted_at DESC

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
            f"No failed payment found for subscription "
            f"{subscription_id}"
        )

    return row

def build_payment_evidence(connection, row):
    (
        payment_id,
        payment_status,
        payment_amount,
        currency,
        payment_method,
        failure_reason,
        decline_code,
        attempt_number,
        attempted_at,
        customer_id,
        customer_name,
        customer_email,
        subscription_id,
        plan_name,
        subscription_amount,
        billing_cycle,
        subscription_status,
        next_billing_date,
    ) = row

    subscription_id = str(subscription_id)

    failure_history = get_failure_history(
        connection,
        subscription_id,
    )

    return {
        "payment_event": {
            "payment_id": str(payment_id),
            "status": payment_status,
            "amount": float(payment_amount),
            "currency": currency,
            "payment_method": payment_method,
            "failure_reason": failure_reason,
            "decline_code": decline_code,
            "attempt_number": attempt_number,
            "attempted_at": attempted_at.isoformat(),
        },
        "customer": {
            "customer_id": str(customer_id),
            "name": customer_name,
            "email": customer_email,
        },
        "subscription": {
            "subscription_id": str(subscription_id),
            "plan_name": plan_name,
            "amount": float(subscription_amount),
            "currency": currency,
            "billing_cycle": billing_cycle,
            "status": subscription_status,
            "next_billing_date": str(
                next_billing_date
            ),
        },
        "failure_history": failure_history,
    }

def get_failure_history(connection, subscription_id):
    query = """
        SELECT
            status,
            failure_reason,
            payment_method,
            attempt_number,
            attempted_at
        FROM payment_attempts
        WHERE subscription_id = %s
        ORDER BY attempted_at ASC;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (subscription_id,),
        )

        rows = cursor.fetchall()

    return [
        {
            "status": row[0],
            "failure_reason": row[1],
            "payment_method": row[2],
            "attempt_number": row[3],
            "attempted_at": row[4].isoformat(),
        }
        for row in rows
    ]


if __name__ == "__main__":

    connection = get_connection()

    try:
        row = get_payment_evidence_for_subscription(
            connection,
            subscription_id="sub_1234567890"
        )

        evidence = build_payment_evidence(
            connection,
            row,
        )

        print("\nReal Payment Evidence")
        print("=" * 60)
        print(evidence)

        print("\nGemini Root Cause Analysis")
        print("=" * 60)

        result = analyze_root_cause(
            evidence
        )

        print(
            result.model_dump_json(
                indent=2
            )
        )

    finally:
        connection.close()



