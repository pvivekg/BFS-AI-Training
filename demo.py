#!/usr/bin/env python3
"""
Demo script to run the Loan Application system without external dependencies.
Simulates the complete workflow locally.
"""

import json
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List

# Mock enums
class EmploymentType:
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"


class RiskLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class Decision:
    APPROVE = "approve"
    REJECT = "reject"
    REVIEW = "review"


class Status:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Mock data stores
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
}


def analyze_applicant(applicant_id: str, age: int, income: float, employment_type: str) -> dict:
    """Analyze applicant profile."""
    if employment_type == "employed":
        if age > 30:
            stability_score = 85
            employment_risk = RiskLevel.LOW
        else:
            stability_score = 70
            employment_risk = RiskLevel.MEDIUM
    elif employment_type == "self_employed":
        stability_score = 60
        employment_risk = RiskLevel.MEDIUM
    else:
        stability_score = 30
        employment_risk = RiskLevel.HIGH

    return {
        "applicant_id": applicant_id,
        "income_stability_score": stability_score,
        "employment_risk": employment_risk,
        "credit_history_summary": "Good payment history",
        "application_completeness_flags": [],
        "analysis_timestamp": datetime.utcnow().isoformat(),
    }


def analyze_financial_risk(
    applicant_id: str,
    credit_score: int,
    annual_income: float,
    loan_amount: float,
    tenure_years: int,
    existing_liabilities: float,
    age: int,
) -> dict:
    """Analyze financial risk."""
    monthly_income = annual_income / 12
    monthly_liabilities = existing_liabilities / 12

    dti = monthly_liabilities / monthly_income if monthly_income > 0 else 0

    if credit_score >= 750:
        credit_risk = RiskLevel.LOW
    elif credit_score >= 700:
        credit_risk = RiskLevel.MEDIUM
    elif credit_score >= 650:
        credit_risk = RiskLevel.HIGH
    else:
        credit_risk = RiskLevel.VERY_HIGH

    loan_to_income = loan_amount / annual_income if annual_income > 0 else 0
    if loan_to_income <= 3:
        loan_risk = RiskLevel.LOW
    elif loan_to_income <= 5:
        loan_risk = RiskLevel.MEDIUM
    elif loan_to_income <= 8:
        loan_risk = RiskLevel.HIGH
    else:
        loan_risk = RiskLevel.VERY_HIGH

    anomalies = []
    if loan_to_income > 10:
        anomalies.append("Loan amount significantly exceeds annual income")
    if dti > 0.7:
        anomalies.append("Extremely high debt-to-income ratio")

    reasoning = f"DTI ratio of {dti*100:.1f}% indicates "
    if dti < 0.3:
        reasoning += "excellent debt management. "
    elif dti < 0.5:
        reasoning += "good debt management. "
    else:
        reasoning += "concerning debt levels. "
    reasoning += f"Credit score of {credit_score} shows {credit_risk}. "
    reasoning += f"Loan-to-income ratio of {loan_to_income:.2f} suggests {loan_risk} risk."

    return {
        "applicant_id": applicant_id,
        "debt_to_income_ratio": round(dti, 3),
        "credit_score_risk_level": credit_risk,
        "loan_amount_risk": loan_risk,
        "anomaly_detection_flags": anomalies,
        "reasoning": reasoning,
        "analysis_timestamp": datetime.utcnow().isoformat(),
    }


