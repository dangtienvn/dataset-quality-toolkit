from __future__ import annotations

import xml.etree.ElementTree as ET
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


class PascalVOCParser(BaseDatasetParser):
    """Parser for Pascal VOC XML Datasets."""

    def __init__(self, images_dir: Union[str, Path], annotations_dir: Union[str, Path]):
        self.images_dir = Path(images_dir)
        self.annotations_dir = Path(annotations_dir)

    def parse(self) -> StandardDataset:
        if not self.images_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {self.images_dir}")

        categories: Dict[int, str] = {}
        category_name_to_id: Dict[str, int] = {}

        xml_files = list(self.annotations_dir.glob("*.xml")) if self.annotations_dir.exists() else []

        items: List[DatasetItem] = []

        for idx, xml_file in enumerate(xml_files):
            img_id = str(idx + 1)
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
            except Exception:
                continue

            file_name = root.findtext("filename", f"{xml_file.stem}.jpg")
            img_path = self.images_dir / file_name
            if not img_path.exists():
                # fallback try stem matching
                possible = list(self.images_dir.glob(f"{xml_file.stem}.*"))
                if possible:
                    img_path = possible[0]

            width, height, channels = 0, 0, 3
            size_elem = root.find("size")
            if size_elem is not None:
                width = int(size_elem.findtext("width", "0"))
                height = int(size_elem.findtext("height", "0"))
                channels = int(size_elem.findtext("depth", "3"))

            if (width == 0 or height == 0) and img_path.exists():
                try:
                    with Image.open(img_path) as im:
                        width, height = im.size
                        channels = len(im.getbands())
                except Exception:
                    pass

            file_size = img_path.stat().st_size if img_path.exists() else 0

            image_info = ImageInfo(
                id=img_id,
                file_name=img_path.name if img_path.exists() else file_name,
                path=img_path,
                width=width,
                height=height,
                channels=channels,
                file_size_bytes=file_size,
            )

            annotations: List[AnnotationInfo] = []
            for ann_idx, obj in enumerate(root.findall("object")):
                cat_name = obj.findtext("name", "unknown")
                if cat_name not in category_name_to_id:
                    new_id = len(category_name_to_id)
                    category_name_to_id[cat_name] = new_id
                    categories[new_id] = cat_name

                cat_id = category_name_to_id[cat_name]

                bndbox = obj.find("bndbox")
                bbox = None
                if bndbox is not None:
                    xmin = float(bndbox.findtext("xmin", "0"))
                    ymin = float(bndbox.findtext("ymin", "0"))
                    xmax = float(bndbox.findtext("xmax", "0"))
                    ymax = float(bndbox.findtext("ymax", "0"))
                    bbox = BBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)

                difficult = bool(int(obj.findtext("difficult", "0")))

                annotations.append(
                    AnnotationInfo(
                        id=f"{img_id}_{ann_idx + 1}",
                        image_id=img_id,
                        category_id=cat_id,
                        category_name=cat_name,
                        bbox=bbox,
                        area=bbox.area if bbox else 0.0,
                        attributes={"difficult": difficult},
                    )
                )

            items.append(DatasetItem(image=image_info, annotations=annotations))

        return StandardDataset(
            name=self.images_dir.name,
            format="pascal_voc",
            categories=categories,
            items=items,
            metadata={"images_dir": str(self.images_dir), "annotations_dir": str(self.annotations_dir)},
        )
