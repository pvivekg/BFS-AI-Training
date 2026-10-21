#!/usr/bin/env python3
"""Script to start all services for the loan application system."""

import subprocess
import time
import sys
import os
import signal

services = [
    {
        "name": "ApplicantDB MCP Server",
        "command": [sys.executable, "mcp_servers/applicant_db_server.py"],
        "port": 8001,
    },
    {
        "name": "RiskRulesDB MCP Server",
        "command": [sys.executable, "mcp_servers/risk_rules_server.py"],
        "port": 8002,
    },
    {
        "name": "DecisionSynthesis MCP Server",
        "command": [sys.executable, "mcp_servers/decision_synthesis_server.py"],
        "port": 8003,
    },
    {
        "name": "NotificationSystem MCP Server",
        "command": [sys.executable, "mcp_servers/notification_server.py"],
        "port": 8004,
    },
    {
        "name": "FastAPI Backend",
        "command": [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        "port": 8000,
    },
    {
        "name": "Streamlit UI",
        "command": ["streamlit", "run", "ui/streamlit_app.py", "--server.port", "8501"],
        "port": 8501,
    },
]

processes = []


def start_services():
    """Start all services."""
    print("\n" + "=" * 60)
    print("🚀 Starting Loan Application System Services")
    print("=" * 60 + "\n")

    for service in services:
        print(f"Starting {service['name']}...")
        try:
            process = subprocess.Popen(
                service["command"],
                cwd=os.path.dirname(os.path.abspath(__file__)) + "/..",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            processes.append({"service": service, "process": process})
            print(f"✅ {service['name']} started (PID: {process.pid})")
        except Exception as e:
            print(f"❌ Error starting {service['name']}: {str(e)}")
        time.sleep(2)

    print("\n" + "=" * 60)
    print("📊 Service Status")
    print("=" * 60)
    print(f"🟢 ApplicantDB MCP Server: http://localhost:8001")
    print(f"🟢 RiskRulesDB MCP Server: http://localhost:8002")
    print(f"🟢 DecisionSynthesis MCP Server: http://localhost:8003")
    print(f"🟢 NotificationSystem MCP Server: http://localhost:8004")
    print(f"🟢 FastAPI Backend: http://localhost:8000")
    print(f"🟢 Streamlit UI: http://localhost:8501")
    print("=" * 60 + "\n")

    print("📚 Quick Links:")
    print("  - API Documentation: http://localhost:8000/docs")
    print("  - Health Check: http://localhost:8000/health")
    print("  - Streamlit UI: http://localhost:8501")
    print("\n💡 Press Ctrl+C to stop all services\n")


def stop_services():
    """Stop all services."""
    print("\n\n" + "=" * 60)
    print("🛑 Stopping all services...")
    print("=" * 60)

    for item in processes:
        try:
            item["process"].terminate()
            print(f"✅ Stopped {item['service']['name']}")
        except Exception as e:
            print(f"⚠️  Error stopping {item['service']['name']}: {str(e)}")

    for item in processes:
        try:
            item["process"].wait(timeout=5)
        except subprocess.TimeoutExpired:
            item["process"].kill()

    print("\n✅ All services stopped\n")


def main():
    """Main entry point."""
    try:
        start_services()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        stop_services()
    except Exception as e:
        print(f"Error: {str(e)}")
        stop_services()
        sys.exit(1)


if __name__ == "__main__":
    main()
