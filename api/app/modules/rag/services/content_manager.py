from abc import ABC, abstractmethod

from unstructured.documents.elements import Element

from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseContentManager(ABC):
    _PARTITION_CONFIG = {
        "strategy": "auto",
        "infer_table_structure": True,
        "extract_images_in_pdf": True,
        "extract_image_block_to_payload": True,
        "chunking_strategy": "by_title",
        "max_characters": 10000,
        "combine_text_under_n_chars": 2000,
        "new_after_n_chars": 6000,
    }

    def process(self, file_path: str) -> tuple[list[Element], list[str]]:
        logger.info(f"Processing document: {file_path}")
        try:
            texts = []
            elements = self._partition_document(file_path)
            logger.debug(f"Document partitioned into {len(elements)} elements")
            for el in elements:
                if el.category == "CompositeElement":
                    texts.append(el)
            images = self._get_images_base64(file_path, elements)

            logger.info(f"Processing completed. Extracted {len(texts)} text chunks and {len(images)} images")
            return texts, images
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}", exc_info=True)
            raise

    @abstractmethod
    def _partition_document(self, file_path: str) -> list[Element]:
        pass

    @abstractmethod
    def _get_images_base64(self, file_path: str, elements: list[Element]) -> list[str]:
        pass
