from __future__ import annotations

from pathlib import Path
import click

from ingestion import COCOParser, YOLOParser, PascalVOCParser, ImageFolderParser
from pipeline import DatasetQualityPipeline


@click.group()
def main():
    """Dataset Quality Toolkit - Validate, profile, and audit CV datasets."""
    pass


@main.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["coco", "yolo", "pascal_voc", "image_folder"], case_sensitive=False),
    required=True,
    help="Dataset format type.",
)
@click.option(
    "--images",
    "-i",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help="Path to images directory.",
)
@click.option(
    "--annotation",
    "-a",
    type=click.Path(exists=True),
    help="Path to COCO annotation JSON file.",
)
@click.option(
    "--labels",
    "-l",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Path to YOLO labels directory.",
)
@click.option(
    "--annotations-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Path to Pascal VOC XML annotations directory.",
)
@click.option(
    "--classes-txt",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to YOLO classes.txt file.",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to custom validation YAML config.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True),
    default="reports",
    help="Output directory for generated reports.",
)
def audit(format, images, annotation, labels, annotations_dir, classes_txt, config, output):
    """Run full quality audit on dataset."""
    format_lower = format.lower()
    parser = None

    if format_lower == "coco":
        if not annotation:
            raise click.UsageError("COCO format requires --annotation / -a pointing to JSON file.")
        parser = COCOParser(annotation_path=annotation, images_dir=images)
    elif format_lower == "yolo":
        if not labels:
            raise click.UsageError("YOLO format requires --labels / -l pointing to labels directory.")
        parser = YOLOParser(images_dir=images, labels_dir=labels, classes_txt=classes_txt)
    elif format_lower == "pascal_voc":
        if not annotations_dir:
            raise click.UsageError("Pascal VOC format requires --annotations-dir pointing to XML directory.")
        parser = PascalVOCParser(images_dir=images, annotations_dir=annotations_dir)
    elif format_lower == "image_folder":
        parser = ImageFolderParser(images_dir=images)

    pipeline = DatasetQualityPipeline(config_path=config)
    click.echo(f"Starting Dataset Audit [{format_lower}]...")
    results = pipeline.run_audit(parser=parser, output_dir=output)

    click.echo(results["cli_summary"])
    if results["html_report_path"]:
        click.echo(f"HTML Report generated: {results['html_report_path']}")
    if results["json_report_path"]:
        click.echo(f"JSON Report generated: {results['json_report_path']}")


if __name__ == "__main__":
    main()
