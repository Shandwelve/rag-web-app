from sentence_transformers import SentenceTransformer

from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingsService:
    def __init__(self) -> None:
        logger.debug("Loading embedding model: all-MiniLM-L6-v2")
        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}", exc_info=True)
            raise

    def embed_text(self, text: str) -> list[float]:
        logger.debug(f"Generating embedding for text of length: {len(text)}")
        try:
            embedding = self.model.encode([text])[0].tolist()
            logger.debug(f"Embedding generated. Dimension: {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}", exc_info=True)
            raise

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        logger.debug(f"Generating embeddings for {len(texts)} texts")
        try:
            embeddings = self.model.encode(texts).tolist()
            logger.debug(
                f"Embeddings generated. Count: {len(embeddings)}, Dimension: {len(embeddings[0]) if embeddings else 0}"
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}", exc_info=True)
            raise
