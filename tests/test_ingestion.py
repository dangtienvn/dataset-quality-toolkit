import json
from pathlib import Path
from PIL import Image
import pytest

from ingestion import (
    BBox,
    COCOParser,
    YOLOParser,
    PascalVOCParser,
    ImageFolderParser,
)


def test_bbox_properties():
    bbox = BBox(xmin=10.0, ymin=20.0, xmax=50.0, ymax=100.0)
    assert bbox.width == 40.0
    assert bbox.height == 80.0
    assert bbox.area == 3200.0
    assert bbox.aspect_ratio == 0.5


def test_coco_parser(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    img_file = images_dir / "test.jpg"
    Image.new("RGB", (100, 100)).save(img_file)

    coco_json = tmp_path / "annotations.json"
    data = {
        "categories": [{"id": 1, "name": "cat"}],
        "images": [{"id": 1, "file_name": "test.jpg", "width": 100, "height": 100}],
        "annotations": [
            {
                "id": 1,
                "image_id": 1,
                "category_id": 1,
                "bbox": [10, 10, 20, 20],
                "area": 400,
            }
        ],
    }
    coco_json.write_text(json.dumps(data))

    parser = COCOParser(annotation_path=coco_json, images_dir=images_dir)
    dataset = parser.parse()

    assert dataset.total_images == 1
    assert dataset.total_annotations == 1
    assert dataset.items[0].annotations[0].category_name == "cat"


def test_yolo_parser(tmp_path):
    images_dir = tmp_path / "images"
    labels_dir = tmp_path / "labels"
    images_dir.mkdir()
    labels_dir.mkdir()

    img_file = images_dir / "sample.jpg"
    Image.new("RGB", (200, 200)).save(img_file)

    label_file = labels_dir / "sample.txt"
    label_file.write_text("0 0.5 0.5 0.2 0.4\n")

    parser = YOLOParser(images_dir=images_dir, labels_dir=labels_dir)
    dataset = parser.parse()

    assert dataset.total_images == 1
    assert dataset.total_annotations == 1
    ann = dataset.items[0].annotations[0]
    assert ann.bbox.width == pytest.approx(40.0)
    assert ann.bbox.height == pytest.approx(80.0)


def test_image_folder_parser(tmp_path):
    cat_dir = tmp_path / "cat"
    cat_dir.mkdir()
    Image.new("RGB", (50, 50)).save(cat_dir / "c1.jpg")

    parser = ImageFolderParser(images_dir=tmp_path)
    dataset = parser.parse()

    assert dataset.total_images == 1
    assert dataset.total_annotations == 1
    assert dataset.items[0].annotations[0].category_name == "cat"
