from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Union
from PIL import Image

from .base import (
    AnnotationInfo,
    BBox,
    BaseDatasetParser,
    DatasetItem,
    ImageInfo,
    StandardDataset,
)


class COCOParser(BaseDatasetParser):
    """Parser for COCO Format Datasets."""

    def __init__(self, annotation_path: Union[str, Path], images_dir: Union[str, Path]):
        self.annotation_path = Path(annotation_path)
        self.images_dir = Path(images_dir)

    def parse(self) -> StandardDataset:
        if not self.annotation_path.exists():
            raise FileNotFoundError(f"COCO annotation file not found: {self.annotation_path}")

        with open(self.annotation_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Build categories map
        categories: Dict[int, str] = {}
        for cat in data.get("categories", []):
            categories[int(cat["id"])] = str(cat["name"])

        # Group annotations by image_id
        img_annotations: Dict[str, List[AnnotationInfo]] = {}
        for ann in data.get("annotations", []):
            img_id = str(ann["image_id"])
            if img_id not in img_annotations:
                img_annotations[img_id] = []

            bbox_obj = None
            if "bbox" in ann and isinstance(ann["bbox"], list) and len(ann["bbox"]) == 4:
                x, y, w, h = ann["bbox"]
                bbox_obj = BBox(xmin=float(x), ymin=float(y), xmax=float(x + w), ymax=float(y + h))

            cat_id = int(ann.get("category_id", -1))
            cat_name = categories.get(cat_id, f"unknown_{cat_id}")

            seg = ann.get("segmentation", None)
            if isinstance(seg, list):
                # Ensure it's list of float lists
                seg_polygons = [
                    [float(coord) for coord in poly]
                    for poly in seg
                    if isinstance(poly, list)
                ]
            else:
                seg_polygons = None

            ann_info = AnnotationInfo(
                id=str(ann.get("id", len(img_annotations[img_id]))),
                image_id=img_id,
                category_id=cat_id,
                category_name=cat_name,
                bbox=bbox_obj,
                segmentation=seg_polygons,
                area=float(ann.get("area", bbox_obj.area if bbox_obj else 0.0)),
                iscrowd=bool(ann.get("iscrowd", False)),
            )
            img_annotations[img_id].append(ann_info)

        # Build dataset items
        items: List[DatasetItem] = []
        for img_dict in data.get("images", []):
            img_id = str(img_dict["id"])
            file_name = img_dict["file_name"]
            img_path = self.images_dir / file_name

            width = int(img_dict.get("width", 0))
            height = int(img_dict.get("height", 0))
            channels = 3
            file_size = 0

            if img_path.exists():
                file_size = img_path.stat().st_size
                if width == 0 or height == 0:
                    try:
                        with Image.open(img_path) as im:
                            width, height = im.size
                            channels = len(im.getbands())
                    except Exception:
                        pass

            image_info = ImageInfo(
                id=img_id,
                file_name=file_name,
                path=img_path,
                width=width,
                height=height,
                channels=channels,
                file_size_bytes=file_size,
            )

            anns = img_annotations.get(img_id, [])
            items.append(DatasetItem(image=image_info, annotations=anns))

        return StandardDataset(
            name=self.annotation_path.stem,
            format="coco",
            categories=categories,
            items=items,
            metadata={"source_file": str(self.annotation_path)},
        )
