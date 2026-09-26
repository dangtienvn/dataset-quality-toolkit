from pathlib import Path
from click.testing import CliRunner
from PIL import Image

from cli import main
from ingestion import ImageFolderParser
from pipeline import DatasetQualityPipeline


def test_full_pipeline(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    Image.new("RGB", (100, 100)).save(images_dir / "sample.jpg")

    parser = ImageFolderParser(images_dir=images_dir)
    pipeline = DatasetQualityPipeline()
    reports_dir = tmp_path / "reports"

    results = pipeline.run_audit(parser=parser, output_dir=reports_dir)

    assert results["html_report_path"].exists()
    assert results["json_report_path"].exists()
    assert "DATASET QUALITY AUDIT DASHBOARD" in results["cli_summary"]


def test_cli_audit_image_folder(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    Image.new("RGB", (50, 50)).save(images_dir / "test.jpg")

    runner = CliRunner()
    result = runner.invoke(
        main,
        ["audit", "--format", "image_folder", "--images", str(images_dir), "--output", str(tmp_path / "out")],
    )

    assert result.exit_code == 0
    assert "Starting Dataset Audit" in result.output
    assert "HTML Report generated" in result.output
