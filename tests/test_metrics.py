from pathlib import Path
from ingestion import AnnotationInfo, BBox, DatasetItem, ImageInfo, StandardDataset
from metrics import ClassDistributionAnalyzer, AnnotationStatsAnalyzer


def test_metrics_analyzers():
    dataset = StandardDataset(
        name="test",
        format="custom",
        categories={1: "cat", 2: "dog"},
        items=[
            DatasetItem(
                image=ImageInfo(id="1", file_name="img1.jpg", path=Path("d"), width=100, height=100),
                annotations=[
                    AnnotationInfo(id="101", image_id="1", category_id=1, category_name="cat", bbox=BBox(xmin=0, ymin=0, xmax=10, ymax=10)), # area 100 small
                    AnnotationInfo(id="102", image_id="1", category_id=1, category_name="cat", bbox=BBox(xmin=0, ymin=0, xmax=10, ymax=10)),
                ],
            ),
            DatasetItem(
                image=ImageInfo(id="2", file_name="img2.jpg", path=Path("d"), width=100, height=100),
                annotations=[
                    AnnotationInfo(id="103", image_id="2", category_id=2, category_name="dog", bbox=BBox(xmin=0, ymin=0, xmax=100, ymax=100)), # area 10000 large
                ],
            ),
        ],
    )

    class_analyzer = ClassDistributionAnalyzer()
    class_report = class_analyzer.analyze(dataset)
    assert class_report.class_counts["cat"] == 2
    assert class_report.class_counts["dog"] == 1
    assert class_report.imbalance_ratio == 2.0

    stats_analyzer = AnnotationStatsAnalyzer()
    stats_report = stats_analyzer.analyze(dataset)
    assert stats_report.total_annotations == 3
    assert stats_report.size_distribution["small (<32x32)"] == 2
    assert stats_report.size_distribution["large (>96x96)"] == 1
