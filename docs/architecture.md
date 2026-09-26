# System Architecture

```mermaid
graph TD
    A[Dataset Source: COCO / YOLO / VOC / ImageFolder] --> B[Dataset Ingestion Layer]
    B --> C[StandardDataset Unified Model]
    C --> D[Metadata / Provenance Tracker]
    C --> E[Annotation Validator]
    C --> F[Image Integrity Validator]
    C --> G[BBox / Mask Validator]
    C --> H[Duplicate Image Detector]
    C --> I[Class Distribution Analyzer]
    C --> J[Annotation Stats Analyzer]
    D --> K[Quality Report Generator]
    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K
    K --> L[Interactive HTML Report]
    K --> M[JSON Summary Report]
    K --> N[CLI Terminal Dashboard]
```

## Modular Layer Breakdown

1. **Ingestion Layer (`src/ingestion/`)**: Standardizes diverse dataset formats into unified `StandardDataset`, `DatasetItem`, `ImageInfo`, and `AnnotationInfo` objects.
2. **Validation Layer (`src/validation/`)**: Modular rules executing deterministic quality checks on metadata, images, annotations, and bounding boxes.
3. **Quality Layer (`src/quality/`)**: Perceptual hashing and content-based duplicate search.
4. **Metrics Layer (`src/metrics/`)**: High-level statistical profiling (class imbalance, scale bins).
5. **Reporting Layer (`src/reporting/`)**: Interactive HTML, JSON, and CLI dashboard generation.
