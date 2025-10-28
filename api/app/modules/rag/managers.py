from typing import Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import openai
from unstructured.documents.elements import Element
from unstructured.partition.pdf import partition_pdf

from app.core.config import settings


class VectorStoreManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name="documents", metadata={"hnsw:space": "cosine"}
        )
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def add_documents(self, documents: list[dict[str, Any]]) -> None:
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedding_model.encode(texts).tolist()
        metadatas = [doc["metadata"] for doc in documents]
        ids = [doc["id"] for doc in documents]

        self.collection.add(
            embeddings=embeddings, documents=texts, metadatas=metadatas, ids=ids
        )

    def search(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        query_embedding = self.embedding_model.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        return [
            {"text": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]

    def delete_documents(self, file_id: int) -> None:
        self.collection.delete(where={"file_id": file_id})


class PDFContentManager:
    def process(self, file_path: str):
        texts = []
        chunks = partition_pdf(
            filename=file_path,
            strategy="auto",
            infer_table_structure=True,
            extract_images_in_pdf=True,
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


class EmbeddingsService:
    def __init__(self) -> None:
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_text(self, text: str) -> list[float]:
        return self.model.encode([text])[0].tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts).tolist()


class OpenAIService:
    def __init__(self) -> None:
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_answer(self, question: str, context: str) -> str:
        system_prompt = """You are a helpful assistant that answers questions based on provided context. 
        Provide accurate, detailed answers based on the context. If the context doesn't contain enough information, 
        say so clearly. Be concise but comprehensive."""

        user_prompt = f"""Context: {context}
        
        Question: {question}
        
        Please provide a detailed answer based on the context above."""

        response = self.client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=settings.MAX_TOKENS,
            temperature=0.7,
        )

        return response.choices[0].message.content
