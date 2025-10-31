from unittest.mock import MagicMock, patch

from app.modules.rag.services.docx_content_manager import DOCXContentManager


def test_partition_document() -> None:
    manager = DOCXContentManager()
    with patch("app.modules.rag.services.docx_content_manager.partition_docx") as mock_partition:
        mock_elements = [MagicMock(category="CompositeElement")]
        mock_partition.return_value = mock_elements

        result = manager._partition_document("/path/to/file.docx")

        assert isinstance(result, list)


def test_get_images_base64() -> None:
    manager = DOCXContentManager()
    elements = []

    with patch("app.modules.rag.services.docx_content_manager.docx.Document") as mock_docx:
        mock_doc = MagicMock()
        mock_rel = MagicMock()
        mock_rel.target_ref = "image"
        mock_image_part = MagicMock()
        mock_image_part.blob = b"image_data"
        mock_rel.target_part = mock_image_part
        mock_doc.part.rels.values.return_value = [mock_rel]
        mock_docx.return_value = mock_doc

        result = manager._get_images_base64("/path/to/file.docx", elements)

        assert isinstance(result, list)


def test_get_images_base64_no_images() -> None:
    manager = DOCXContentManager()
    elements = []

    with patch("app.modules.rag.services.docx_content_manager.docx.Document") as mock_docx:
        mock_doc = MagicMock()
        mock_rel = MagicMock()
        mock_rel.target_ref = "other"
        mock_doc.part.rels.values.return_value = [mock_rel]
        mock_docx.return_value = mock_doc

        result = manager._get_images_base64("/path/to/file.docx", elements)

        assert len(result) == 0
