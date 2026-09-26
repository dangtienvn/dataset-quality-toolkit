# Dataset Quality Toolkit

> A toolkit for validating, profiling, and auditing computer vision datasets and annotations.

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![Status Beta](https://img.shields.io/badge/Status-Beta-blue)

---

## Overview

**`dataset-quality-toolkit`** is an end-to-end framework designed to profile, validate, and audit computer vision datasets (COCO, YOLO, Pascal VOC, raw image folders). It detects corrupted image files, broken bounding boxes, category label errors, duplicate image samples, and class imbalance issues, outputting interactive HTML and JSON audit reports.

---

## Workflow & Feature Pipeline

```
Dataset Ingestion
      ↓
Metadata / Provenance
      ↓
Annotation Validation
      ↓
Image Validation
      ↓
BBox / Mask Validation
      ↓
Duplicate Detection
      ↓
Class Distribution
      ↓
Annotation Statistics
      ↓
Quality Report
```

---

## Directory Structure

```
dataset-quality-toolkit/
│
├── src/
│   ├── ingestion/       # COCO, YOLO, Pascal VOC, and Image Folder parsers
│   ├── validation/      # Metadata, annotation, image, and BBox/Mask rules
│   ├── quality/         # Exact (MD5) & Perceptual (dHash) duplicate detectors
│   ├── metrics/         # Class imbalance and annotation scale profiling
│   ├── reporting/       # Interactive HTML, JSON, and CLI report generators
│   ├── pipeline.py      # Main pipeline orchestrator
│   └── cli.py           # Command-line interface
│
├── configs/             # Default validation YAML configuration
├── tests/               # Pytest suite
├── examples/            # Example scripts (quickstart, COCO audit)
├── reports/             # Generated audit report output directory
├── docs/                # Architecture and validation documentation
│
├── README.md
├── pyproject.toml
└── LICENSE
```

---

## Installation

Install in editable mode:

```bash
pip install -e .
```

Dependencies: `pydantic`, `pillow`, `numpy`, `pyyaml`, `jinja2`, `click`.

---

## Quick Usage

### Command Line Interface (CLI)

```bash
# Audit a COCO Dataset
dataset-quality-toolkit audit -f coco -a ./annotations.json -i ./images/ -o ./reports/

# Audit a YOLO Dataset
dataset-quality-toolkit audit -f yolo -i ./images/ -l ./labels/ -o ./reports/

# Audit an Image Directory
dataset-quality-toolkit audit -f image_folder -i ./images/ -o ./reports/
```

### Python API

```python
from ingestion import COCOParser
from pipeline import DatasetQualityPipeline

# 1. Initialize Parser
parser = COCOParser(
    annotation_path="path/to/annotations.json",
    images_dir="path/to/images/"
)

# 2. Run Audit Pipeline
pipeline = DatasetQualityPipeline()
results = pipeline.run_audit(parser=parser, output_dir="reports")

# 3. View Summary
print(results["cli_summary"])
print("HTML Report:", results["html_report_path"])
```

---

## License

[MIT License](LICENSE)
