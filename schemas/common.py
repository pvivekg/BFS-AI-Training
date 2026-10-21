from enum import Enum


class EmploymentType(str, Enum):
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"


class Location(str, Enum):
    NEW_YORK = "New York"
    CALIFORNIA = "California"
    TEXAS = "Texas"
    FLORIDA = "Florida"
    ILLINOIS = "Illinois"
    PENNSYLVANIA = "Pennsylvania"
    OHIO = "Ohio"
    GEORGIA = "Georgia"
    NORTH_CAROLINA = "North Carolina"
    OTHER = "Other"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class Decision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REVIEW = "review"


class Status(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
