"""Database abstraction layer for persistent storage."""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from abc import ABC, abstractmethod

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./loan_applications.db"
)


class IApplicationRepository(ABC):
    """Interface for application storage."""

    @abstractmethod
    def save_application(self, app_id: str, app_data: Dict[str, Any]) -> bool:
        """Save application."""
        pass

    @abstractmethod
    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve application."""
        pass

    @abstractmethod
    def get_all_applications(self) -> List[Dict[str, Any]]:
        """Get all applications."""
        pass

    @abstractmethod
    def update_application(self, app_id: str, app_data: Dict[str, Any]) -> bool:
        """Update application."""
        pass

    @abstractmethod
    def delete_application(self, app_id: str) -> bool:
        """Delete application."""
        pass


class SQLiteApplicationRepository(IApplicationRepository):
    """SQLite implementation of application repository."""

    def __init__(self, db_path: str = "loan_applications.db"):
        """Initialize SQLite repository.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.storage = {}  # For MVP, using in-memory dict with file persistence
        self._init_db()

    def _init_db(self):
        """Initialize database (create tables if needed)."""
        # For MVP with SQLite in-memory, we'll use JSON file storage
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    self.storage = json.load(f)
            except Exception as e:
                print(f"Error loading database: {e}")
                self.storage = {}

    def _persist(self):
        """Persist storage to file."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.storage, f, indent=2, default=str)
        except Exception as e:
            print(f"Error persisting database: {e}")

    def save_application(self, app_id: str, app_data: Dict[str, Any]) -> bool:
        """Save application to database.

        Args:
            app_id: Application ID
            app_data: Application data

        Returns:
            True if saved successfully
        """
        try:
            self.storage[app_id] = {
                "id": app_id,
                "data": app_data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            self._persist()
            return True
        except Exception as e:
            print(f"Error saving application: {e}")
            return False

    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve application from database.

        Args:
            app_id: Application ID

        Returns:
            Application data or None if not found
        """
        return self.storage.get(app_id)

    def get_all_applications(self) -> List[Dict[str, Any]]:
        """Get all applications from database.

        Returns:
            List of all applications
        """
        return list(self.storage.values())

    def update_application(self, app_id: str, app_data: Dict[str, Any]) -> bool:
        """Update application in database.

        Args:
            app_id: Application ID
            app_data: Updated application data

        Returns:
            True if updated successfully
        """
        try:
            if app_id not in self.storage:
                return False

            self.storage[app_id]["data"] = app_data
            self.storage[app_id]["updated_at"] = datetime.utcnow().isoformat()
            self._persist()
            return True
        except Exception as e:
            print(f"Error updating application: {e}")
            return False

    def delete_application(self, app_id: str) -> bool:
        """Delete application from database.

        Args:
            app_id: Application ID

        Returns:
            True if deleted successfully
        """
        try:
            if app_id in self.storage:
                del self.storage[app_id]
                self._persist()
                return True
            return False
        except Exception as e:
            print(f"Error deleting application: {e}")
            return False


class AuditLogRepository:
    """Repository for audit logging."""

    def __init__(self, db_path: str = "audit_log.db"):
        """Initialize audit log repository.

        Args:
            db_path: Path to audit log file
        """
        self.db_path = db_path
        self.logs: List[Dict[str, Any]] = []
        self._init_db()

    def _init_db(self):
        """Initialize audit log database."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    self.logs = json.load(f)
            except Exception as e:
                print(f"Error loading audit log: {e}")
                self.logs = []

    def _persist(self):
        """Persist audit logs to file."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.logs, f, indent=2, default=str)
        except Exception as e:
            print(f"Error persisting audit log: {e}")

    def log_action(
        self,
        case_id: str,
        applicant_id: str,
        action_type: str,
        details: str,
        actor: str = "system"
    ) -> bool:
        """Log an action.

        Args:
            case_id: Case ID
            applicant_id: Applicant ID
            action_type: Type of action
            details: Action details
            actor: Who performed the action

        Returns:
            True if logged successfully
        """
        try:
            log_entry = {
                "id": len(self.logs) + 1,
                "case_id": case_id,
                "applicant_id": applicant_id,
                "action_type": action_type,
                "details": details,
                "actor": actor,
                "timestamp": datetime.utcnow().isoformat(),
            }
            self.logs.append(log_entry)
            self._persist()
            return True
        except Exception as e:
            print(f"Error logging action: {e}")
            return False

    def get_case_logs(self, case_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a case.

        Args:
            case_id: Case ID

        Returns:
            List of log entries for the case
        """
        return [log for log in self.logs if log["case_id"] == case_id]

    def get_all_logs(self) -> List[Dict[str, Any]]:
        """Get all audit logs.

        Returns:
            List of all log entries
        """
        return self.logs


# Global repository instances
app_repository = SQLiteApplicationRepository("loan_applications.db")
audit_repository = AuditLogRepository("audit_log.db")


def get_app_repository() -> IApplicationRepository:
    """Get application repository.

    Returns:
        Application repository instance
    """
    return app_repository


def get_audit_repository() -> AuditLogRepository:
    """Get audit log repository.

    Returns:
        Audit log repository instance
    """
    return audit_repository


# Test database
if __name__ == "__main__":
    repo = SQLiteApplicationRepository()

    # Test save
    test_app = {
        "applicant_id": "APP001",
        "age": 35,
        "income": 75000,
        "status": "completed"
    }
    repo.save_application("app_001", test_app)
    print("Saved application")

    # Test retrieve
    retrieved = repo.get_application("app_001")
    print(f"Retrieved: {retrieved}")

    # Test update
    test_app["status"] = "approved"
    repo.update_application("app_001", test_app)
    print("Updated application")

    # Test get all
    all_apps = repo.get_all_applications()
    print(f"Total applications: {len(all_apps)}")

    # Test audit log
    audit_repo = AuditLogRepository()
    audit_repo.log_action("CASE_001", "APP001", "decision_made", "Approved")
    logs = audit_repo.get_case_logs("CASE_001")
    print(f"Audit logs: {logs}")
