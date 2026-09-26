from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BBox(BaseModel):
    """Bounding Box in absolute pixel coordinates [xmin, ymin, xmax, ymax]."""
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    @property
    def width(self) -> float:
        return self.xmax - self.xmin

    @property
    def height(self) -> float:
        return self.ymax - self.ymin

    @property
    def area(self) -> float:
        return max(0.0, self.width) * max(0.0, self.height)

    @property
    def aspect_ratio(self) -> float:
        if self.height <= 0:
            return 0.0
        return self.width / self.height


class AnnotationInfo(BaseModel):
    """Unified Annotation representation."""
    id: str
    image_id: str
    category_id: int
    category_name: str
    bbox: Optional[BBox] = None
    segmentation: Optional[List[List[float]]] = None  # List of polygon points [[x1, y1, x2, y2, ...]]
    area: Optional[float] = None
    iscrowd: bool = False
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ImageInfo(BaseModel):
    """Unified Image Metadata representation."""
    id: str
    file_name: str
    path: Path
    width: int
    height: int
    channels: int = 3
    file_size_bytes: int = 0
    checksum_md5: Optional[str] = None


class DatasetItem(BaseModel):
    """Single sample containing an image and its annotations."""
    image: ImageInfo
    annotations: List[AnnotationInfo] = Field(default_factory=list)


class StandardDataset(BaseModel):
    """Standardized CV Dataset container."""
    name: str
    format: str  # 'coco', 'yolo', 'pascal_voc', 'image_folder'
    categories: Dict[int, str] = Field(default_factory=dict)
    items: List[DatasetItem] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def total_images(self) -> int:
        return len(self.items)

    @property
    def total_annotations(self) -> int:
        return sum(len(item.annotations) for item in self.items)


class BaseDatasetParser(ABC):
    """Abstract Base Class for Dataset Parsers."""

    @abstractmethod
    def parse(self) -> StandardDataset:
        """Parse dataset into StandardDataset structure."""
        pass
