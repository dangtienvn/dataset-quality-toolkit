from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Any
from ingestion.base import StandardDataset
from validation.base import Severity, ValidationResult


class MetadataValidator:
    """Validator and extractor for Dataset Metadata and Provenance."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def validate(self, dataset: StandardDataset) -> ValidationResult:
        result = ValidationResult(validator_name="MetadataValidator")
        result.total_checked = dataset.total_images

        format_counts: Dict[str, int] = {}
        total_bytes = 0
        missing_images = 0

        for item in dataset.items:
            img = item.image
            ext = img.path.suffix.lower() if img.path else ".unknown"
            format_counts[ext] = format_counts.get(ext, 0) + 1

            if img.path and img.path.exists():
                file_size = img.path.stat().st_size
                img.file_size_bytes = file_size
                total_bytes += file_size
                # Compute md5 checksum if requested or missing
                if not img.checksum_md5:
                    try:
                        md5 = hashlib.md5(img.path.read_bytes()).hexdigest()
                        img.checksum_md5 = md5
                    except Exception as e:
                        result.add_issue(
                            severity=Severity.WARNING,
                            issue_type="hash_failed",
                            message=f"Could not compute MD5 hash: {e}",
                            image_id=img.id,
                        )
            else:
                missing_images += 1
                result.add_issue(
                    severity=Severity.ERROR,
                    issue_type="missing_image_file",
                    message=f"Image file does not exist at path: {img.path}",
                    image_id=img.id,
                    details={"file_name": img.file_name, "expected_path": str(img.path)},
                )

        result.passed_count = dataset.total_images - missing_images
        dataset.metadata["file_format_counts"] = format_counts
        dataset.metadata["total_size_bytes"] = total_bytes
        dataset.metadata["average_file_size_bytes"] = (
            total_bytes / dataset.total_images if dataset.total_images > 0 else 0
        )

        return result
