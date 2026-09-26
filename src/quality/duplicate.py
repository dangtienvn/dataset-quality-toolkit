from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Tuple
from PIL import Image
import numpy as np

from ingestion.base import StandardDataset
from validation.base import Severity, ValidationIssue, ValidationResult


class DuplicateDetector:
    """Duplicate and Near-Duplicate Image Detector using MD5 and Perceptual Difference Hashing (dHash)."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        # Max hamming distance threshold for near-duplicates (0 = exact perceptual match, <= 4 = near match)
        self.max_hamming_distance = self.config.get("max_hamming_distance", 2)

    def _compute_dhash(self, img_path) -> int:
        """Compute 64-bit Difference Hash (dHash) of an image using PIL & numpy."""
        with Image.open(img_path) as im:
            # Convert to 9x8 grayscale
            resized = im.convert("L").resize((9, 8), Image.Resampling.BILINEAR)
            pixels = np.asarray(resized, dtype=np.int32)
            # Difference between adjacent pixels
            diff = pixels[:, 1:] > pixels[:, :-1]
            # Flatten to 64-bit integer
            hash_val = 0
            for bit in diff.flatten():
                hash_val = (hash_val << 1) | int(bit)
            return hash_val

    def detect(self, dataset: StandardDataset) -> ValidationResult:
        result = ValidationResult(validator_name="DuplicateDetector")
        result.total_checked = dataset.total_images

        exact_md5_map: Dict[str, List[str]] = {}
        dhashes: List[Tuple[str, int]] = []  # (image_id, dhash_int)

        for item in dataset.items:
            img = item.image
            if not img.path or not img.path.exists():
                continue

            # 1. Exact MD5 check
            md5_hex = img.checksum_md5
            if not md5_hex:
                try:
                    md5_hex = hashlib.md5(img.path.read_bytes()).hexdigest()
                    img.checksum_md5 = md5_hex
                except Exception:
                    continue

            if md5_hex in exact_md5_map:
                exact_md5_map[md5_hex].append(img.id)
            else:
                exact_md5_map[md5_hex] = [img.id]

            # 2. Perceptual dHash computation
            try:
                dh = self._compute_dhash(img.path)
                dhashes.append((img.id, dh))
            except Exception:
                pass

        # Report exact duplicates
        for md5_hex, img_ids in exact_md5_map.items():
            if len(img_ids) > 1:
                result.add_issue(
                    severity=Severity.WARNING,
                    issue_type="exact_duplicate_images",
                    message=f"Exact duplicate image group found (MD5: {md5_hex}): {img_ids}",
                    image_id=img_ids[0],
                    details={"duplicate_image_ids": img_ids},
                )

        # Report near-duplicates using dHash Hamming distance
        near_duplicate_pairs = []
        n = len(dhashes)
        for i in range(n):
            id_i, hash_i = dhashes[i]
            for j in range(i + 1, n):
                id_j, hash_j = dhashes[j]
                # Hamming distance = bit count of XOR
                hamming_dist = bin(hash_i ^ hash_j).count("1")
                if hamming_dist <= self.max_hamming_distance:
                    # Check if not already in exact MD5 group
                    near_duplicate_pairs.append((id_i, id_j, hamming_dist))

        if near_duplicate_pairs:
            for id1, id2, dist in near_duplicate_pairs:
                result.add_issue(
                    severity=Severity.INFO,
                    issue_type="near_duplicate_images",
                    message=f"Near-duplicate image pair detected ({id1} <-> {id2}, hamming_distance={dist}).",
                    image_id=id1,
                    details={"pair": [id1, id2], "hamming_distance": dist},
                )

        result.passed_count = result.total_checked - len([i for i in result.issues if i.severity == Severity.ERROR])
        return result
