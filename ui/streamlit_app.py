"""Streamlit-based chatbot UI for loan application submission and status tracking."""

import streamlit as st
import requests
import json
from datetime import datetime
from schemas.common import EmploymentType, Location

st.set_page_config(
    page_title="Loan Application System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000"

st.title("🏦 AI-Powered Loan Application System")
st.markdown(
    "Submit your loan application and receive an instant decision powered by multi-agent AI"
)

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select a page:",
        ["📝 Submit Application", "📊 View Status", "📈 System Statistics"],
    )

if page == "📝 Submit Application":
    st.header("Submit Loan Application")

    with st.form("loan_application_form"):
        col1, col2 = st.columns(2)

        with col1:
            applicant_id = st.text_input(
                "Applicant ID",
                value="APP001",
                help="Unique identifier for the applicant",
            )
            age = st.number_input(
                "Age",
                min_value=18,
                max_value=100,
                value=35,
                help="Applicant age in years",
            )
            income = st.number_input(
                "Annual Income ($)",
                min_value=0,
                value=75000,
                step=1000,
                help="Annual income in dollars",
            )
            employment_type = st.selectbox(
                "Employment Type",
                [e.value for e in EmploymentType],
                help="Type of employment",
            )

        with col2:
            credit_score = st.number_input(
                "Credit Score",
                min_value=300,
                max_value=850,
                value=720,
                help="Credit score (300-850)",
            )
            loan_amount = st.number_input(
                "Loan Amount ($)",
                min_value=1000,
                value=250000,
                step=1000,
                help="Requested loan amount",
            )
            tenure = st.number_input(
                "Loan Tenure (Years)",
                min_value=1,
                max_value=30,
                value=20,
                help="Loan repayment period",
            )
            existing_liabilities = st.number_input(
                "Existing Liabilities ($)",
                min_value=0,
                value=50000,
                step=1000,
                help="Current outstanding debts",
            )

        location = st.selectbox(
            "Location",
            [l.value for l in Location],
            help="Applicant location",
        )

        submit_button = st.form_submit_button("Submit Application", use_container_width=True)

    if submit_button:
        with st.spinner("Processing your application... Please wait."):
            try:
                payload = {
                    "applicant_id": applicant_id,
                    "age": age,
                    "income": income,
                    "employment_type": employment_type,
                    "credit_score": credit_score,
                    "loan_amount": loan_amount,
                    "tenure": tenure,
                    "existing_liabilities": existing_liabilities,
                    "location": location,
                }

                response = requests.post(f"{API_URL}/api/applications", json=payload)

                if response.status_code == 200:
                    result = response.json()
                    st.session_state.last_application_id = result.get("application_id")

                    st.success("✅ Application processed successfully!")

                    decision = result.get("decision", {})
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Decision",
                            decision.get("classification", "N/A").upper(),
                        )
                    with col2:
                        st.metric(
                            "Risk Score",
                            f"{decision.get('risk_score', 0):.1f}/100",
                        )
                    with col3:
                        st.metric(
                            "Confidence",
                            f"{decision.get('confidence_level', 0) * 100:.1f}%",
                        )

                    st.info(f"📋 Application ID: {result.get('application_id')}")

                    st.markdown("### Decision Explanation")
                    st.write(decision.get("explanation", "No explanation available"))

                    st.markdown("### Key Decision Factors")
                    factors = decision.get("key_factors", [])
                    if factors:
                        for factor in factors:
                            st.write(f"• {factor}")
                    else:
                        st.write("No specific factors available")

                    st.markdown("### Processing Details")
                    st.json(
                        {
                            "Processing Time": f"{result.get('processing_time', 0):.2f}s",
                            "Status": result.get("status"),
                            "Timestamp": result.get("timestamp"),
                        }
                    )

                else:
                    error_data = response.json() if response.text else {}
                    st.error(
                        f"❌ Error processing application: {error_data.get('detail', 'Unknown error')}"
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot connect to API. Make sure FastAPI server is running on http://localhost:8000"
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

elif page == "📊 View Status":
    st.header("Application Status Tracker")

    application_id = st.text_input(
        "Enter Application ID",
        value=st.session_state.get("last_application_id", ""),
        placeholder="e.g., APP001 or returned application ID",
    )

    if st.button("Retrieve Status", use_container_width=True):
        if not application_id:
            st.warning("Please enter an application ID")
        else:
            try:
                response = requests.get(
                    f"{API_URL}/api/applications/{application_id}"
                )

                if response.status_code == 200:
                    app_data = response.json()

                    st.success(f"✅ Status for Application {application_id}")

                    st.markdown("### Application Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Applicant ID", app_data.get("applicant_id"))
                    with col2:
                        st.metric("Status", app_data.get("status", "Unknown").upper())
                    with col3:
                        st.metric(
                            "Created",
                            datetime.fromisoformat(
                                app_data.get("created_at", "")
                            ).strftime("%Y-%m-%d %H:%M"),
                        )

                    if app_data.get("decision"):
                        st.markdown("### Decision Details")
                        decision = app_data["decision"]
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Classification", decision.get("classification", "N/A").upper())
                        with col2:
                            st.metric("Risk Score", f"{decision.get('risk_score', 0):.1f}/100")
                        with col3:
                            st.metric("Confidence", f"{decision.get('confidence_level', 0) * 100:.1f}%")

                        st.markdown(f"**Explanation:** {decision.get('explanation', 'N/A')}")

                        if decision.get("key_factors"):
                            st.markdown("**Key Factors:**")
                            for factor in decision["key_factors"]:
                                st.write(f"• {factor}")

                    with st.expander("View Complete Analysis"):
                        st.json(app_data)

                elif response.status_code == 404:
                    st.error("❌ Application not found")
                else:
                    st.error(f"❌ Error retrieving application: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

elif page == "📈 System Statistics":
    st.header("System Statistics")

    try:
        response = requests.get(f"{API_URL}/api/stats")

        if response.status_code == 200:
            stats = response.json()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Applications", stats.get("total_applications", 0))
            with col2:
                st.metric("Approved", stats.get("approved", 0))
            with col3:
                st.metric("Rejected", stats.get("rejected", 0))
            with col4:
                st.metric("Under Review", stats.get("review", 0))

            approval_rate = stats.get("approval_rate", 0)
            st.metric("Approval Rate", f"{approval_rate:.1f}%")

            st.markdown("### Processing Health")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Failed", stats.get("failed", 0))

            st.markdown("---")
            st.info(
                "💡 This dashboard shows statistics for all applications processed in this session. "
                "Refresh the page to get updated statistics."
            )

        else:
            st.error("❌ Error retrieving statistics")

    except requests.exceptions.ConnectionError:
        st.error(
            "❌ Cannot connect to API. Make sure FastAPI server is running on http://localhost:8000"
        )
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.markdown(
    """
    ### About This System

    This AI-powered loan application system uses:
    - **Multi-Agent Architecture**: Specialized agents for different evaluation aspects
    - **LangGraph Orchestration**: Coordinated workflow management
    - **MCP Servers**: Standardized tool communication
    - **Claude Sonnet 4.6**: Advanced language model for decision synthesis

    **Agents:**
    1. **Applicant Profile Agent** - Analyzes background and employment
    2. **Financial Risk Agent** - Assesses financial metrics
    3. **Loan Decision Agent** - Synthesizes decision
    4. **Compliance Orchestrator** - Executes decision and creates audit trail
    """
)
