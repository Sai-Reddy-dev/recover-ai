import time

from app.database import get_connection
from app.detector import detect_revenue_risk
from recovery_decision_agent import decide_recovery_action
from recovery_workflow import execute_recovery_action
from audit_logger import log_audit_event

from guardrails import (
    validate_recovery_action,
    get_recovery_case_id,
)

from root_cause_agent import (
    analyze_root_cause,
    get_payment_evidence_for_subscription,
    build_payment_evidence,
)




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
        ↓
    Guardrails
        ↓
    Recovery Workflow
        ↓
    Audit Trail
    """

    # --------------------------------------------------
    # 1. Get the real recovery case ID
    # --------------------------------------------------

    recovery_case_id = get_recovery_case_id(
        connection,
        risk_case["subscription_id"],
    )

    # --------------------------------------------------
    # 2. Audit: risk detected
    # --------------------------------------------------

    log_audit_event(
        connection=connection,
        recovery_case_id=recovery_case_id,
        event_type="risk_detected",
        actor="system",
        message=(
            f"Revenue risk detected: "
            f"₹{risk_case['revenue_at_risk']:.2f}."
        ),
        metadata={
            "risk_score": risk_case["risk_score"],
            "severity": risk_case["severity"],
            "failed_attempt_count": risk_case[
                "failed_attempt_count"
            ],
        },
    )

    # --------------------------------------------------
    # 3. Get real payment evidence
    # --------------------------------------------------

    row = get_payment_evidence_for_subscription(
        connection,
        risk_case["subscription_id"],
    )

    evidence = build_payment_evidence(
        connection,
        row,
    )

    # --------------------------------------------------
    # 4. Day 5 — Gemini root cause analysis
    # --------------------------------------------------

    analysis = analyze_root_cause(evidence)

    log_audit_event(
        connection=connection,
        recovery_case_id=recovery_case_id,
        event_type="root_cause_identified",
        actor="ai_agent",
        message=(
            f"Root cause identified: "
            f"{analysis.root_cause}."
        ),
        metadata={
            "root_cause": analysis.root_cause,
            "failure_type": analysis.failure_type,
            "recovery_probability": (
                analysis.recovery_probability
            ),
            "confidence": analysis.confidence,
        },
    )

    # --------------------------------------------------
    # 5. Day 6 — deterministic recovery policy
    # --------------------------------------------------

    recovery_action = decide_recovery_action(
        root_cause=analysis.root_cause,
        failure_type=analysis.failure_type,
        recovery_probability=(
            analysis.recovery_probability
        ),
        confidence=analysis.confidence,
        failed_attempt_count=(
            risk_case["failed_attempt_count"]
        ),
        latest_attempt_number=(
            risk_case["latest_attempt_number"]
        ),
    )

    log_audit_event(
        connection=connection,
        recovery_case_id=recovery_case_id,
        event_type="recovery_decision",
        actor="ai_agent",
        message=(
            f"Recommended action: "
            f"{recovery_action.action}."
        ),
        metadata={
            "action": recovery_action.action,
            "reasoning": recovery_action.reasoning,
            "confidence": recovery_action.confidence,
        },
    )

    # --------------------------------------------------
    # 6. Day 9 — Guardrail validation
    # --------------------------------------------------

    guardrail_result = validate_recovery_action(
        connection=connection,
        subscription_id=(
            risk_case["subscription_id"]
        ),
        recovery_case_id=recovery_case_id,
        action=recovery_action.action,
        root_cause=analysis.root_cause,
        retry_count=(
            risk_case["failed_attempt_count"]
        ),
    )

    log_audit_event(
        connection=connection,
        recovery_case_id=recovery_case_id,
        event_type="guardrail_evaluated",
        actor="policy_engine",
        message=(
            f"Guardrail evaluation: "
            f"{guardrail_result.action}."
        ),
        metadata={
            "approved": guardrail_result.approved,
            "action": guardrail_result.action,
            "reason": guardrail_result.reason,
        },
    )

    # --------------------------------------------------
    # 7. Execute only after guardrail validation
    # --------------------------------------------------

    if guardrail_result.approved:

        execution_result = execute_recovery_action(
            action=recovery_action.action,
            amount=risk_case["revenue_at_risk"],
        )

    else:

        execution_result = execute_recovery_action(
            action=guardrail_result.action,
            amount=risk_case["revenue_at_risk"],
        )

    # --------------------------------------------------
    # 8. Audit: action executed
    # --------------------------------------------------

    log_audit_event(
        connection=connection,
        recovery_case_id=recovery_case_id,
        event_type="action_executed",
        actor="executor",
        message=(
            f"Recovery action executed: "
            f"{execution_result['execution_status']}."
        ),
        metadata={
            "action": execution_result["action"],
            "execution_status": (
                execution_result["execution_status"]
            ),
            "payment_status": (
                execution_result["payment_status"]
            ),
            "amount_recovered": (
                execution_result["amount_recovered"]
            ),
        },
    )

    # --------------------------------------------------
    # 9. Audit: workflow stopped/completed
    # --------------------------------------------------

    if execution_result["execution_status"] in {
        "COMPLETED",
        "ESCALATED",
        "STOPPED",
        "WAITING_FOR_CUSTOMER",
    }:

        log_audit_event(
            connection=connection,
            recovery_case_id=recovery_case_id,
            event_type="workflow_stopped",
            actor="system",
            message=(
                "Recovery workflow completed "
                "its current execution step."
            ),
            metadata={
                "execution_status": (
                    execution_result[
                        "execution_status"
                    ]
                ),
                "payment_status": (
                    execution_result[
                        "payment_status"
                    ]
                ),
            },
        )

    # --------------------------------------------------
    # 10. Return complete result
    # --------------------------------------------------

    return {
        "risk_case": risk_case,
        "ai_analysis": analysis.model_dump(),
        "recovery_decision": (
            recovery_action.model_dump()
        ),
        "guardrail_result": (
            guardrail_result.model_dump()
        ),
        "execution_result": execution_result,
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

                execution = result["execution_result"]

                print(
                    f"Execution: "
                    f"{execution['execution_status']}"
                )

                print(
                    f"Payment: "
                    f"{execution['payment_status']}"
                )

                print(
                    f"Recovered: "
                    f"₹{execution['amount_recovered']:.2f}"
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
        limit=1
    )

    if results:
        import pprint
        pprint.pp(results[0])

    print_pipeline_summary(
        results,
        errors,
    )