from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.rag.models import DocumentChunk
from app.modules.rag.repositories.document_chunk import DocumentChunkRepository


@pytest.mark.asyncio
async def test_create_batch(mock_session: MagicMock) -> None:
    chunks = [DocumentChunk(id=i, text=f"text{i}", embedding=[0.1] * 384, file_id=1, chunk_index=i) for i in range(3)]
    mock_session.refresh = AsyncMock()

    repo = DocumentChunkRepository(session=mock_session)
    result = await repo.create_batch(chunks)

    assert len(result) == 3
    mock_session.add.assert_called()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_search_by_embedding(mock_session: MagicMock, mock_document_chunk: DocumentChunk) -> None:
    chunks = [mock_document_chunk]
    mock_result = MagicMock()
    mock_result.all.return_value = chunks
    mock_session.exec.return_value = mock_result

    repo = DocumentChunkRepository(session=mock_session)
    query_embedding = [0.1] * 384
    result = await repo.search_by_embedding(query_embedding, n_results=5)

    assert len(result) == 1
    assert result[0] == mock_document_chunk


@pytest.mark.asyncio
async def test_get_by_file_id(mock_session: MagicMock) -> None:
    chunks = [DocumentChunk(id=i, text=f"text{i}", embedding=[0.1] * 384, file_id=1, chunk_index=i) for i in range(3)]
    mock_result = MagicMock()
    mock_result.all.return_value = chunks
    mock_session.exec.return_value = mock_result

    repo = DocumentChunkRepository(session=mock_session)
    result = await repo.get_by_file_id(1)

    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_by_file_id_and_chunk_index(mock_session: MagicMock, mock_document_chunk: DocumentChunk) -> None:
    mock_result = MagicMock()
    mock_result.first.return_value = mock_document_chunk
    mock_session.exec.return_value = mock_result

    repo = DocumentChunkRepository(session=mock_session)
    result = await repo.get_by_file_id_and_chunk_index(1, 0)

    assert result == mock_document_chunk


@pytest.mark.asyncio
async def test_chunk_exists_true(mock_session: MagicMock, mock_document_chunk: DocumentChunk) -> None:
    mock_result = MagicMock()
    mock_result.first.return_value = mock_document_chunk
    mock_session.exec.return_value = mock_result

    repo = DocumentChunkRepository(session=mock_session)
    result = await repo.chunk_exists(1)

    assert result is True


@pytest.mark.asyncio
async def test_chunk_exists_false(mock_session: MagicMock) -> None:
    mock_result = MagicMock()
    mock_result.first.return_value = None
    mock_session.exec.return_value = mock_result

    repo = DocumentChunkRepository(session=mock_session)
    result = await repo.chunk_exists(999)

    assert result is False
