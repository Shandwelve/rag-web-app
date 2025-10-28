from abc import ABC, abstractmethod

from unstructured.documents.elements import Element


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
        texts = []
        chunks = self._partition_document(file_path)

        for chunk in chunks:
            if chunk.category == "CompositeElement":
                texts.append(chunk)
        images = self._get_images_base64(chunks)
        return texts, images

    @abstractmethod
    def _partition_document(self, file_path: str) -> list[Element]:
        pass

    def _get_images_base64(self, chunks: list[Element]) -> list[str]:
        images_b64 = []
        for chunk in chunks:
            if chunk.category == "CompositeElement":
                chunk_elements = chunk.metadata.orig_elements
                for element in chunk_elements:
                    if element.category == "Image":
                        images_b64.append(element.metadata.image_base64)
        return images_b64
