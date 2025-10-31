import base64

import docx
from unstructured.documents.elements import Element
from unstructured.partition.docx import partition_docx

from app.core.logging import get_logger
from app.modules.rag.services import BaseContentManager

logger = get_logger(__name__)


class DOCXContentManager(BaseContentManager):
    def _partition_document(self, file_path: str) -> list[Element]:
        logger.debug(f"Partitioning DOCX file: {file_path}")
        try:
            config = self._PARTITION_CONFIG.copy()
            config.pop("extract_images_in_pdf", None)
            config.pop("extract_image_block_to_payload", None)

            elements = partition_docx(filename=file_path, **config)
            logger.debug(f"DOCX partitioned into {len(elements)} elements")
            return elements
        except Exception as e:
            logger.error(f"Error partitioning DOCX file {file_path}: {str(e)}", exc_info=True)
            raise

    def _get_images_base64(self, file_path: str, elements: list[Element]) -> list[str]:
        logger.debug("Extracting images from DOCX file path")
        images_b64 = []
        try:
            doc = docx.Document(file_path)

            for rel in doc.part.rels.values():
                if "image" in rel.target_ref:
                    image_part = rel.target_part
                    image_bytes = image_part.blob
                    b64_string = base64.b64encode(image_bytes).decode("utf-8")
                    images_b64.append(b64_string)

        except Exception as e:
            logger.error(
                f"Error extracting images from DOCX {file_path}: {str(e)}",
                exc_info=True,
            )

        logger.debug(f"Extracted {len(images_b64)} images from DOCX")
        return images_b64