def synthesize_decision(
    applicant_id: str,
    income_stability_score: float,
    employment_risk: str,
    dti_ratio: float,
    credit_risk_level: str,
    loan_amount_risk: str,
    anomaly_flags: List[str],
    age: int,
    credit_score: int,
) -> dict:
    """Synthesize loan decision."""
    score = 50

    score -= income_stability_score * 0.25

    employment_risk_map = {
        RiskLevel.LOW: -10,
        RiskLevel.MEDIUM: 0,
        RiskLevel.HIGH: 10,
        RiskLevel.VERY_HIGH: 20,
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
        RiskLevel.LOW: -15,
        RiskLevel.MEDIUM: -5,
        RiskLevel.HIGH: 10,
        RiskLevel.VERY_HIGH: 20,
    }
    score += credit_risk_map.get(credit_risk_level, 0)

    loan_amount_risk_map = {
        RiskLevel.LOW: -10,
        RiskLevel.MEDIUM: 0,
        RiskLevel.HIGH: 15,
        RiskLevel.VERY_HIGH: 25,
    }
    score += loan_amount_risk_map.get(loan_amount_risk, 0)
    score += len(anomaly_flags) * 10

    score = max(0, min(100, score))

    if score < 30:
        classification = Decision.APPROVE
        confidence = 0.95
    elif score < 50:
        classification = Decision.APPROVE
        confidence = 0.75
    elif score < 65:
        classification = Decision.REVIEW
        confidence = 0.80
    elif score < 80:
        classification = Decision.REJECT
        confidence = 0.75
    else:
        classification = Decision.REJECT
        confidence = 0.95

    factors = []
    if income_stability_score >= 70:
        factors.append(f"Strong income stability ({income_stability_score:.0f}%) supports approval")
    else:
        factors.append(f"Income stability concerns ({income_stability_score:.0f}%) raise questions")

    if employment_risk == RiskLevel.LOW:
        factors.append("Stable employment status is positive")
    elif employment_risk == RiskLevel.VERY_HIGH:
        factors.append("Employment risk is a significant concern")

    if credit_risk_level == RiskLevel.LOW:
        factors.append("Excellent credit history supports approval")
    elif credit_risk_level == RiskLevel.VERY_HIGH:
        factors.append("Poor credit history raises concerns")

    if dti_ratio < 0.4:
        factors.append(f"Low debt-to-income ratio ({dti_ratio:.2%}) supports approval")
    elif dti_ratio > 0.6:
        factors.append(f"High debt-to-income ratio ({dti_ratio:.2%}) raises concerns")

    if loan_amount_risk != RiskLevel.LOW:
        factors.append(f"Loan amount risk level is {loan_amount_risk}")

    if anomaly_flags:
        factors.append(f"Detected {len(anomaly_flags)} anomalies in application")

    explanation = f"Decision: {classification.upper()}. Risk Score: {score:.0f}/100. "
    explanation += " ".join(factors)

    return {
        "applicant_id": applicant_id,
        "classification": classification,
        "risk_score": round(score, 2),
        "confidence_level": round(confidence, 2),
        "key_decision_factors": factors,
        "explanation": explanation,
        "decision_timestamp": datetime.utcnow().isoformat(),
    }


