import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.rag.models import DocumentChunk
from app.modules.rag.repositories.document_chunk import DocumentChunkRepository
from app.modules.rag.services.vector_store_manager import VectorStoreManager


@pytest.mark.asyncio
async def test_add_documents(mock_session: AsyncMock) -> None:
    mock_repo = MagicMock(spec=DocumentChunkRepository)
    mock_repo.create_batch = AsyncMock()
    documents = [{"text": "test", "metadata": {"file_id": 1, "chunk_index": 0}}]

    mock_torch = MagicMock()
    mock_torch.set_default_device = MagicMock()
    mock_model = MagicMock()
    mock_embeddings_array = MagicMock()
    mock_embeddings_array.tolist.return_value = [[0.1] * 384]
    mock_model.encode.return_value = mock_embeddings_array

    with patch.dict(sys.modules, {"torch": mock_torch}):
        with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
            manager = VectorStoreManager(repository=mock_repo)
            await manager.add_documents(documents)
            mock_repo.create_batch.assert_called_once()


@pytest.mark.asyncio
async def test_search(mock_session: AsyncMock, mock_document_chunk: DocumentChunk) -> None:
    mock_repo = MagicMock(spec=DocumentChunkRepository)
    mock_repo.search_by_embedding = AsyncMock(return_value=[mock_document_chunk])

    mock_torch = MagicMock()
    mock_torch.set_default_device = MagicMock()
    mock_model = MagicMock()
    mock_embedding_array = MagicMock()
    mock_embedding_array.tolist.return_value = [0.1] * 384
    mock_model.encode.return_value = [mock_embedding_array]

    with patch.dict(sys.modules, {"torch": mock_torch}):
        with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
            manager = VectorStoreManager(repository=mock_repo)
            results = await manager.search("test query", n_results=5)

            assert len(results) == 1
            assert "text" in results[0]
            assert "metadata" in results[0]
            assert "distance" in results[0]


@pytest.mark.asyncio
async def test_search_empty_results(mock_session: AsyncMock) -> None:
    mock_repo = MagicMock(spec=DocumentChunkRepository)
    mock_repo.search_by_embedding = AsyncMock(return_value=[])

    mock_torch = MagicMock()
    mock_torch.set_default_device = MagicMock()
    mock_model = MagicMock()
    mock_embedding_array = MagicMock()
    mock_embedding_array.tolist.return_value = [0.1] * 384
    mock_model.encode.return_value = [mock_embedding_array]

    with patch.dict(sys.modules, {"torch": mock_torch}):
        with patch("sentence_transformers.SentenceTransformer", return_value=mock_model):
            manager = VectorStoreManager(repository=mock_repo)
            results = await manager.search("test query", n_results=5)

            assert len(results) == 0
