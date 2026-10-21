"""Financial Risk Analysis Agent - Analyzes financial metrics and risk."""

import json
import subprocess
from typing import Dict, Any
from agents.base_agent import BaseAgent
from schemas.agent_responses import RiskAnalysisResponse
from schemas.loan_application import LoanApplication


class FinancialRiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("FinancialRiskAgent")
        self.mcp_process = None

    def start_mcp_server(self) -> None:
        """Start the RiskRulesDB MCP server."""
        try:
            self.mcp_process = subprocess.Popen(
                ["python", "mcp_servers/risk_rules_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            print(f"Error starting MCP server: {e}")

    def call_mcp_tool(self, tool_name: str, **kwargs) -> str:
        """Directly call MCP server tool (mock implementation for now)."""
        from mcp_servers.risk_rules_server import (
            calculate_dti_ratio,
            assess_credit_risk,
            assess_loan_risk,
            detect_anomalies,
            generate_risk_analysis,
        )

        if tool_name == "calculate_dti_ratio":
            return json.dumps(
                calculate_dti_ratio(
                    kwargs.get("monthly_income"),
                    kwargs.get("monthly_liabilities"),
                )
            )
        elif tool_name == "assess_credit_risk":
            return json.dumps(assess_credit_risk(kwargs.get("credit_score")))
        elif tool_name == "assess_loan_risk":
            return json.dumps(
                assess_loan_risk(
                    kwargs.get("loan_amount"),
                    kwargs.get("annual_income"),
                    kwargs.get("tenure_years"),
                    kwargs.get("existing_liabilities"),
                )
            )
        elif tool_name == "detect_anomalies":
            return json.dumps(
                detect_anomalies(
                    kwargs.get("credit_score"),
                    kwargs.get("age"),
                    kwargs.get("income"),
                    kwargs.get("loan_amount"),
                    kwargs.get("dti_ratio"),
                )
            )
        elif tool_name == "generate_risk_analysis":
            return generate_risk_analysis(
                kwargs.get("applicant_id"),
                kwargs.get("credit_score"),
                kwargs.get("annual_income"),
                kwargs.get("loan_amount"),
                kwargs.get("tenure_years"),
                kwargs.get("existing_liabilities"),
                kwargs.get("age"),
            )
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def analyze(self, application: LoanApplication) -> RiskAnalysisResponse:
        """Analyze financial risk."""

        monthly_income = application.income / 12
        monthly_liabilities = application.existing_liabilities / 12

        prompt = f"""Analyze the financial risk for the following loan application:

Applicant ID: {application.applicant_id}
Annual Income: ${application.income}
Credit Score: {application.credit_score}
Requested Loan Amount: ${application.loan_amount}
Loan Tenure: {application.tenure} years
Existing Liabilities: ${application.existing_liabilities}
Age: {application.age}

Please use the following tools to perform risk analysis:
1. calculate_dti_ratio - to calculate debt-to-income ratio
2. assess_credit_risk - to assess credit score risk
3. assess_loan_risk - to assess loan amount risk
4. detect_anomalies - to detect any financial anomalies
5. generate_risk_analysis - to create comprehensive analysis

After gathering the data, provide a detailed risk assessment."""

        tools = [
            {
                "name": "calculate_dti_ratio",
                "description": "Calculate Debt-to-Income ratio",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "monthly_income": {
                            "type": "number",
                            "description": "Monthly income",
                        },
                        "monthly_liabilities": {
                            "type": "number",
                            "description": "Monthly liabilities",
                        },
                    },
                    "required": ["monthly_income", "monthly_liabilities"],
                },
            },
            {
                "name": "assess_credit_risk",
                "description": "Assess credit risk based on credit score",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "credit_score": {
                            "type": "integer",
                            "description": "Credit score",
                        }
                    },
                    "required": ["credit_score"],
                },
            },
            {
                "name": "assess_loan_risk",
                "description": "Assess loan amount risk",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "loan_amount": {
                            "type": "number",
                            "description": "Loan amount",
                        },
                        "annual_income": {
                            "type": "number",
                            "description": "Annual income",
                        },
                        "tenure_years": {
                            "type": "integer",
                            "description": "Loan tenure in years",
                        },
                        "existing_liabilities": {
                            "type": "number",
                            "description": "Existing liabilities",
                        },
                    },
                    "required": [
                        "loan_amount",
                        "annual_income",
                        "tenure_years",
                        "existing_liabilities",
                    ],
                },
            },
            {
                "name": "detect_anomalies",
                "description": "Detect financial anomalies",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "credit_score": {
                            "type": "integer",
                            "description": "Credit score",
                        },
                        "age": {"type": "integer", "description": "Applicant age"},
                        "income": {
                            "type": "number",
                            "description": "Annual income",
                        },
                        "loan_amount": {
                            "type": "number",
                            "description": "Loan amount",
                        },
                        "dti_ratio": {
                            "type": "number",
                            "description": "DTI ratio",
                        },
                    },
                    "required": ["credit_score", "age", "income", "loan_amount", "dti_ratio"],
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
                "Based on the gathered data, summarize the financial risk assessment."
            )

        risk_result = self.call_mcp_tool(
            "generate_risk_analysis",
            applicant_id=application.applicant_id,
            credit_score=application.credit_score,
            annual_income=application.income,
            loan_amount=application.loan_amount,
            tenure_years=application.tenure,
            existing_liabilities=application.existing_liabilities,
            age=application.age,
        )
        return RiskAnalysisResponse(**json.loads(risk_result))

    def cleanup(self) -> None:
        """Stop MCP server."""
        if self.mcp_process:
            self.mcp_process.terminate()
