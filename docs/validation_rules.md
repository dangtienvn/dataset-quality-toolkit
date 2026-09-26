# Validation Rules & Checks

`dataset-quality-toolkit` performs systematic validation across 9 key stages:

---

## 1. Metadata / Provenance Tracking
- **File Format Check**: Analyzes image file extensions and reports file format distribution (.jpg, .png, etc.).
- **Missing File Check**: Verifies that every image referenced in annotation metadata exists on disk.
- **MD5 Checksum & Provenance**: Computes MD5 hash signatures for data integrity verification and tracking.

---

## 2. Annotation Validation
- **Invalid Category IDs**: Detects negative or invalid category IDs.
- **Unlisted Categories**: Flags category IDs present in annotations that are missing from dataset category definitions.
- **Unannotated Images**: Highlights images with zero annotations.

---

## 3. Image Validation
- **Image Corruption Check**: Attempts to open and verify image file bytes using Pillow.
- **Zero Dimension Check**: Flags images with width $\le 0$ or height $\le 0$.
- **Header Mismatch Check**: Detects discrepancies between metadata dimensions and actual image file pixel dimensions.
- **Aspect Ratio Checks**: Flags extreme aspect ratios ($> 10.0$ or $< 0.1$).

---

## 4. BBox / Mask Validation
- **Inverted BBox Coordinates**: Flags boxes where $x_{min} \ge x_{max}$ or $y_{min} \ge y_{max}$.
- **Tiny BBox Check**: Flags bounding boxes with width or height below 2 pixels.
- **Out of Bounds Check**: Identifies bounding boxes extending beyond image boundary boundaries ($x_{max} > width$, $y_{max} > height$, $x_{min} < 0$).
- **Polygon Mask Integrity**: Checks polygon coordinate count (even number, minimum 6 numbers for 3 vertices).

---

## 5. Duplicate Detection
- **Exact Duplicate Detection**: Grouping images with identical MD5 hashes.
- **Perceptual Near-Duplicate Detection**: Difference Hashing (dHash) to detect visually identical or scaled images (Hamming distance $\le 2$).

---

## 6. Class Distribution & Imbalance
- **Class Counts & Percentages**: Frequency distribution per class.
- **Imbalance Ratio**: Calculates $\frac{\text{max\_class\_count}}{\text{min\_class\_count}}$ to identify severe class imbalance.
- **Co-occurrence Matrix**: Tracks classes co-occurring in the same image.

---

## 7. Annotation Statistics
- **Annotation Density**: Mean, min, max annotations per image.
- **COCO Scale Bins**: Small ($< 32^2$), Medium ($32^2 \le area \le 96^2$), Large ($> 96^2$).
- **Aspect Ratio Stats**: Mean, median, and standard deviation of box aspect ratios.
