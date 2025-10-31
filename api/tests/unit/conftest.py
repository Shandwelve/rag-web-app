from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.auth.models import User
from app.modules.auth.schema import UserRole
from app.modules.files.models import File
from app.modules.files.schema import FileType
from app.modules.rag.models import Answer, DocumentChunk, Image, Question


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.exec = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_user() -> User:
    return User(
        id=1,
        workos_id="workos_123",
        email="test@example.com",
        role=UserRole.USER,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_admin_user() -> User:
    return User(
        id=2,
        workos_id="workos_456",
        email="admin@example.com",
        role=UserRole.ADMIN,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_file() -> File:
    return File(
        id=1,
        filename="test-uuid.pdf",
        original_filename="test.pdf",
        file_path="/path/to/test-uuid.pdf",
        file_size=1024,
        file_type=FileType.PDF,
        user_id=1,
        content_hash="abc123",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_docx_file() -> File:
    return File(
        id=2,
        filename="test-uuid.docx",
        original_filename="test.docx",
        file_path="/path/to/test-uuid.docx",
        file_size=2048,
        file_type=FileType.DOCX,
        user_id=1,
        content_hash="def456",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_question() -> Question:
    return Question(
        id=1,
        question_text="What is the answer?",
        user_id=1,
        session_id="session_123",
        context_files=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_answer() -> Answer:
    return Answer(
        id=1,
        answer_text="The answer is 42",
        question_id=1,
        confidence_score=0.95,
        sources_used='[{"file_id": 1, "chunk_index": 0}]',
        processing_time_ms=100,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_document_chunk() -> DocumentChunk:
    embedding = [0.1] * 384
    return DocumentChunk(
        id=1,
        text="Sample text chunk",
        embedding=embedding,
        file_id=1,
        chunk_index=0,
        page_number=1,
        chunk_metadata={"filename": "test.pdf"},
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_image() -> Image:
    return Image(
        id=1,
        chunk_id=1,
        image_data="base64encodedimage",
        file_id=1,
        page_number=1,
        description="Test image",
        image_index=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_openai_client() -> MagicMock:
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Generated answer"
    mock_response.usage.total_tokens = 100
    client.chat.completions.create.return_value = mock_response
    return client


@pytest.fixture
def mock_openai_audio_client() -> MagicMock:
    client = MagicMock()
    client.audio.transcriptions.create.return_value = "Transcribed text"
    return client


@pytest.fixture
def mock_sentence_transformer() -> MagicMock:
    model = MagicMock()
    model.encode.return_value = [[0.1] * 384]
    return model


@pytest.fixture
def mock_workos_client() -> MagicMock:
    client = MagicMock()
    mock_session = MagicMock()
    mock_auth_response = MagicMock()
    mock_auth_response.authenticated = True
    mock_auth_response.user = MagicMock()
    mock_auth_response.user.id = "workos_123"
    mock_auth_response.user.email = "test@example.com"
    mock_session.authenticate.return_value = mock_auth_response
    mock_session.refresh.return_value = mock_auth_response
    mock_session.get_logout_url.return_value = "https://logout.url"
    client.user_management.load_sealed_session.return_value = mock_session
    client.user_management.get_authorization_url.return_value = "https://auth.url"
    mock_auth_response_with_session = MagicMock()
    mock_auth_response_with_session.sealed_session = "sealed_session_token"
    client.user_management.authenticate_with_code.return_value = mock_auth_response_with_session
    return client


@pytest.fixture
def mock_request() -> MagicMock:
    request = MagicMock()
    request.cookies = {}
    request.base_url = MagicMock()
    request.base_url.__str__ = lambda x: "http://localhost:8000/"
    return request


@pytest.fixture
def mock_upload_file() -> MagicMock:
    file = MagicMock()
    file.filename = "test.pdf"
    file.read = AsyncMock(return_value=b"file content")
    return file


@pytest.fixture
def mock_audio_file() -> MagicMock:
    file = MagicMock()
    file.filename = "test.webm"
    file.read = AsyncMock(return_value=b"audio content")
    return file


@pytest.fixture
def sample_file_content() -> bytes:
    return b"Sample PDF content"


@pytest.fixture
def sample_text() -> str:
    return "This is a sample text for testing"


@pytest.fixture
def sample_texts() -> list[str]:
    return ["Text 1", "Text 2", "Text 3"]


@pytest.fixture
def sample_embedding() -> list[float]:
    return [0.1] * 384


@pytest.fixture
def sample_embeddings() -> list[list[float]]:
    return [[0.1] * 384, [0.2] * 384, [0.3] * 384]
