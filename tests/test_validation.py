from pathlib import Path
from PIL import Image
import pytest

from ingestion import AnnotationInfo, BBox, DatasetItem, ImageInfo, StandardDataset
from validation import (
    MetadataValidator,
    AnnotationValidator,
    ImageValidator,
    BBoxMaskValidator,
    Severity,
)


def test_metadata_validator(tmp_path):
    img_path = tmp_path / "test.jpg"
    Image.new("RGB", (10, 10)).save(img_path)

    dataset = StandardDataset(
        name="test",
        format="custom",
        items=[
            DatasetItem(
                image=ImageInfo(
                    id="1", file_name="test.jpg", path=img_path, width=10, height=10
                )
            )
        ],
    )

    validator = MetadataValidator()
    result = validator.validate(dataset)
    assert result.passed_count == 1
    assert dataset.items[0].image.checksum_md5 is not None


def test_annotation_validator():
    dataset = StandardDataset(
        name="test",
        format="custom",
        categories={1: "cat"},
        items=[
            DatasetItem(
                image=ImageInfo(id="1", file_name="test.jpg", path=Path("dummy"), width=10, height=10),
                annotations=[
                    AnnotationInfo(id="101", image_id="1", category_id=-1, category_name="unknown")
                ],
            )
        ],
    )

    validator = AnnotationValidator()
    result = validator.validate(dataset)
    assert result.failed_count == 1
    assert result.issues[0].issue_type == "invalid_category_id"


def test_bbox_mask_validator():
    dataset = StandardDataset(
        name="test",
        format="custom",
        items=[
            DatasetItem(
                image=ImageInfo(id="1", file_name="test.jpg", path=Path("dummy"), width=100, height=100),
                annotations=[
                    AnnotationInfo(
                        id="101",
                        image_id="1",
                        category_id=1,
                        category_name="cat",
                        bbox=BBox(xmin=50.0, ymin=50.0, xmax=20.0, ymax=20.0),  # Inverted!
                    ),
                    AnnotationInfo(
                        id="102",
                        image_id="1",
                        category_id=1,
                        category_name="cat",
                        segmentation=[[0, 0, 10]],  # Odd points!
                    ),
                ],
            )
        ],
    )

    validator = BBoxMaskValidator()
    result = validator.validate(dataset)
    assert result.failed_count >= 2
    issue_types = [i.issue_type for i in result.issues]
    assert "invalid_bbox_coordinates" in issue_types
    assert "invalid_polygon_format" in issue_types
