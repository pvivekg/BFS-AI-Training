#!/usr/bin/env python3
"""DecisionSynthesis MCP Server - Provides loan decision synthesis tools."""

import json
from fastmcp import Server
from schemas.common import Decision, RiskLevel
from schemas.agent_responses import LoanDecisionResponse
from datetime import datetime

app = Server("decision_synthesis_server")


@app.tool()
def synthesize_decision(
    applicant_id: str,
    income_stability_score: float,
    employment_risk: str,
    dti_ratio: float,
    credit_risk_level: str,
    loan_amount_risk: str,
    anomaly_flags: list,
    age: int,
) -> dict:
    """Synthesize all risk factors into a loan decision."""

    risk_score = calculate_risk_score(
        income_stability_score,
        employment_risk,
        dti_ratio,
        credit_risk_level,
        loan_amount_risk,
        anomaly_flags,
    )

    if risk_score < 30:
        classification = Decision.APPROVE
        confidence = 0.95
    elif risk_score < 50:
        classification = Decision.APPROVE
        confidence = 0.75
    elif risk_score < 65:
        classification = Decision.REVIEW
        confidence = 0.80
    elif risk_score < 80:
        classification = Decision.REJECT
        confidence = 0.75
    else:
        classification = Decision.REJECT
        confidence = 0.95

    return {
        "applicant_id": applicant_id,
        "classification": classification.value,
        "risk_score": round(risk_score, 2),
        "confidence_level": round(confidence, 2),
    }


@app.tool()
def calculate_risk_score(
    income_stability_score: float,
    employment_risk: str,
    dti_ratio: float,
    credit_risk_level: str,
    loan_amount_risk: str,
    anomaly_flags: list,
) -> float:
    """Calculate overall risk score (0-100)."""

    score = 50

    score -= income_stability_score * 0.25

    employment_risk_map = {
        RiskLevel.LOW.value: -10,
        RiskLevel.MEDIUM.value: 0,
        RiskLevel.HIGH.value: 10,
        RiskLevel.VERY_HIGH.value: 20,
    }
    score += employment_risk_map.get(employment_risk, 0)

    if dti_ratio < 0.3:
        score -= 15
    elif dti_ratio < 0.5:
        score -= 8
    elif dti_ratio < 0.7:
        score += 5
    else:
        score += 15

    credit_risk_map = {
        RiskLevel.LOW.value: -15,
        RiskLevel.MEDIUM.value: -5,
        RiskLevel.HIGH.value: 10,
        RiskLevel.VERY_HIGH.value: 20,
    }
    score += credit_risk_map.get(credit_risk_level, 0)

    loan_amount_risk_map = {
        RiskLevel.LOW.value: -10,
        RiskLevel.MEDIUM.value: 0,
        RiskLevel.HIGH.value: 15,
        RiskLevel.VERY_HIGH.value: 25,
    }
    score += loan_amount_risk_map.get(loan_amount_risk, 0)

    score += len(anomaly_flags) * 10

    return max(0, min(100, score))


@app.tool()
def explain_decision(
    applicant_id: str,
    classification: str,
    risk_score: float,
    income_stability_score: float,
    employment_risk: str,
    credit_risk_level: str,
    loan_amount_risk: str,
    dti_ratio: float,
    anomaly_flags: list,
) -> dict:
    """Generate explanation for the decision."""

    factors = []

    if income_stability_score >= 70:
        factors.append(
            f"Strong income stability ({income_stability_score:.0f}%) supports approval"
        )
    else:
        factors.append(
            f"Income stability concerns ({income_stability_score:.0f}%) raise questions"
        )

    if employment_risk == RiskLevel.LOW.value:
        factors.append("Stable employment status is positive")
    elif employment_risk == RiskLevel.VERY_HIGH.value:
        factors.append("Employment risk is a significant concern")

    if credit_risk_level == RiskLevel.LOW.value:
        factors.append("Excellent credit history supports approval")
    elif credit_risk_level == RiskLevel.VERY_HIGH.value:
        factors.append("Poor credit history raises concerns")

    if dti_ratio < 0.4:
        factors.append(
            f"Low debt-to-income ratio ({dti_ratio:.2%}) supports approval"
        )
    elif dti_ratio > 0.6:
        factors.append(
            f"High debt-to-income ratio ({dti_ratio:.2%}) raises concerns"
        )

    if loan_amount_risk != RiskLevel.LOW.value:
        factors.append(f"Loan amount risk level is {loan_amount_risk}")

    if anomaly_flags:
        factors.append(f"Detected {len(anomaly_flags)} anomalies in application")

    explanation = (
        f"Decision: {classification.upper()}. Risk Score: {risk_score:.0f}/100. "
    )
    explanation += " ".join(factors)

    return {
        "applicant_id": applicant_id,
        "key_factors": factors,
        "explanation": explanation,
    }


@app.tool()
def generate_decision_report(
    applicant_id: str,
    income_stability_score: float,
    employment_risk: str,
    dti_ratio: float,
    credit_score: int,
    credit_risk_level: str,
    loan_amount_risk: str,
    anomaly_flags: list,
    age: int,
) -> str:
    """Generate comprehensive loan decision report."""

    synthesis = synthesize_decision(
        applicant_id,
        income_stability_score,
        employment_risk,
        dti_ratio,
        credit_risk_level,
        loan_amount_risk,
        anomaly_flags,
        age,
    )

    risk_score = synthesis["risk_score"]

    explanation_data = explain_decision(
        applicant_id,
        synthesis["classification"],
        risk_score,
        income_stability_score,
        employment_risk,
        credit_risk_level,
        loan_amount_risk,
        dti_ratio,
        anomaly_flags,
    )

    response = LoanDecisionResponse(
        applicant_id=applicant_id,
        classification=synthesis["classification"],
        risk_score=risk_score,
        confidence_level=synthesis["confidence_level"],
        key_decision_factors=explanation_data["key_factors"],
        explanation=explanation_data["explanation"],
    )

    return response.model_dump_json()


if __name__ == "__main__":
    app.run()
