from abc import ABC, abstractmethod

from unstructured.documents.elements import Element
from unstructured.partition.docx import partition_docx
from unstructured.partition.pdf import partition_pdf

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
            chunks = self._partition_document(file_path)
            logger.debug(f"Document partitioned into {len(chunks)} chunks")

            for chunk in chunks:
                if chunk.category == "CompositeElement":
                    texts.append(chunk)
            
            images = self._get_images_base64(chunks)
            logger.info(f"Processing completed. Extracted {len(texts)} text chunks and {len(images)} images")
            return texts, images
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}", exc_info=True)
            raise

    @abstractmethod
    def _partition_document(self, file_path: str) -> list[Element]:
        pass

    def _get_images_base64(self, chunks: list[Element]) -> list[str]:
        logger.debug("Extracting images from document chunks")
        images_b64 = []
        for chunk in chunks:
            if chunk.category == "CompositeElement":
                chunk_elements = chunk.metadata.orig_elements
                for element in chunk_elements:
                    if element.category == "Image":
                        images_b64.append(element.metadata.image_base64)
        logger.debug(f"Extracted {len(images_b64)} images")
        return images_b64


class DOCXContentManager(BaseContentManager):
    def _partition_document(self, file_path: str) -> list[Element]:
        logger.debug(f"Partitioning DOCX file: {file_path}")
        try:
            elements = partition_docx(filename=file_path, **self._PARTITION_CONFIG)
            logger.debug(f"DOCX partitioned into {len(elements)} elements")
            return elements
        except Exception as e:
            logger.error(f"Error partitioning DOCX file {file_path}: {str(e)}", exc_info=True)
            raise


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
