from unittest.mock import MagicMock, patch

import pytest

from app.modules.rag.services.embeddings_service import EmbeddingsService


def test_embed_text() -> None:
    with patch("app.modules.rag.services.embeddings_service.SentenceTransformer") as mock_transformer:
        mock_model = MagicMock()
        mock_embedding_array = MagicMock()
        mock_embedding_array.tolist.return_value = [0.1] * 384
        mock_model.encode.return_value = [mock_embedding_array]
        mock_transformer.return_value = mock_model

        service = EmbeddingsService()
        result = service.embed_text("test text")

        assert len(result) == 384
        assert isinstance(result[0], float)


def test_embed_texts() -> None:
    with patch("app.modules.rag.services.embeddings_service.SentenceTransformer") as mock_transformer:
        mock_model = MagicMock()
        mock_embeddings_array = MagicMock()
        mock_embeddings_array.tolist.return_value = [[0.1] * 384, [0.2] * 384]
        mock_model.encode.return_value = mock_embeddings_array
        mock_transformer.return_value = mock_model

        service = EmbeddingsService()
        result = service.embed_texts(["text1", "text2"])

        assert len(result) == 2
        assert len(result[0]) == 384
