from unstructured.documents.elements import Element
from unstructured.partition.docx import partition_docx

from .base_content_manager import BaseContentManager


class DOCXContentManager(BaseContentManager):
    def _partition_document(self, file_path: str) -> list[Element]:
        return partition_docx(filename=file_path, **self._PARTITION_CONFIG)
