from __future__ import annotations

from typing import Any, Dict
from ingestion.base import StandardDataset
from validation.base import Severity, ValidationResult


class AnnotationValidator:
    """Validator for Annotation Integrity and Categories."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def validate(self, dataset: StandardDataset) -> ValidationResult:
        result = ValidationResult(validator_name="AnnotationValidator")
        result.total_checked = dataset.total_annotations

        known_categories = dataset.categories

        for item in dataset.items:
            img = item.image
            if not item.annotations and self.config.get("warn_empty_image", True):
                result.add_issue(
                    severity=Severity.WARNING,
                    issue_type="unannotated_image",
                    message=f"Image {img.file_name} has no annotations.",
                    image_id=img.id,
                )

            for ann in item.annotations:
                # Check category ID
                if ann.category_id < 0:
                    result.add_issue(
                        severity=Severity.ERROR,
                        issue_type="invalid_category_id",
                        message=f"Annotation {ann.id} has negative category_id ({ann.category_id}).",
                        image_id=img.id,
                        annotation_id=ann.id,
                    )

                if known_categories and ann.category_id not in known_categories:
                    result.add_issue(
                        severity=Severity.WARNING,
                        issue_type="unknown_category_id",
                        message=f"Annotation category_id {ann.category_id} not listed in dataset categories.",
                        image_id=img.id,
                        annotation_id=ann.id,
                        details={"category_name": ann.category_name},
                    )

        result.passed_count = result.total_checked - result.failed_count
        return result
