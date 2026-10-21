"""Loan Decision Agent - Synthesizes analysis into approval/rejection decision."""

import json
import subprocess
from typing import Dict, Any
from agents.base_agent import BaseAgent
from schemas.agent_responses import LoanDecisionResponse, ApplicantProfileResponse, RiskAnalysisResponse
from schemas.loan_application import LoanApplication


class LoanDecisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("LoanDecisionAgent")
        self.mcp_process = None

    def start_mcp_server(self) -> None:
        """Start the DecisionSynthesis MCP server."""
        try:
            self.mcp_process = subprocess.Popen(
                ["python", "mcp_servers/decision_synthesis_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            print(f"Error starting MCP server: {e}")

    def call_mcp_tool(self, tool_name: str, **kwargs) -> str:
        """Directly call MCP server tool (mock implementation for now)."""
        from mcp_servers.decision_synthesis_server import (
            synthesize_decision,
            calculate_risk_score,
            explain_decision,
            generate_decision_report,
        )

        if tool_name == "synthesize_decision":
            return json.dumps(
                synthesize_decision(
                    kwargs.get("applicant_id"),
                    kwargs.get("income_stability_score"),
                    kwargs.get("employment_risk"),
                    kwargs.get("dti_ratio"),
                    kwargs.get("credit_risk_level"),
                    kwargs.get("loan_amount_risk"),
                    kwargs.get("anomaly_flags", []),
                    kwargs.get("age"),
                )
            )
        elif tool_name == "calculate_risk_score":
            return json.dumps(
                {
                    "risk_score": calculate_risk_score(
                        kwargs.get("income_stability_score"),
                        kwargs.get("employment_risk"),
                        kwargs.get("dti_ratio"),
                        kwargs.get("credit_risk_level"),
                        kwargs.get("loan_amount_risk"),
                        kwargs.get("anomaly_flags", []),
                    )
                }
            )
        elif tool_name == "explain_decision":
            return json.dumps(
                explain_decision(
                    kwargs.get("applicant_id"),
                    kwargs.get("classification"),
                    kwargs.get("risk_score"),
                    kwargs.get("income_stability_score"),
                    kwargs.get("employment_risk"),
                    kwargs.get("credit_risk_level"),
                    kwargs.get("loan_amount_risk"),
                    kwargs.get("dti_ratio"),
                    kwargs.get("anomaly_flags", []),
                )
            )
        elif tool_name == "generate_decision_report":
            return generate_decision_report(
                kwargs.get("applicant_id"),
                kwargs.get("income_stability_score"),
                kwargs.get("employment_risk"),
                kwargs.get("dti_ratio"),
                kwargs.get("credit_score"),
                kwargs.get("credit_risk_level"),
                kwargs.get("loan_amount_risk"),
                kwargs.get("anomaly_flags", []),
                kwargs.get("age"),
            )
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def decide(
        self,
        application: LoanApplication,
        applicant_analysis: ApplicantProfileResponse,
        risk_analysis: RiskAnalysisResponse,
    ) -> LoanDecisionResponse:
        """Make loan decision based on analysis."""

        prompt = f"""Based on the applicant profile and financial risk analysis, make a loan decision:

Applicant ID: {application.applicant_id}
Age: {application.age}
Credit Score: {application.credit_score}

Applicant Analysis:
- Income Stability Score: {applicant_analysis.income_stability_score}
- Employment Risk: {applicant_analysis.employment_risk}
- Credit History: {applicant_analysis.credit_history_summary}

Financial Risk Analysis:
- DTI Ratio: {risk_analysis.debt_to_income_ratio}
- Credit Risk Level: {risk_analysis.credit_score_risk_level}
- Loan Amount Risk: {risk_analysis.loan_amount_risk}
- Anomalies: {', '.join(risk_analysis.anomaly_detection_flags) if risk_analysis.anomaly_detection_flags else 'None'}

Please use the following tools to synthesize the decision:
1. synthesize_decision - to make the approval/rejection decision
2. explain_decision - to generate explanation for the decision
3. generate_decision_report - to create comprehensive decision report

Provide a final loan decision with reasoning."""

        tools = [
            {
                "name": "synthesize_decision",
                "description": "Synthesize decision based on all factors",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "applicant_id": {
                            "type": "string",
                            "description": "Applicant ID",
                        },
                        "income_stability_score": {
                            "type": "number",
                            "description": "Income stability score",
                        },
                        "employment_risk": {
                            "type": "string",
                            "description": "Employment risk level",
                        },
                        "dti_ratio": {
                            "type": "number",
                            "description": "Debt-to-income ratio",
                        },
                        "credit_risk_level": {
                            "type": "string",
                            "description": "Credit risk level",
                        },
                        "loan_amount_risk": {
                            "type": "string",
                            "description": "Loan amount risk level",
                        },
                        "anomaly_flags": {
                            "type": "array",
                            "description": "Anomaly flags",
                        },
                        "age": {
                            "type": "integer",
                            "description": "Applicant age",
                        },
                    },
                    "required": [
                        "applicant_id",
                        "income_stability_score",
                        "employment_risk",
                        "dti_ratio",
                        "credit_risk_level",
                        "loan_amount_risk",
                        "age",
                    ],
                },
            },
            {
                "name": "explain_decision",
                "description": "Generate explanation for the decision",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "applicant_id": {
                            "type": "string",
                            "description": "Applicant ID",
                        },
                        "classification": {
                            "type": "string",
                            "description": "Decision classification",
                        },
                        "risk_score": {
                            "type": "number",
                            "description": "Risk score",
                        },
                        "income_stability_score": {
                            "type": "number",
                            "description": "Income stability score",
                        },
                        "employment_risk": {
                            "type": "string",
                            "description": "Employment risk level",
                        },
                        "credit_risk_level": {
                            "type": "string",
                            "description": "Credit risk level",
                        },
                        "loan_amount_risk": {
                            "type": "string",
                            "description": "Loan amount risk level",
                        },
                        "dti_ratio": {
                            "type": "number",
                            "description": "Debt-to-income ratio",
                        },
                        "anomaly_flags": {
                            "type": "array",
                            "description": "Anomaly flags",
                        },
                    },
                    "required": [
                        "applicant_id",
                        "classification",
                        "risk_score",
                        "income_stability_score",
                        "employment_risk",
                        "credit_risk_level",
                        "loan_amount_risk",
                        "dti_ratio",
                    ],
                },
            },
        ]

        response = self.think(prompt, tools)

        for tool_call in response.get("tool_calls", []):
            tool_result = self.call_mcp_tool(
                tool_call["name"], **tool_call.get("input", {})
            )
            self.add_tool_result(tool_call["id"], tool_call["name"], tool_result)

        if response.get("tool_calls"):
            final_response = self.think(
                "Based on the synthesized decision, provide the final determination."
            )

        decision_result = self.call_mcp_tool(
            "generate_decision_report",
            applicant_id=application.applicant_id,
            income_stability_score=applicant_analysis.income_stability_score,
            employment_risk=applicant_analysis.employment_risk,
            dti_ratio=risk_analysis.debt_to_income_ratio,
            credit_score=application.credit_score,
            credit_risk_level=risk_analysis.credit_score_risk_level,
            loan_amount_risk=risk_analysis.loan_amount_risk,
            anomaly_flags=risk_analysis.anomaly_detection_flags,
            age=application.age,
        )
        return LoanDecisionResponse(**json.loads(decision_result))

    def cleanup(self) -> None:
        """Stop MCP server."""
        if self.mcp_process:
            self.mcp_process.terminate()
