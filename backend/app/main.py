from fastapi import FastAPI, HTTPException

from app.database import get_connection
from app.detector import detect_revenue_risk


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