def process_application(app_data: dict) -> dict:
    """Process a complete loan application."""
    start_time = datetime.utcnow()
    application_id = str(uuid.uuid4())

    print("\n" + "=" * 70)
    print(f"📋 Processing Application: {application_id}")
    print("=" * 70)

    print(f"\n1️⃣ Analyzing Applicant Profile...")
    applicant_analysis = analyze_applicant(
        app_data["applicant_id"],
        app_data["age"],
        app_data["income"],
        app_data["employment_type"],
    )
    print(f"   ✅ Income Stability Score: {applicant_analysis['income_stability_score']}")
    print(f"   ✅ Employment Risk: {applicant_analysis['employment_risk']}")

    print(f"\n2️⃣ Analyzing Financial Risk...")
    risk_analysis = analyze_financial_risk(
        app_data["applicant_id"],
        app_data["credit_score"],
        app_data["income"],
        app_data["loan_amount"],
        app_data["tenure"],
        app_data["existing_liabilities"],
        app_data["age"],
    )
    print(f"   ✅ DTI Ratio: {risk_analysis['debt_to_income_ratio']:.3f}")
    print(f"   ✅ Credit Risk: {risk_analysis['credit_score_risk_level']}")
    print(f"   ✅ Loan Amount Risk: {risk_analysis['loan_amount_risk']}")

    print(f"\n3️⃣ Synthesizing Decision...")
    decision = synthesize_decision(
        app_data["applicant_id"],
        applicant_analysis["income_stability_score"],
        applicant_analysis["employment_risk"],
        risk_analysis["debt_to_income_ratio"],
        risk_analysis["credit_score_risk_level"],
        risk_analysis["loan_amount_risk"],
        risk_analysis["anomaly_detection_flags"],
        app_data["age"],
        app_data["credit_score"],
    )
    print(f"   ✅ Decision: {decision['classification'].upper()}")
    print(f"   ✅ Risk Score: {decision['risk_score']}/100")
    print(f"   ✅ Confidence: {decision['confidence_level'] * 100:.1f}%")

    print(f"\n4️⃣ Creating Compliance Record...")
    case_id = f"CASE_{uuid.uuid4().hex[:8].upper()}"
    compliance = {
        "applicant_id": app_data["applicant_id"],
        "case_id": case_id,
        "action_taken": decision["classification"].upper(),
        "notification_sent": True,
        "timestamp": datetime.utcnow().isoformat(),
        "summary": f"Loan application decision executed and applicant notified. Decision: {decision['classification']}",
    }
    print(f"   ✅ Case ID: {case_id}")
    print(f"   ✅ Notification Sent: {compliance['notification_sent']}")

    processing_time = (datetime.utcnow() - start_time).total_seconds()

    result = {
        "application_id": application_id,
        "status": Status.COMPLETED,
        "applicant_id": app_data["applicant_id"],
        "applicant_analysis": applicant_analysis,
        "risk_analysis": risk_analysis,
        "decision": decision,
        "compliance": compliance,
        "processing_time": round(processing_time, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }

    return result


def display_result(result: dict):
    """Display the decision in a formatted way."""
    decision = result["decision"]

    print("\n" + "=" * 70)
    print("🎯 LOAN APPLICATION DECISION")
    print("=" * 70)

    # Decision Summary
    print(f"\n📊 SUMMARY:")
    print(f"   Application ID: {result['application_id']}")
    print(f"   Applicant ID: {result['applicant_id']}")
    print(f"   Status: {result['status'].upper()}")

    # Decision
    decision_color = "🟢" if decision["classification"] == "approve" else "🔴" if decision["classification"] == "reject" else "🟡"
    print(f"\n{decision_color} DECISION: {decision['classification'].upper()}")
    print(f"   Risk Score: {decision['risk_score']}/100")
    print(f"   Confidence Level: {decision['confidence_level'] * 100:.1f}%")

    # Explanation
    print(f"\n📝 EXPLANATION:")
    print(f"   {decision['explanation']}")

    # Key Factors
    print(f"\n🔍 KEY DECISION FACTORS:")
    for i, factor in enumerate(decision["key_decision_factors"], 1):
        print(f"   {i}. {factor}")

    # Processing Info
    print(f"\n⏱️  PROCESSING TIME: {result['processing_time']}s")
    print(f"⏰ TIMESTAMP: {result['timestamp']}")

    print("\n" + "=" * 70)


def main():
    """Main demo function."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🏦 MULTI-AGENT LOAN APPLICATION SYSTEM DEMO".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    # Sample Applications
    sample_applications = [
        {
            "applicant_id": "APP001",
            "age": 35,
            "income": 75000,
            "employment_type": "employed",
            "credit_score": 720,
            "loan_amount": 250000,
            "tenure": 20,
            "existing_liabilities": 50000,
            "location": "New York",
        },
        {
            "applicant_id": "APP002",
            "age": 28,
            "income": 95000,
            "employment_type": "employed",
            "credit_score": 780,
            "loan_amount": 350000,
            "tenure": 25,
            "existing_liabilities": 30000,
            "location": "California",
        },
        {
            "applicant_id": "APP003",
            "age": 45,
            "income": 120000,
            "employment_type": "self_employed",
            "credit_score": 650,
            "loan_amount": 500000,
            "tenure": 30,
            "existing_liabilities": 200000,
            "location": "Texas",
        },
    ]

    results = []

    for app_data in sample_applications:
        result = process_application(app_data)
        results.append(result)
        display_result(result)
        print()

    # Statistics
    print("\n" + "=" * 70)
    print("📈 SYSTEM STATISTICS")
    print("=" * 70)
    total = len(results)
    approved = sum(1 for r in results if r["decision"]["classification"] == "approve")
    rejected = sum(1 for r in results if r["decision"]["classification"] == "reject")
    review = sum(1 for r in results if r["decision"]["classification"] == "review")
    approval_rate = (approved / (total - 0)) * 100 if total > 0 else 0

    print(f"\n   Total Applications Processed: {total}")
    print(f"   ✅ Approved: {approved}")
    print(f"   ❌ Rejected: {rejected}")
    print(f"   🔄 Under Review: {review}")
    print(f"   📊 Approval Rate: {approval_rate:.1f}%")

    print("\n" + "=" * 70)
    print("\n✨ Demo completed successfully!\n")

    # Export results
    with open("demo_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"📁 Results saved to: demo_results.json\n")


if __name__ == "__main__":
    main()
