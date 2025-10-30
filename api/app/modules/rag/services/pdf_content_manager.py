from unstructured.documents.elements import Element
from unstructured.partition.pdf import partition_pdf

from app.core.logging import get_logger
from app.modules.rag.services import BaseContentManager

logger = get_logger(__name__)



class PDFContentManager(BaseContentManager):
    def _partition_document(self, file_path: str) -> list[Element]:
        logger.debug(f"Partitioning PDF file: {file_path}")
        try:
            elements = partition_pdf(filename=file_path, **self._PARTITION_CONFIG)
            logger.debug(f"PDF partitioned into {len(elements)} elements")
            return elements
        except Exception as e:
            logger.error(f"Error partitioning PDF file {file_path}: {str(e)}", exc_info=True)
            raise

    def _get_images_base64(self, file_path: str, elements: list[Element]) -> list[str]:
        logger.debug("Extracting images from PDF document elements")
        images_b64 = []
        for chunk in elements:
            if chunk.category == "CompositeElement":
                chunk_elements = chunk.metadata.orig_elements
                for element in chunk_elements:
                    if element.category == "Image" and getattr(element.metadata, "image_base64", None):
                        images_b64.append(element.metadata.image_base64)

        for element in elements:
            if element.category == "Image" and getattr(element.metadata, "image_base64", None):
                if element.metadata.image_base64 not in images_b64:
                    images_b64.append(element.metadata.image_base64)

        logger.debug(f"Extracted {len(images_b64)} images from PDF elements")
        return list(set(images_b64))
