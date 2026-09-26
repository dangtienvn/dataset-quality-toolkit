from __future__ import annotations

from typing import Any, Dict
from ingestion.base import StandardDataset
from validation.base import Severity, ValidationResult


class BBoxMaskValidator:
    """Validator for Bounding Box and Segmentation Mask Integrity."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.min_bbox_size = self.config.get("min_bbox_size", 2.0)  # min pixels width/height
        self.strict_out_of_bounds = self.config.get("strict_out_of_bounds", False)

    def validate(self, dataset: StandardDataset) -> ValidationResult:
        result = ValidationResult(validator_name="BBoxMaskValidator")
        result.total_checked = dataset.total_annotations

        for item in dataset.items:
            img = item.image
            w, h = img.width, img.height

            for ann in item.annotations:
                # 1. BBox Validation
                if ann.bbox is not None:
                    bbox = ann.bbox

                    # Inverted coordinates
                    if bbox.xmin >= bbox.xmax or bbox.ymin >= bbox.ymax:
                        result.add_issue(
                            severity=Severity.ERROR,
                            issue_type="invalid_bbox_coordinates",
                            message=f"BBox has invalid inverted coordinates: [{bbox.xmin}, {bbox.ymin}, {bbox.xmax}, {bbox.ymax}]",
                            image_id=img.id,
                            annotation_id=ann.id,
                        )

                    # Tiny BBox
                    elif bbox.width < self.min_bbox_size or bbox.height < self.min_bbox_size:
                        result.add_issue(
                            severity=Severity.WARNING,
                            issue_type="tiny_bbox",
                            message=f"BBox size ({bbox.width:.1f}x{bbox.height:.1f}) is below minimum size threshold.",
                            image_id=img.id,
                            annotation_id=ann.id,
                        )

                    # Out of bounds check (if image dimensions are known)
                    if w > 0 and h > 0:
                        is_oob = (
                            bbox.xmin < 0
                            or bbox.ymin < 0
                            or bbox.xmax > w
                            or bbox.ymax > h
                        )
                        if is_oob:
                            sev = Severity.ERROR if self.strict_out_of_bounds else Severity.WARNING
                            result.add_issue(
                                severity=sev,
                                issue_type="out_of_bounds_bbox",
                                message=f"BBox [{bbox.xmin:.1f}, {bbox.ymin:.1f}, {bbox.xmax:.1f}, {bbox.ymax:.1f}] extends outside image bounds ({w}x{h}).",
                                image_id=img.id,
                                annotation_id=ann.id,
                                details={"image_width": w, "image_height": h},
                            )

                # 2. Segmentation Mask Validation
                if ann.segmentation is not None:
                    for poly_idx, poly in enumerate(ann.segmentation):
                        if len(poly) % 2 != 0:
                            result.add_issue(
                                severity=Severity.ERROR,
                                issue_type="invalid_polygon_format",
                                message=f"Polygon #{poly_idx} has odd number of coordinates ({len(poly)}).",
                                image_id=img.id,
                                annotation_id=ann.id,
                            )
                        elif len(poly) < 6:
                            result.add_issue(
                                severity=Severity.ERROR,
                                issue_type="degenerate_polygon",
                                message=f"Polygon #{poly_idx} has fewer than 3 vertices (coords={len(poly)}).",
                                image_id=img.id,
                                annotation_id=ann.id,
                            )

        result.passed_count = result.total_checked - result.failed_count
        return result
