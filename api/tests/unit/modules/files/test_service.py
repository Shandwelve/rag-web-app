from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.files.exceptions import UnsupportedFileTypeError
from app.modules.files.models import File
from app.modules.files.repository import FileRepository
from app.modules.files.schema import FileContentResponse, FileType
from app.modules.files.service import FileService
from app.modules.rag.services import VectorStoreManager


@pytest.mark.asyncio
async def test_save_file_new_file(mock_session: MagicMock, mock_file: File, sample_file_content: bytes) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    mock_file_repo.get_by_hash = AsyncMock(return_value=None)
    mock_file_repo.create = AsyncMock(return_value=mock_file)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("aiofiles.open", create=True) as mock_open:
        mock_file_obj = MagicMock()
        mock_file_obj.__aenter__ = AsyncMock(return_value=mock_file_obj)
        mock_file_obj.__aexit__ = AsyncMock()
        mock_file_obj.write = AsyncMock()
        mock_open.return_value = mock_file_obj

        with patch("app.modules.files.service.settings") as mock_settings:
            mock_settings.STORAGE_DIR = Path("/tmp")
            service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
            result = await service.save_file(sample_file_content, "test.pdf", 1)

            assert result == mock_file


@pytest.mark.asyncio
async def test_save_file_existing_file(mock_session: MagicMock, mock_file: File, sample_file_content: bytes) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    mock_file_repo.get_by_hash = AsyncMock(return_value=mock_file)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("app.modules.files.service.settings") as mock_settings:
        mock_settings.STORAGE_DIR = Path("/tmp")
        service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
        result = await service.save_file(sample_file_content, "test.pdf", 1)

        assert result == mock_file


@pytest.mark.asyncio
async def test_save_file_unsupported_type(mock_session: MagicMock, sample_file_content: bytes) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("app.modules.files.service.settings") as mock_settings:
        mock_settings.STORAGE_DIR = Path("/tmp")
        service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
        with pytest.raises(UnsupportedFileTypeError):
            await service.save_file(sample_file_content, "test.txt", 1)


@pytest.mark.asyncio
async def test_get_file(mock_session: MagicMock, mock_file: File) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    mock_file_repo.get_by_id = AsyncMock(return_value=mock_file)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("app.modules.files.service.settings") as mock_settings:
        mock_settings.STORAGE_DIR = Path("/tmp")
        service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
        result = await service.get_file(1, 1)

        assert result == mock_file


@pytest.mark.asyncio
async def test_get_files(mock_session: MagicMock) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    files = [File(id=i, filename=f"file{i}.pdf", original_filename=f"file{i}.pdf", file_path=f"/path/file{i}.pdf", file_size=1024, file_type=FileType.PDF, user_id=1) for i in range(3)]
    mock_file_repo.get_all = AsyncMock(return_value=files)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("app.modules.files.service.settings") as mock_settings:
        mock_settings.STORAGE_DIR = Path("/tmp")
        service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
        result = await service.get_files()

        assert len(result) == 3


@pytest.mark.asyncio
async def test_delete_file_success(mock_session: MagicMock, mock_file: File) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    mock_file_repo.get_by_id = AsyncMock(return_value=mock_file)
    mock_file_repo.delete = AsyncMock(return_value=True)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("app.modules.files.service.settings") as mock_settings:
        mock_settings.STORAGE_DIR = Path("/tmp")
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.unlink") as mock_unlink:
                service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
                result = await service.delete_file(1, 1)

                assert result is True
                mock_unlink.assert_called_once()


@pytest.mark.asyncio
async def test_delete_file_not_found(mock_session: MagicMock) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    mock_file_repo.get_by_id = AsyncMock(return_value=None)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("app.modules.files.service.settings") as mock_settings:
        mock_settings.STORAGE_DIR = Path("/tmp")
        service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
        result = await service.delete_file(999, 1)

        assert result is False


@pytest.mark.asyncio
async def test_get_file_content_success(mock_session: MagicMock, mock_file: File) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    mock_file_repo.get_by_id = AsyncMock(return_value=mock_file)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("app.modules.files.service.settings") as mock_settings:
        mock_settings.STORAGE_DIR = Path("/tmp")
        with patch("pathlib.Path.exists", return_value=True):
            with patch("aiofiles.open", create=True) as mock_open:
                mock_file_obj = MagicMock()
                mock_file_obj.__aenter__ = AsyncMock(return_value=mock_file_obj)
                mock_file_obj.__aexit__ = AsyncMock()
                mock_file_obj.read = AsyncMock(return_value=b"file content")
                mock_open.return_value = mock_file_obj

                service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
                result = await service.get_file_content(1, 1)

                assert isinstance(result, FileContentResponse)
                assert result.content == b"file content"


@pytest.mark.asyncio
async def test_get_file_content_not_found(mock_session: MagicMock) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    mock_file_repo.get_by_id = AsyncMock(return_value=None)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("app.modules.files.service.settings") as mock_settings:
        mock_settings.STORAGE_DIR = Path("/tmp")
        service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
        result = await service.get_file_content(999, 1)

        assert result is None


def test_get_file_type_pdf(mock_session: MagicMock) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("app.modules.files.service.settings") as mock_settings:
        mock_settings.STORAGE_DIR = Path("/tmp")
        service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
        file_type = service._get_file_type("test.pdf")

        assert file_type == FileType.PDF


def test_get_file_type_docx(mock_session: MagicMock) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("app.modules.files.service.settings") as mock_settings:
        mock_settings.STORAGE_DIR = Path("/tmp")
        service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
        file_type = service._get_file_type("test.docx")

        assert file_type == FileType.DOCX


def test_get_file_type_unsupported(mock_session: MagicMock) -> None:
    mock_file_repo = MagicMock(spec=FileRepository)
    mock_vector_store = MagicMock(spec=VectorStoreManager)

    with patch("app.modules.files.service.settings") as mock_settings:
        mock_settings.STORAGE_DIR = Path("/tmp")
        service = FileService(file_repository=mock_file_repo, vector_store=mock_vector_store)
        with pytest.raises(UnsupportedFileTypeError):
            service._get_file_type("test.txt")
