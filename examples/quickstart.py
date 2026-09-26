"""Quickstart Example for Dataset Quality Toolkit."""
import sys
from pathlib import Path
from PIL import Image

# Ensure src is in python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingestion import ImageFolderParser
from pipeline import DatasetQualityPipeline


def main():
    # 1. Create a dummy test image folder
    sample_dir = Path(__file__).parent / "sample_data"
    sample_dir.mkdir(exist_ok=True)

    # Create dummy images
    img1 = sample_dir / "cat.jpg"
    img2 = sample_dir / "dog.jpg"

    if not img1.exists():
        Image.new("RGB", (300, 300), color=(255, 0, 0)).save(img1)
    if not img2.exists():
        Image.new("RGB", (400, 300), color=(0, 255, 0)).save(img2)

    print("Created sample dataset at:", sample_dir)

    # 2. Initialize Parser and Pipeline
    parser = ImageFolderParser(images_dir=sample_dir)
    pipeline = DatasetQualityPipeline()

    # 3. Run Audit
    results = pipeline.run_audit(parser=parser, output_dir="reports")

    # 4. Output Summary
    print("\n--- CLI Audit Summary ---")
    print(results["cli_summary"])
    print(f"\nHTML report saved to: {results['html_report_path']}")


if __name__ == "__main__":
    main()
