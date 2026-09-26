"""COCO Dataset Audit Example for Dataset Quality Toolkit."""
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingestion import COCOParser
from pipeline import DatasetQualityPipeline


def main():
    example_dir = Path(__file__).parent / "coco_sample"
    images_dir = example_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    ann_file = example_dir / "annotations.json"

    # Create mock image
    img_path = images_dir / "000001.jpg"
    if not img_path.exists():
        Image.new("RGB", (640, 480), color=(100, 150, 200)).save(img_path)

    # Create mock COCO JSON
    coco_data = {
        "categories": [{"id": 1, "name": "person"}, {"id": 2, "name": "car"}],
        "images": [{"id": 1, "file_name": "000001.jpg", "width": 640, "height": 480}],
        "annotations": [
            {
                "id": 101,
                "image_id": 1,
                "category_id": 1,
                "bbox": [50, 50, 100, 200], # [x, y, w, h]
                "area": 20000,
                "iscrowd": 0,
            }
        ],
    }

    with open(ann_file, "w", encoding="utf-8") as f:
        json.dump(coco_data, f, indent=2)

    # Run Pipeline
    parser = COCOParser(annotation_path=ann_file, images_dir=images_dir)
    pipeline = DatasetQualityPipeline()
    results = pipeline.run_audit(parser=parser, output_dir="reports")

    print(results["cli_summary"])


if __name__ == "__main__":
    main()
