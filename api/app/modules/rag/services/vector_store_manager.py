from typing import Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class VectorStoreManager:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(name="documents", metadata={"hnsw:space": "cosine"})
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def add_documents(self, documents: list[dict[str, Any]]) -> None:
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedding_model.encode(texts).tolist()
        metadatas = [doc["metadata"] for doc in documents]
        ids = [doc["id"] for doc in documents]

        self.collection.add(embeddings=embeddings, documents=texts, metadatas=metadatas, ids=ids)

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
                strict=True,
            )
        ]

    def delete_documents(self, file_id: int) -> None:
        self.collection.delete(where={"file_id": file_id})
