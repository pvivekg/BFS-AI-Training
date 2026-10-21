#!/usr/bin/env python3
"""ApplicantDB MCP Server - Provides applicant profile and employment data."""

import json
from fastmcp import Server
from schemas.common import EmploymentType, RiskLevel
from schemas.agent_responses import ApplicantProfileResponse
from datetime import datetime

app = Server("applicant_db_server")

# Mock database of applicants
APPLICANT_DATABASE = {
    "APP001": {
        "name": "John Doe",
        "age": 35,
        "income": 75000,
        "employment_type": "employed",
        "employment_tenure_years": 8,
        "employment_stability": "high",
        "credit_history": "Good payment history, minor late payment 2 years ago",
        "credit_age_years": 12,
    },
    "APP002": {
        "name": "Jane Smith",
        "age": 28,
        "income": 95000,
        "employment_type": "employed",
        "employment_tenure_years": 3,
        "employment_stability": "medium",
        "credit_history": "Excellent payment history, no delinquencies",
        "credit_age_years": 8,
    },
    "APP003": {
        "name": "Bob Johnson",
        "age": 45,
        "income": 120000,
        "employment_type": "self_employed",
        "employment_tenure_years": 10,
        "employment_stability": "medium",
        "credit_history": "Good payment history with some variations",
        "credit_age_years": 20,
    },
}


@app.tool()
def get_applicant_profile(applicant_id: str) -> dict:
    """Retrieve applicant profile information."""
    if applicant_id not in APPLICANT_DATABASE:
        return {"error": f"Applicant {applicant_id} not found"}

    applicant = APPLICANT_DATABASE[applicant_id]
    return {
        "applicant_id": applicant_id,
        "name": applicant["name"],
        "age": applicant["age"],
        "income": applicant["income"],
        "employment_type": applicant["employment_type"],
    }


@app.tool()
def get_employment_history(applicant_id: str) -> dict:
    """Retrieve employment history and stability assessment."""
    if applicant_id not in APPLICANT_DATABASE:
        return {"error": f"Applicant {applicant_id} not found"}

    applicant = APPLICANT_DATABASE[applicant_id]

    # Calculate employment risk
    tenure = applicant["employment_tenure_years"]
    if tenure >= 5:
        employment_risk = RiskLevel.LOW
    elif tenure >= 2:
        employment_risk = RiskLevel.MEDIUM
    else:
        employment_risk = RiskLevel.HIGH

    return {
        "applicant_id": applicant_id,
        "employment_type": applicant["employment_type"],
        "employment_tenure_years": tenure,
        "employment_stability": applicant["employment_stability"],
        "employment_risk": employment_risk.value,
        "income_stability_score": min(100, (tenure / 10) * 100),
    }


@app.tool()
def get_credit_history(applicant_id: str) -> dict:
    """Retrieve credit history information."""
    if applicant_id not in APPLICANT_DATABASE:
        return {"error": f"Applicant {applicant_id} not found"}

    applicant = APPLICANT_DATABASE[applicant_id]
    return {
        "applicant_id": applicant_id,
        "credit_history": applicant["credit_history"],
        "credit_age_years": applicant["credit_age_years"],
        "credit_age_assessment": "Established" if applicant["credit_age_years"] >= 10 else "Moderate" if applicant["credit_age_years"] >= 5 else "New",
    }


@app.tool()
def generate_applicant_analysis(applicant_id: str) -> str:
    """Generate comprehensive applicant profile analysis."""
    if applicant_id not in APPLICANT_DATABASE:
        return json.dumps({"error": f"Applicant {applicant_id} not found"})

    applicant = APPLICANT_DATABASE[applicant_id]
    profile_data = get_applicant_profile(applicant_id)
    employment_data = get_employment_history(applicant_id)
    credit_data = get_credit_history(applicant_id)

    completeness_flags = []
    if not applicant.get("name"):
        completeness_flags.append("Missing name")

    response = ApplicantProfileResponse(
        applicant_id=applicant_id,
        income_stability_score=employment_data["income_stability_score"],
        employment_risk=employment_data["employment_risk"],
        credit_history_summary=credit_data["credit_history"],
        application_completeness_flags=completeness_flags,
    )

    return response.model_dump_json()


if __name__ == "__main__":
    app.run()
