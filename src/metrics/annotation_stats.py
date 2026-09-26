from __future__ import annotations

from typing import Dict, List, Any
import numpy as np
from pydantic import BaseModel, Field
from ingestion.base import StandardDataset


class AnnotationStatsReport(BaseModel):
    total_images: int = 0
    total_annotations: int = 0
    avg_annotations_per_image: float = 0.0
    max_annotations_per_image: int = 0
    min_annotations_per_image: int = 0
    size_distribution: Dict[str, int] = Field(default_factory=dict)  # 'small', 'medium', 'large'
    aspect_ratio_stats: Dict[str, float] = Field(default_factory=dict)


class AnnotationStatsAnalyzer:
    """Analyzer for Dataset Annotation Density and Size Statistics."""

    def analyze(self, dataset: StandardDataset) -> AnnotationStatsReport:
        img_ann_counts: List[int] = []
        areas: List[float] = []
        aspect_ratios: List[float] = []

        small_count = 0   # area < 32^2 (1024)
        medium_count = 0  # 1024 <= area <= 96^2 (9216)
        large_count = 0   # area > 9216

        for item in dataset.items:
            count = len(item.annotations)
            img_ann_counts.append(count)

            for ann in item.annotations:
                if ann.bbox is not None:
                    area = ann.bbox.area
                    areas.append(area)

                    if area < 1024.0:
                        small_count += 1
                    elif area <= 9216.0:
                        medium_count += 1
                    else:
                        large_count += 1

                    ar = ann.bbox.aspect_ratio
                    if ar > 0:
                        aspect_ratios.append(ar)

        total_imgs = len(dataset.items)
        total_anns = sum(img_ann_counts)
        avg_anns = total_anns / total_imgs if total_imgs > 0 else 0.0
        max_anns = max(img_ann_counts) if img_ann_counts else 0
        min_anns = min(img_ann_counts) if img_ann_counts else 0

        ar_mean = float(np.mean(aspect_ratios)) if aspect_ratios else 0.0
        ar_median = float(np.median(aspect_ratios)) if aspect_ratios else 0.0
        ar_std = float(np.std(aspect_ratios)) if aspect_ratios else 0.0

        return AnnotationStatsReport(
            total_images=total_imgs,
            total_annotations=total_anns,
            avg_annotations_per_image=round(avg_anns, 2),
            max_annotations_per_image=max_anns,
            min_annotations_per_image=min_anns,
            size_distribution={
                "small (<32x32)": small_count,
                "medium (32x32 to 96x96)": medium_count,
                "large (>96x96)": large_count,
            },
            aspect_ratio_stats={
                "mean": round(ar_mean, 2),
                "median": round(ar_median, 2),
                "std": round(ar_std, 2),
            },
        )
