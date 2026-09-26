from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml
from PIL import Image

from .base import (
    AnnotationInfo,
    BBox,
    BaseDatasetParser,
    DatasetItem,
    ImageInfo,
    StandardDataset,
)


class YOLOParser(BaseDatasetParser):
    """Parser for YOLO Format Datasets."""

    def __init__(
        self,
        images_dir: Union[str, Path],
        labels_dir: Union[str, Path],
        yaml_path: Optional[Union[str, Path]] = None,
        classes_txt: Optional[Union[str, Path]] = None,
    ):
        self.images_dir = Path(images_dir)
        self.labels_dir = Path(labels_dir)
        self.yaml_path = Path(yaml_path) if yaml_path else None
        self.classes_txt = Path(classes_txt) if classes_txt else None

    def _load_categories(self) -> Dict[int, str]:
        categories: Dict[int, str] = {}
        if self.yaml_path and self.yaml_path.exists():
            with open(self.yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                names = data.get("names", {})
                if isinstance(names, list):
                    for idx, name in enumerate(names):
                        categories[idx] = str(name)
                elif isinstance(names, dict):
                    for idx, name in names.items():
                        categories[int(idx)] = str(name)
        elif self.classes_txt and self.classes_txt.exists():
            with open(self.classes_txt, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    name = line.strip()
                    if name:
                        categories[idx] = name
        return categories

    def parse(self) -> StandardDataset:
        if not self.images_dir.exists():
            raise FileNotFoundError(f"YOLO images directory not found: {self.images_dir}")

        categories = self._load_categories()

        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
        image_files = [
            f for f in self.images_dir.glob("*") if f.suffix.lower() in valid_extensions
        ]

        items: List[DatasetItem] = []

        for idx, img_path in enumerate(image_files):
            img_id = str(idx + 1)
            width, height, channels = 0, 0, 3
            file_size = img_path.stat().st_size

            try:
                with Image.open(img_path) as im:
                    width, height = im.size
                    channels = len(im.getbands())
            except Exception:
                pass

            image_info = ImageInfo(
                id=img_id,
                file_name=img_path.name,
                path=img_path,
                width=width,
                height=height,
                channels=channels,
                file_size_bytes=file_size,
            )

            # Look for matching label text file
            label_file = self.labels_dir / f"{img_path.stem}.txt"
            annotations: List[AnnotationInfo] = []

            if label_file.exists():
                with open(label_file, "r", encoding="utf-8") as f:
                    for ann_idx, line in enumerate(f):
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            cat_id = int(parts[0])
                            x_center = float(parts[1])
                            y_center = float(parts[2])
                            norm_w = float(parts[3])
                            norm_h = float(parts[4])

                            # Convert normalized YOLO bbox to absolute pixel coordinates [xmin, ymin, xmax, ymax]
                            abs_w = norm_w * width
                            abs_h = norm_h * height
                            abs_xc = x_center * width
                            abs_yc = y_center * height

                            xmin = abs_xc - (abs_w / 2.0)
                            ymin = abs_yc - (abs_h / 2.0)
                            xmax = abs_xc + (abs_w / 2.0)
                            ymax = abs_yc + (abs_h / 2.0)

                            bbox = BBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
                            cat_name = categories.get(cat_id, f"class_{cat_id}")

                            annotations.append(
                                AnnotationInfo(
                                    id=f"{img_id}_{ann_idx + 1}",
                                    image_id=img_id,
                                    category_id=cat_id,
                                    category_name=cat_name,
                                    bbox=bbox,
                                    area=bbox.area,
                                )
                            )

            items.append(DatasetItem(image=image_info, annotations=annotations))

        return StandardDataset(
            name=self.images_dir.name,
            format="yolo",
            categories=categories,
            items=items,
            metadata={"images_dir": str(self.images_dir), "labels_dir": str(self.labels_dir)},
        )
