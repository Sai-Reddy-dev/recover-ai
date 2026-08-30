import time

from app.database import get_connection
from app.detector import detect_revenue_risk

from root_cause_agent import (
    analyze_root_cause,
    get_payment_evidence_for_subscription,
    build_payment_evidence,
)

from recovery_decision_agent import decide_recovery_action


# Day 7 batch configuration
DEFAULT_CASE_LIMIT = 100

# Gemini free-tier limit currently observed in testing:
# 5 requests per minute.
REQUESTS_PER_WINDOW = 5
WINDOW_SECONDS = 60


def process_risk_case(connection, risk_case):
    """
    Process one real revenue-risk case through:

    Risk Detection
        ↓
    Payment Evidence
        ↓
    Root Cause AI
        ↓
    Recovery Policy
    """

    row = get_payment_evidence_for_subscription(
        connection,
        risk_case["subscription_id"],
    )

    evidence = build_payment_evidence(
        connection,
        row,
    )

    # Day 5 — Gemini root cause analysis
    analysis = analyze_root_cause(evidence)

    # Day 6 — deterministic recovery policy
    recovery_action = decide_recovery_action(
        root_cause=analysis.root_cause,
        failure_type=analysis.failure_type,
        recovery_probability=analysis.recovery_probability,
        confidence=analysis.confidence,
        failed_attempt_count=risk_case["failed_attempt_count"],
        latest_attempt_number=risk_case["latest_attempt_number"],
    )

    return {
        "risk_case": risk_case,
        "ai_analysis": analysis.model_dump(),
        "recovery_decision": recovery_action.model_dump(),
    }


def run_recovery_pipeline(
    limit=DEFAULT_CASE_LIMIT,
):
    """
    Run the complete RecoverAI intelligence pipeline
    against multiple real risk cases.

    The pipeline does not execute payment actions.
    It only produces recovery recommendations.
    """

    connection = get_connection()

    try:
        # Day 3 — detect real revenue-risk cases
        cases = detect_revenue_risk(connection)

        if not cases:
            raise RuntimeError(
                "No revenue risk cases found."
            )

        cases = cases[:limit]

        results = []
        errors = []

        window_start = time.time()
        requests_in_window = 0

        print(
            f"\nStarting recovery pipeline "
            f"for {len(cases)} cases..."
        )

        for index, risk_case in enumerate(
            cases,
            start=1,
        ):

            # -----------------------------------------
            # Gemini rate-limit protection
            # -----------------------------------------

            elapsed = time.time() - window_start

            if (
                requests_in_window >= REQUESTS_PER_WINDOW
                and elapsed < WINDOW_SECONDS
            ):
                wait_seconds = (
                    WINDOW_SECONDS - elapsed
                )

                print(
                    f"\nRate-limit window reached. "
                    f"Waiting {wait_seconds:.1f} seconds..."
                )

                time.sleep(wait_seconds)

                window_start = time.time()
                requests_in_window = 0

            print(
                f"\nProcessing case "
                f"{index}/{len(cases)}"
            )

            try:

                result = process_risk_case(
                    connection,
                    risk_case,
                )

                results.append(result)

                requests_in_window += 1

                action = result[
                    "recovery_decision"
                ]["action"]

                root_cause = result[
                    "ai_analysis"
                ]["root_cause"]

                print(
                    f"Root cause: {root_cause}"
                )

                print(
                    f"Action: {action}"
                )

            except Exception as error:

                error_message = str(error)

                if "GEMINI_QUOTA_EXHAUSTED" in error_message:
                    errors.append(
                        {
                            "subscription_id": str(
                                risk_case["subscription_id"]
                            ),
                            "status": "AI_ANALYSIS_UNAVAILABLE",
                            "reason": "GEMINI_QUOTA_EXHAUSTED",
                        }
                    )

                    print(
                        "Gemini daily quota exhausted."
                    )

                    print(
                        "Stopping AI batch safely."
                    )

                    break

                errors.append(
                    {
                        "subscription_id": str(
                            risk_case["subscription_id"]
                        ),
                        "status": "PROCESSING_ERROR",
                        "reason": error_message,
                    }
                )

                print(
                    f"ERROR processing case "
                    f"{index}: {error_message}"
                )
        return results, errors

    finally:
        connection.close()


def print_pipeline_summary(
    results,
    errors,
):
    print("\n")
    print("=" * 60)
    print("RECOVERY PIPELINE SUMMARY")
    print("=" * 60)

    print(
        f"Cases successfully processed: "
        f"{len(results)}"
    )

    print(
        f"Cases with errors: "
        f"{len(errors)}"
    )

    total_revenue_at_risk = sum(
        result["risk_case"]["revenue_at_risk"]
        for result in results
    )

    print(
        f"Revenue at risk processed: "
        f"₹{total_revenue_at_risk:.2f}"
    )

    action_counts = {}

    for result in results:

        action = result[
            "recovery_decision"
        ]["action"]

        action_counts[action] = (
            action_counts.get(action, 0) + 1
        )

    print("\nRecovery actions:")

    for action, count in sorted(
        action_counts.items()
    ):

        print(
            f"{action}: {count}"
        )

    if errors:

        print("\nErrors:")

        for error in errors[:10]:

            print(
                f"- {error['subscription_id']}: "
                f"{error.get('reason', 'UNKNOWN_ERROR')}"
            )

        if len(errors) > 10:

            print(
                f"... and "
                f"{len(errors) - 10} more"
            )


if __name__ == "__main__":

    results, errors = run_recovery_pipeline(
        limit=10
    )

    print_pipeline_summary(
        results,
        errors,
    )