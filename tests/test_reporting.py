from pathlib import Path
import pytest
from ingestion.base import StandardDataset, DatasetItem, ImageInfo, AnnotationInfo, BBox
from validation.base import ValidationResult, ValidationIssue
from metrics.class_distribution import ClassDistributionReport
from metrics.annotation_stats import AnnotationStatsReport
from reporting.report_generator import ReportGenerator


@pytest.fixture
def sample_dataset():
    img1 = ImageInfo(id="1", file_name="img1.jpg", path=Path("img1.jpg"), width=640, height=480)
    ann1 = AnnotationInfo(id="101", image_id="1", category_id=1, category_name="person", bbox=BBox(xmin=10, ymin=10, xmax=60, ymax=60))
    item1 = DatasetItem(image=img1, annotations=[ann1])

    img2 = ImageInfo(id="2", file_name="img2.jpg", path=Path("img2.jpg"), width=800, height=600)
    ann2 = AnnotationInfo(id="102", image_id="2", category_id=2, category_name="car", bbox=BBox(xmin=20, ymin=20, xmax=220, ymax=220))
    item2 = DatasetItem(image=img2, annotations=[ann2])

    return StandardDataset(
        name="test_dataset",
        format="coco",
        categories={1: "person", 2: "car"},
        items=[item1, item2],
    )


@pytest.fixture
def sample_validation_results():
    res1 = ValidationResult(validator_name="Image Integrity", total_checked=2, passed_count=2)
    res2 = ValidationResult(
        validator_name="Annotation Validity",
        total_checked=2,
        passed_count=1,
        failed_count=1,
        issues=[
            ValidationIssue(
                severity="ERROR",
                validator="Annotation Validity",
                issue_type="invalid_bbox",
                message="Bounding box out of bounds",
                image_id="2",
                annotation_id="102",
            )
        ],
    )
    return [res1, res2]


@pytest.fixture
def sample_class_report():
    return ClassDistributionReport(
        class_counts={"person": 1, "car": 1},
        class_percentages={"person": 50.0, "car": 50.0},
        total_annotations=2,
        imbalance_ratio=1.0,
    )


@pytest.fixture
def sample_ann_report():
    return AnnotationStatsReport(
        total_images=2,
        total_annotations=2,
        avg_annotations_per_image=1.0,
        max_annotations_per_image=1,
        min_annotations_per_image=1,
        size_distribution={"small (<32x32)": 0, "medium (32x32 to 96x96)": 1, "large (>96x96)": 1},
    )


def test_generate_html_creates_file_and_contains_components(
    tmp_path, sample_dataset, sample_validation_results, sample_class_report, sample_ann_report
):
    generator = ReportGenerator(output_dir=tmp_path)
    html_file = generator.generate_html(
        sample_dataset, sample_validation_results, sample_class_report, sample_ann_report
    )

    assert html_file.exists()
    content = html_file.read_text(encoding="utf-8")

    # Assert key UI elements and metadata exist in generated HTML
    assert "test_dataset" in content
    assert "COCO" in content
    assert "Quality Index" in content
    assert "Image Integrity" in content
    assert "Annotation Validity" in content
    assert "Bounding box out of bounds" in content
    assert "Class Distribution" in content
    assert "BBox Size Distribution" in content
    assert "classChart" in content
    assert "sizeChart" in content
    assert "filterIssues" in content


def test_generate_json_and_cli_summary(
    tmp_path, sample_dataset, sample_validation_results, sample_class_report, sample_ann_report
):
    generator = ReportGenerator(output_dir=tmp_path)
    json_file = generator.generate_json(
        sample_dataset, sample_validation_results, sample_class_report, sample_ann_report
    )

    assert json_file.exists()

    cli_summary = generator.generate_cli_summary(
        sample_dataset, sample_validation_results, sample_class_report, sample_ann_report
    )
    assert "DATASET QUALITY AUDIT DASHBOARD: TEST_DATASET" in cli_summary
