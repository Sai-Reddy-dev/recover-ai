from app.database import get_connection
from app.detector import detect_revenue_risk
from recovery_decision_agent import decide_recovery_action

from root_cause_agent import (
    analyze_root_cause,
    get_payment_evidence_for_subscription,
    build_payment_evidence,
)


def analyze_one_risk_case():

    connection = get_connection()

    try:
        # Step 1: Run the existing Day 3 detector
        cases = detect_revenue_risk(connection)

        if not cases:
            raise RuntimeError(
                "No revenue risk cases found."
            )

        # Step 2: Select one real risk case
        risk_case = cases[0]

        print("\nSelected Risk Case")
        print("=" * 60)
        print(risk_case)

        # Step 3: Get real payment evidence
        row = get_payment_evidence_for_subscription(
            connection,
            risk_case["subscription_id"],
        )

        evidence = build_payment_evidence(
            connection,
            row,
        )

        # Step 4: Send evidence to Gemini
        analysis = analyze_root_cause(
            evidence
        )

        
        recovery_action = decide_recovery_action(
            root_cause=analysis.root_cause,
            failure_type=analysis.failure_type,
            recovery_probability=analysis.recovery_probability,
            confidence=analysis.confidence,
            failed_attempt_count=risk_case["failed_attempt_count"],
            latest_attempt_number=risk_case["latest_attempt_number"],
        )

        # Step 5: Combine deterministic + AI results
        result = {
            "risk_case": risk_case,
            "ai_analysis": analysis.model_dump(),
            "recovery_decision": recovery_action.model_dump(),
        }

        return result

    finally:
        connection.close()


if __name__ == "__main__":

    result = analyze_one_risk_case()

    print("\nAI Analysis Result")
    print("=" * 60)
    print(result)