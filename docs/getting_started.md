# Getting Started with Dataset Quality Toolkit

`dataset-quality-toolkit` is an open-source Python framework designed for computer vision data quality assurance. It helps you validate annotations, detect corrupt images, find duplicate samples, analyze class imbalances, and produce comprehensive quality audit reports.

---

## Installation

Install in editable mode from source:

```bash
pip install -e .
```

Or install dependencies with `uv` / `pip`:

```bash
pip install pydantic pillow numpy pyyaml jinja2 click
```

---

## Quickstart (CLI)

Audit a COCO dataset:

```bash
dataset-quality-toolkit audit \
  --format coco \
  --annotation ./path/to/annotations.json \
  --images ./path/to/images \
  --output ./reports
```

Audit a YOLO dataset:

```bash
dataset-quality-toolkit audit \
  --format yolo \
  --images ./path/to/images \
  --labels ./path/to/labels \
  --classes-txt ./path/to/classes.txt \
  --output ./reports
```

Audit an unannotated image folder:

```bash
dataset-quality-toolkit audit \
  --format image_folder \
  --images ./path/to/images \
  --output ./reports
```

---

## Quickstart (Python API)

```python
from dataset_quality_toolkit.ingestion import COCOParser
from dataset_quality_toolkit import DatasetQualityPipeline

# 1. Initialize Parser
parser = COCOParser(
    annotation_path="annotations.json",
    images_dir="images/"
)

# 2. Run Audit Pipeline
pipeline = DatasetQualityPipeline()
results = pipeline.run_audit(parser=parser, output_dir="reports")

# 3. Access Reports & Dashboard
print(results["cli_summary"])
print("HTML Report:", results["html_report_path"])
```
