from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.rag.models import Image
from app.modules.rag.repositories.image import ImageRepository


@pytest.mark.asyncio
async def test_create_batch(mock_session: MagicMock) -> None:
    images = [Image(id=i, chunk_id=1, image_data=f"image{i}", file_id=1, image_index=i) for i in range(3)]
    mock_session.refresh = AsyncMock()

    repo = ImageRepository(session=mock_session)
    result = await repo.create_batch(images)

    assert len(result) == 3
    mock_session.add.assert_called()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_chunk_id(mock_session: MagicMock, mock_image: Image) -> None:
    images = [mock_image]
    mock_result = MagicMock()
    mock_result.all.return_value = images
    mock_session.exec.return_value = mock_result

    repo = ImageRepository(session=mock_session)
    result = await repo.get_by_chunk_id(1)

    assert len(result) == 1
    assert result[0] == mock_image


@pytest.mark.asyncio
async def test_get_by_chunk_ids(mock_session: MagicMock) -> None:
    images = [Image(id=i, chunk_id=1, image_data=f"image{i}", file_id=1, image_index=i) for i in range(3)]
    mock_result = MagicMock()
    mock_result.all.return_value = images
    mock_session.exec.return_value = mock_result

    repo = ImageRepository(session=mock_session)
    result = await repo.get_by_chunk_ids([1, 2])

    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_by_file_id(mock_session: MagicMock) -> None:
    images = [Image(id=i, chunk_id=1, image_data=f"image{i}", file_id=1, image_index=i) for i in range(3)]
    mock_result = MagicMock()
    mock_result.all.return_value = images
    mock_session.exec.return_value = mock_result

    repo = ImageRepository(session=mock_session)
    result = await repo.get_by_file_id(1)

    assert len(result) == 3


@pytest.mark.asyncio
async def test_delete_by_file_id(mock_session: MagicMock) -> None:
    images = [Image(id=i, chunk_id=1, image_data=f"image{i}", file_id=1, image_index=i) for i in range(3)]
    mock_result = MagicMock()
    mock_result.all.return_value = images
    mock_session.exec.return_value = mock_result
    mock_session.delete = AsyncMock()

    repo = ImageRepository(session=mock_session)
    result = await repo.delete_by_file_id(1)

    assert result == 3
    mock_session.commit.assert_called_once()
