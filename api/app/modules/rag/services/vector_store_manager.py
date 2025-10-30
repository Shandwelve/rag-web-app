from typing import Annotated, Any

import numpy as np
from fastapi import Depends

from app.core.logging import get_logger
from app.modules.rag.models import DocumentChunk
from app.modules.rag.repositories.document_chunk import DocumentChunkRepository

logger = get_logger(__name__)


class VectorStoreManager:
    def __init__(
        self,
        repository: Annotated[DocumentChunkRepository, Depends(DocumentChunkRepository)],
    ) -> None:
        logger.info("Initializing VectorStoreManager with pgvector")
        self._repository = repository

        try:
            logger.debug("Loading embedding model: all-MiniLM-L6-v2")
            try:
                import torch
                from sentence_transformers import SentenceTransformer

                torch.set_default_device("cpu")
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

            except Exception as model_error:
                logger.warning(
                    f"Failed to load model with device specification: {model_error}, trying fallback initialization"
                )

                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer("all-MiniLM-L6-v2", device="meta")
                self.embedding_model = model.to_empty(device="cpu")

            logger.info("Embedding model loaded successfully")

        except Exception as e:
            logger.error(f"Error initializing VectorStoreManager: {str(e)}", exc_info=True)
            raise

    async def add_documents(self, documents: list[dict[str, Any]]) -> None:
        logger.info(f"Adding {len(documents)} documents to vector store")
        try:
            texts = [doc["text"] for doc in documents]
            logger.debug(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.embedding_model.encode(texts).tolist()

            chunk_objects = []
            for doc, embedding in zip(documents, embeddings, strict=True):
                metadata = doc.get("metadata", {})
                chunk = DocumentChunk(
                    text=doc["text"],
                    embedding=embedding,
                    file_id=metadata.get("file_id"),
                    chunk_index=metadata.get("chunk_index", 0),
                    page_number=metadata.get("page_number"),
                    chunk_metadata=metadata,
                )
                chunk_objects.append(chunk)

            await self._repository.create_batch(chunk_objects)
            logger.info(f"Successfully added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}", exc_info=True)
            raise

    async def search(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        logger.info(f"Searching vector store for query: {query[:100]}..., n_results: {n_results}")
        try:
            query_embedding = self.embedding_model.encode([query])[0].tolist()

            chunks = await self._repository.search_by_embedding(query_embedding, n_results)

            search_results = []
            for chunk in chunks:
                embedding_array = np.array(chunk.embedding)
                query_array = np.array(query_embedding)
                cosine_sim = np.dot(embedding_array, query_array) / (
                    np.linalg.norm(embedding_array) * np.linalg.norm(query_array)
                )
                distance = 1.0 - cosine_sim

                if chunk.chunk_metadata:
                    metadata = chunk.chunk_metadata.copy()
                    metadata.setdefault("file_id", chunk.file_id)
                    metadata.setdefault("chunk_index", chunk.chunk_index)
                    metadata.setdefault("page_number", chunk.page_number)
                else:
                    metadata = {
                        "file_id": chunk.file_id,
                        "filename": None,
                        "chunk_index": chunk.chunk_index,
                        "page_number": chunk.page_number,
                    }

                search_results.append(
                    {
                        "text": chunk.text,
                        "metadata": metadata,
                        "distance": float(distance),
                    }
                )

            result_count = len(search_results)
            logger.info(f"Vector search completed. Found {result_count} results")
            distances = [round(r["distance"], 4) for r in search_results[:3]] if search_results else "N/A"
            logger.debug(f"Result distances: {distances}")

            return search_results
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}", exc_info=True)
            raise
