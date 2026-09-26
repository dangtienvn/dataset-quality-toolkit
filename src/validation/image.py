from __future__ import annotations

from typing import Any, Dict
from PIL import Image
from ingestion.base import StandardDataset
from validation.base import Severity, ValidationResult


class ImageValidator:
    """Validator for Image file integrity, dimensions, and color space."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_aspect_ratio = self.config.get("max_aspect_ratio", 10.0)
        self.min_aspect_ratio = self.config.get("min_aspect_ratio", 0.1)
        self.min_resolution = self.config.get("min_resolution", (10, 10))

    def validate(self, dataset: StandardDataset) -> ValidationResult:
        result = ValidationResult(validator_name="ImageValidator")
        result.total_checked = dataset.total_images

        for item in dataset.items:
            img = item.image
            if not img.path or not img.path.exists():
                # Already caught in metadata validator, skip reading
                continue

            try:
                with Image.open(img.path) as im:
                    im.verify()

                # Re-open for mode/size check after verify
                with Image.open(img.path) as im:
                    w, h = im.size
                    mode = im.mode

                    # Check zero/tiny dimensions
                    if w <= 0 or h <= 0:
                        result.add_issue(
                            severity=Severity.ERROR,
                            issue_type="zero_dimension_image",
                            message=f"Image has invalid dimensions: {w}x{h}",
                            image_id=img.id,
                        )
                    elif w < self.min_resolution[0] or h < self.min_resolution[1]:
                        result.add_issue(
                            severity=Severity.WARNING,
                            issue_type="tiny_image",
                            message=f"Image resolution {w}x{h} below minimum threshold {self.min_resolution}.",
                            image_id=img.id,
                        )

                    # Check metadata mismatch
                    if img.width > 0 and img.height > 0:
                        if img.width != w or img.height != h:
                            result.add_issue(
                                severity=Severity.WARNING,
                                issue_type="dimension_mismatch",
                                message=f"Header dimension ({img.width}x{img.height}) mismatch with actual image ({w}x{h}).",
                                image_id=img.id,
                            )
                            img.width, img.height = w, h

                    # Aspect ratio check
                    if h > 0:
                        ar = w / h
                        if ar > self.max_aspect_ratio or ar < self.min_aspect_ratio:
                            result.add_issue(
                                severity=Severity.WARNING,
                                issue_type="extreme_aspect_ratio",
                                message=f"Image aspect ratio {ar:.2f} is extreme.",
                                image_id=img.id,
                                details={"aspect_ratio": ar},
                            )
            except Exception as e:
                result.add_issue(
                    severity=Severity.ERROR,
                    issue_type="corrupted_image",
                    message=f"Failed to open or verify image: {e}",
                    image_id=img.id,
                    details={"error": str(e)},
                )

        result.passed_count = result.total_checked - result.failed_count
        return result
