from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml

from ingestion import (
    BaseDatasetParser,
    COCOParser,
    YOLOParser,
    PascalVOCParser,
    ImageFolderParser,
    StandardDataset,
)
from validation import (
    MetadataValidator,
    AnnotationValidator,
    ImageValidator,
    BBoxMaskValidator,
    ValidationResult,
)
from quality import DuplicateDetector
from metrics import ClassDistributionAnalyzer, AnnotationStatsAnalyzer
from reporting import ReportGenerator


class DatasetQualityPipeline:
    """End-to-End Dataset Quality Audit Pipeline."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config: Dict[str, Any] = {}
        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}

    def run_audit(
        self,
        parser: BaseDatasetParser,
        output_dir: Union[str, Path] = "reports",
        generate_html: bool = True,
        generate_json: bool = True,
    ) -> Dict[str, Any]:
        """Execute the full audit pipeline on the dataset."""
        # 1. Dataset Ingestion
        dataset: StandardDataset = parser.parse()

        # 2. Metadata / Provenance Tracking
        metadata_validator = MetadataValidator(self.config.get("metadata", {}))
        res_meta = metadata_validator.validate(dataset)

        # 3. Annotation Validation
        ann_validator = AnnotationValidator(self.config.get("annotation", {}))
        res_ann = ann_validator.validate(dataset)

        # 4. Image Validation
        img_validator = ImageValidator(self.config.get("image", {}))
        res_img = img_validator.validate(dataset)

        # 5. BBox / Mask Validation
        bbox_validator = BBoxMaskValidator(self.config.get("bbox_mask", {}))
        res_bbox = bbox_validator.validate(dataset)

        # 6. Duplicate Detection
        duplicate_detector = DuplicateDetector(self.config.get("duplicate", {}))
        res_dup = duplicate_detector.detect(dataset)

        validation_results = [res_meta, res_ann, res_img, res_bbox, res_dup]

        # 7. Class Distribution Analysis
        class_analyzer = ClassDistributionAnalyzer()
        class_report = class_analyzer.analyze(dataset)

        # 8. Annotation Statistics
        stats_analyzer = AnnotationStatsAnalyzer()
        ann_report = stats_analyzer.analyze(dataset)

        # 9. Quality Report Generation
        reporter = ReportGenerator(output_dir=output_dir)

        html_path = None
        json_path = None
        if generate_html:
            html_path = reporter.generate_html(
                dataset, validation_results, class_report, ann_report
            )

        if generate_json:
            json_path = reporter.generate_json(
                dataset, validation_results, class_report, ann_report
            )

        cli_dashboard = reporter.generate_cli_summary(
            dataset, validation_results, class_report, ann_report
        )

        return {
            "dataset": dataset,
            "validation_results": validation_results,
            "class_report": class_report,
            "annotation_report": ann_report,
            "cli_summary": cli_dashboard,
            "html_report_path": html_path,
            "json_report_path": json_path,
        }
