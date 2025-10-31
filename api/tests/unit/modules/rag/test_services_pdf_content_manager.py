from unittest.mock import MagicMock, patch

import pytest

from app.modules.rag.services.pdf_content_manager import PDFContentManager


def test_partition_document() -> None:
    manager = PDFContentManager()
    with patch("app.modules.rag.services.pdf_content_manager.partition_pdf") as mock_partition:
        mock_elements = [MagicMock(category="CompositeElement")]
        mock_partition.return_value = mock_elements

        result = manager._partition_document("/path/to/file.pdf")

        assert isinstance(result, list)


def test_get_images_base64() -> None:
    manager = PDFContentManager()
    mock_element = MagicMock()
    mock_element.category = "CompositeElement"
    mock_element.metadata.orig_elements = []
    elements = [mock_element]

    result = manager._get_images_base64("/path/to/file.pdf", elements)

    assert isinstance(result, list)


def test_get_images_base64_with_image_elements() -> None:
    manager = PDFContentManager()
    mock_image_element = MagicMock()
    mock_image_element.category = "Image"
    mock_image_element.metadata.image_base64 = "base64image"

    mock_composite = MagicMock()
    mock_composite.category = "CompositeElement"
    mock_composite.metadata.orig_elements = []

    elements = [mock_composite, mock_image_element]

    result = manager._get_images_base64("/path/to/file.pdf", elements)

    assert len(result) == 1
    assert result[0] == "base64image"
