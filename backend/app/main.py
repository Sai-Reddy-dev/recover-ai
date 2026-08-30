from fastapi import FastAPI, HTTPException

from app.database import get_connection
from app.detector import detect_revenue_risk
from payment_degradation_detector import detect_payment_degradation
from ai_analysis_service import analyze_one_risk_case
from recovery_pipeline import run_recovery_pipeline

app = FastAPI(
    title="RecoverAI",
    description="AI Subscription Revenue Recovery Agent",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "service": "RecoverAI",
        "status": "running",
        "version": "0.1.0",
    }


@app.post("/detect")
def detect():
    try:
        connection = get_connection()

        try:
            cases = detect_revenue_risk(connection)
        finally:
            connection.close()

        revenue_at_risk = sum(
            case["revenue_at_risk"]
            for case in cases
        )

        high_risk_cases = sum(
            1
            for case in cases
            if case["severity"] in ["HIGH", "CRITICAL"]
        )

        return {
            "cases_detected": len(cases),
            "revenue_at_risk": round(revenue_at_risk, 2),
            "high_risk_cases": high_risk_cases,
            "cases": cases,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

@app.get("/degradation")
def degradation():
    try:
        connection = get_connection()

        try:
            results = detect_payment_degradation(connection)
        finally:
            connection.close()

        degraded_methods = [
            result
            for result in results
            if result["status"] == "DEGRADED"
        ]

        affected_subscriptions = sum(
            result["affected_subscriptions"]
            for result in degraded_methods
        )

        revenue_at_risk = sum(
            result["revenue_at_risk"]
            for result in degraded_methods
        )

        return {
            "degraded_methods": len(degraded_methods),
            "affected_subscriptions": affected_subscriptions,
            "revenue_at_risk": round(
                revenue_at_risk,
                2,
            ),
            "degradations": results,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

@app.post("/analyze")
def analyze():
    try:
        result = analyze_one_risk_case()

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

@app.post("/recover")
def recover():
    try:
        results, errors = run_recovery_pipeline(
            limit=100
        )

        total_revenue_at_risk = sum(
            result["risk_case"]["revenue_at_risk"]
            for result in results
        )

        action_counts = {}

        for result in results:
            action = result[
                "recovery_decision"
            ]["action"]

            action_counts[action] = (
                action_counts.get(action, 0) + 1
            )

        if errors:
            status = "PARTIAL"
        else:
            status = "COMPLETE"

        return {
            "status": status,
            "cases_requested": 100,
            "cases_processed": len(results),
            "cases_with_errors": len(errors),
            "revenue_at_risk_processed": round(
                total_revenue_at_risk,
                2,
            ),
            "recovery_actions": action_counts,
            "results": results,
            "errors": errors,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )
