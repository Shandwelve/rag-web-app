from typing import Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class VectorStoreManager:
    def __init__(self) -> None:
        logger.info(f"Initializing VectorStoreManager with ChromaDB path: {settings.CHROMA_PERSIST_DIRECTORY}")
        try:
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=Settings(anonymized_telemetry=False),
            )
            self.collection = self.client.get_or_create_collection(name="documents", metadata={"hnsw:space": "cosine"})
            logger.info("ChromaDB collection 'documents' initialized successfully")
            
            logger.debug("Loading embedding model: all-MiniLM-L6-v2")
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error initializing VectorStoreManager: {str(e)}", exc_info=True)
            raise

    def add_documents(self, documents: list[dict[str, Any]]) -> None:
        logger.info(f"Adding {len(documents)} documents to vector store")
        try:
            texts = [doc["text"] for doc in documents]
            logger.debug(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.embedding_model.encode(texts).tolist()
            metadatas = [doc["metadata"] for doc in documents]
            ids = [doc["id"] for doc in documents]

            self.collection.add(embeddings=embeddings, documents=texts, metadatas=metadatas, ids=ids)
            logger.info(f"Successfully added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}", exc_info=True)
            raise

    def search(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        logger.info(f"Searching vector store for query: {query[:100]}..., n_results: {n_results}")
        try:
            query_embedding = self.embedding_model.encode([query]).tolist()

            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            result_count = len(results["documents"][0]) if results["documents"] else 0
            logger.info(f"Vector search completed. Found {result_count} results")
            logger.debug(f"Result distances: {[round(d, 4) for d in results['distances'][0][:3]] if results.get('distances') and results['distances'][0] else 'N/A'}")

            return [
                {"text": doc, "metadata": meta, "distance": dist}
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                    strict=True,
                )
            ]
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}", exc_info=True)
            raise

    def delete_documents(self, file_id: int) -> None:
        logger.info(f"Deleting documents from vector store for file_id: {file_id}")
        try:
            self.collection.delete(where={"file_id": file_id})
            logger.info(f"Successfully deleted documents for file_id: {file_id}")
        except Exception as e:
            logger.error(f"Error deleting documents for file_id {file_id}: {str(e)}", exc_info=True)
            raise
