from unstructured.documents.elements import Element
from unstructured.partition.pdf import partition_pdf


class PDFContentManager:
    def process(self, file_path: str):
        texts = []
        chunks = partition_pdf(
            filename=file_path,
            strategy="auto",
            infer_table_structure=True,
            extract_images_in_pdf=True,
            output_dir_path=".",
            extract_image_block_to_payload=True,
            chunking_strategy="by_title",
            max_characters=10000,
            combine_text_under_n_chars=2000,
            new_after_n_chars=6000,
        )

        for chunk in chunks:
            if chunk.category == "CompositeElement":
                texts.append(chunk)
        images = self._get_images_base64(chunks)
        return texts, images

    def _get_images_base64(self, chunks: list[Element]):
        images_b64 = []
        for chunk in chunks:
            if chunk.category == "CompositeElement":
                chunk_elements = chunk.metadata.orig_elements
                for element in chunk_elements:
                    if element.category == "Image":
                        images_b64.append(element.metadata.image_base64)
        return images_b64

