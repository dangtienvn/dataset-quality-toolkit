from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union
from PIL import Image

from .base import (
    AnnotationInfo,
    BaseDatasetParser,
    DatasetItem,
    ImageInfo,
    StandardDataset,
)


class ImageFolderParser(BaseDatasetParser):
    """Parser for unannotated image folders or subfolder-per-class datasets."""

    def __init__(self, images_dir: Union[str, Path]):
        self.images_dir = Path(images_dir)

    def parse(self) -> StandardDataset:
        if not self.images_dir.exists():
            raise FileNotFoundError(f"Images directory not found: {self.images_dir}")

        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
        subfolders = [d for d in self.images_dir.iterdir() if d.is_dir()]

        categories: Dict[int, str] = {}
        category_map: Dict[str, int] = {}
        items: List[DatasetItem] = []

        if subfolders:
            for idx, folder in enumerate(sorted(subfolders)):
                cat_name = folder.name
                categories[idx] = cat_name
                category_map[cat_name] = idx

                for img_idx, img_path in enumerate(folder.glob("*")):
                    if img_path.suffix.lower() in valid_extensions:
                        items.append(self._create_item(img_path, idx, cat_name, len(items) + 1))
        else:
            for img_idx, img_path in enumerate(self.images_dir.glob("*")):
                if img_path.suffix.lower() in valid_extensions:
                    items.append(self._create_item(img_path, None, None, img_idx + 1))

        return StandardDataset(
            name=self.images_dir.name,
            format="image_folder",
            categories=categories,
            items=items,
            metadata={"images_dir": str(self.images_dir)},
        )

    def _create_item(
        self,
        img_path: Path,
        cat_id: Union[int, None],
        cat_name: Union[str, None],
        seq_id: int,
    ) -> DatasetItem:
        img_id = str(seq_id)
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

        annotations: List[AnnotationInfo] = []
        if cat_id is not None and cat_name is not None:
            annotations.append(
                AnnotationInfo(
                    id=f"{img_id}_cls",
                    image_id=img_id,
                    category_id=cat_id,
                    category_name=cat_name,
                )
            )

        return DatasetItem(image=image_info, annotations=annotations)
