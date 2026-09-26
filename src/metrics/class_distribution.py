from __future__ import annotations

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from ingestion.base import StandardDataset


class ClassDistributionReport(BaseModel):
    class_counts: Dict[str, int] = Field(default_factory=dict)
    class_percentages: Dict[str, float] = Field(default_factory=dict)
    imbalance_ratio: float = 1.0
    most_frequent_class: str = ""
    least_frequent_class: str = ""
    co_occurrence_matrix: Dict[str, Dict[str, int]] = Field(default_factory=dict)


class ClassDistributionAnalyzer:
    """Analyzer for Dataset Class Distribution and Imbalance."""

    def analyze(self, dataset: StandardDataset) -> ClassDistributionReport:
        counts: Dict[str, int] = {}
        co_occur: Dict[str, Dict[str, int]] = {}

        for item in dataset.items:
            present_classes_in_image = set()
            for ann in item.annotations:
                cname = ann.category_name or f"class_{ann.category_id}"
                counts[cname] = counts.get(cname, 0) + 1
                present_classes_in_image.add(cname)

            # Build co-occurrence matrix
            cls_list = sorted(list(present_classes_in_image))
            for c1 in cls_list:
                if c1 not in co_occur:
                    co_occur[c1] = {}
                for c2 in cls_list:
                    co_occur[c1][c2] = co_occur[c1].get(c2, 0) + 1

        total_annotations = sum(counts.values())
        percentages: Dict[str, float] = {
            cname: (cnt / total_annotations * 100.0) if total_annotations > 0 else 0.0
            for cname, cnt in counts.items()
        }

        if counts:
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            most_freq = sorted_counts[0][0]
            least_freq = sorted_counts[-1][0]
            max_c = sorted_counts[0][1]
            min_c = max(1, sorted_counts[-1][1])
            imbalance = max_c / min_c
        else:
            most_freq = ""
            least_freq = ""
            imbalance = 1.0

        return ClassDistributionReport(
            class_counts=counts,
            class_percentages=percentages,
            imbalance_ratio=round(imbalance, 2),
            most_frequent_class=most_freq,
            least_frequent_class=least_freq,
            co_occurrence_matrix=co_occur,
        )
