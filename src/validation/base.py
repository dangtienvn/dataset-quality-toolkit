from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ValidationIssue(BaseModel):
    validator: str
    severity: Severity
    issue_type: str
    message: str
    image_id: Optional[str] = None
    annotation_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    validator_name: str
    total_checked: int = 0
    passed_count: int = 0
    failed_count: int = 0
    warning_count: int = 0
    issues: List[ValidationIssue] = Field(default_factory=list)

    def add_issue(
        self,
        severity: Severity,
        issue_type: str,
        message: str,
        image_id: Optional[str] = None,
        annotation_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        issue = ValidationIssue(
            validator=self.validator_name,
            severity=severity,
            issue_type=issue_type,
            message=message,
            image_id=image_id,
            annotation_id=annotation_id,
            details=details or {},
        )
        self.issues.append(issue)
        if severity == Severity.ERROR:
            self.failed_count += 1
        elif severity == Severity.WARNING:
            self.warning_count += 1
