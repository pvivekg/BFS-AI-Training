#!/usr/bin/env python3
"""RiskRulesDB MCP Server - Provides financial risk analysis tools."""

import json
from fastmcp import Server
from schemas.common import RiskLevel
from schemas.agent_responses import RiskAnalysisResponse
from datetime import datetime

app = Server("risk_rules_server")


@app.tool()
def calculate_dti_ratio(monthly_income: float, monthly_liabilities: float) -> dict:
    """Calculate Debt-to-Income (DTI) ratio."""
    if monthly_income <= 0:
        return {"error": "Monthly income must be positive"}

    dti = monthly_liabilities / monthly_income
    return {
        "monthly_income": monthly_income,
        "monthly_liabilities": monthly_liabilities,
        "dti_ratio": round(dti, 3),
        "dti_percentage": round(dti * 100, 2),
    }


@app.tool()
def assess_credit_risk(credit_score: int) -> dict:
    """Assess credit risk based on credit score."""
    if credit_score < 300 or credit_score > 850:
        return {"error": "Credit score must be between 300 and 850"}

    if credit_score >= 750:
        risk_level = RiskLevel.LOW
        risk_description = "Excellent credit profile"
    elif credit_score >= 700:
        risk_level = RiskLevel.MEDIUM
        risk_description = "Good credit profile"
    elif credit_score >= 650:
        risk_level = RiskLevel.HIGH
        risk_description = "Fair credit profile"
    else:
        risk_level = RiskLevel.VERY_HIGH
        risk_description = "Poor credit profile"

    return {
        "credit_score": credit_score,
        "credit_risk_level": risk_level.value,
        "risk_description": risk_description,
    }


@app.tool()
def assess_loan_risk(
    loan_amount: float,
    annual_income: float,
    tenure_years: int,
    existing_liabilities: float,
) -> dict:
    """Assess loan risk based on loan parameters."""
    loan_to_income_ratio = loan_amount / annual_income
    monthly_payment_estimate = (loan_amount / (tenure_years * 12)) + (
        existing_liabilities / 12
    )
    monthly_income = annual_income / 12

    if monthly_income > 0:
        loan_payment_ratio = monthly_payment_estimate / monthly_income
    else:
        loan_payment_ratio = float("inf")

    if loan_to_income_ratio <= 3 and loan_payment_ratio <= 0.4:
        risk_level = RiskLevel.LOW
    elif loan_to_income_ratio <= 5 and loan_payment_ratio <= 0.5:
        risk_level = RiskLevel.MEDIUM
    elif loan_to_income_ratio <= 8 and loan_payment_ratio <= 0.6:
        risk_level = RiskLevel.HIGH
    else:
        risk_level = RiskLevel.VERY_HIGH

    return {
        "loan_amount": loan_amount,
        "annual_income": annual_income,
        "tenure_years": tenure_years,
        "loan_to_income_ratio": round(loan_to_income_ratio, 3),
        "estimated_monthly_payment": round(monthly_payment_estimate, 2),
        "payment_to_income_ratio": round(loan_payment_ratio, 3),
        "loan_amount_risk": risk_level.value,
    }


@app.tool()
def detect_anomalies(
    credit_score: int,
    age: int,
    income: float,
    loan_amount: float,
    dti_ratio: float,
) -> dict:
    """Detect financial anomalies in application."""
    anomalies = []

    if age < 25 and credit_score < 650:
        anomalies.append("Young age with low credit score")

    if loan_amount > income * 10:
        anomalies.append("Loan amount significantly exceeds annual income")

    if dti_ratio > 0.7:
        anomalies.append("Extremely high debt-to-income ratio")

    if income < 30000 and loan_amount > 200000:
        anomalies.append("High loan amount relative to income level")

    return {
        "anomalies_detected": len(anomalies) > 0,
        "anomaly_flags": anomalies,
        "anomaly_count": len(anomalies),
    }


@app.tool()
def generate_risk_analysis(
    applicant_id: str,
    credit_score: int,
    annual_income: float,
    loan_amount: float,
    tenure_years: int,
    existing_liabilities: float,
    age: int,
) -> str:
    """Generate comprehensive financial risk analysis."""
    monthly_income = annual_income / 12
    monthly_liabilities = existing_liabilities / 12

    dti_data = calculate_dti_ratio(monthly_income, monthly_liabilities)
    dti_ratio = dti_data.get("dti_ratio", 0)

    credit_risk_data = assess_credit_risk(credit_score)
    loan_risk_data = assess_loan_risk(
        loan_amount, annual_income, tenure_years, existing_liabilities
    )
    anomalies_data = detect_anomalies(
        credit_score, age, annual_income, loan_amount, dti_ratio
    )

    reasoning = f"DTI ratio of {dti_data['dti_percentage']}% indicates "
    if dti_ratio < 0.3:
        reasoning += "excellent debt management. "
    elif dti_ratio < 0.5:
        reasoning += "good debt management. "
    else:
        reasoning += "concerning debt levels. "

    reasoning += f"Credit score of {credit_score} shows {credit_risk_data['risk_description'].lower()}. "
    reasoning += f"Loan-to-income ratio of {loan_risk_data['loan_to_income_ratio']} suggests {loan_risk_data['loan_amount_risk']} risk."

    response = RiskAnalysisResponse(
        applicant_id=applicant_id,
        debt_to_income_ratio=dti_ratio,
        credit_score_risk_level=credit_risk_data["credit_risk_level"],
        loan_amount_risk=loan_risk_data["loan_amount_risk"],
        anomaly_detection_flags=anomalies_data["anomaly_flags"],
        reasoning=reasoning,
    )

    return response.model_dump_json()


if __name__ == "__main__":
    app.run()
