from PIL import Image
from ingestion import DatasetItem, ImageInfo, StandardDataset
from quality import DuplicateDetector


def test_duplicate_detector(tmp_path):
    img1_path = tmp_path / "img1.jpg"
    img2_path = tmp_path / "img2.jpg"

    # Create identical images
    img = Image.new("RGB", (100, 100), color=(120, 120, 120))
    img.save(img1_path)
    img.save(img2_path)

    dataset = StandardDataset(
        name="test",
        format="custom",
        items=[
            DatasetItem(image=ImageInfo(id="1", file_name="img1.jpg", path=img1_path, width=100, height=100)),
            DatasetItem(image=ImageInfo(id="2", file_name="img2.jpg", path=img2_path, width=100, height=100)),
        ],
    )

    detector = DuplicateDetector()
    result = detector.detect(dataset)

    issue_types = [i.issue_type for i in result.issues]
    assert "exact_duplicate_images" in issue_types
