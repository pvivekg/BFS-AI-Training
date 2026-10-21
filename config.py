import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    FASTAPI_HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
    FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))
    FASTAPI_DEBUG = os.getenv("FASTAPI_DEBUG", "False").lower() == "true"

    MCP_APPLICANT_DB_PORT = int(os.getenv("MCP_APPLICANT_DB_PORT", 8001))
    MCP_RISK_RULES_PORT = int(os.getenv("MCP_RISK_RULES_PORT", 8002))
    MCP_DECISION_SYNTHESIS_PORT = int(os.getenv("MCP_DECISION_SYNTHESIS_PORT", 8003))
    MCP_NOTIFICATION_PORT = int(os.getenv("MCP_NOTIFICATION_PORT", 8004))

    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8501))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

config = Config()
