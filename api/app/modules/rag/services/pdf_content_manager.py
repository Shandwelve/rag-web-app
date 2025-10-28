from unstructured.documents.elements import Element
from unstructured.partition.pdf import partition_pdf

from .base_content_manager import BaseContentManager


class PDFContentManager(BaseContentManager):
    def _partition_document(self, file_path: str) -> list[Element]:
        return partition_pdf(filename=file_path, **self._PARTITION_CONFIG)
