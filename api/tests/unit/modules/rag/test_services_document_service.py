from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.files.repository import FileRepository
from app.modules.files.schema import FileType
from app.modules.rag.repositories.document_chunk import DocumentChunkRepository
from app.modules.rag.repositories.image import ImageRepository
from app.modules.rag.repositories.qa import QARepository
from app.modules.rag.schema import AnswerResponse, QuestionRequest, QuestionStats
from app.modules.rag.services import DOCXContentManager, PDFContentManager
from app.modules.rag.services.audio_processing_service import AudioProcessingService
from app.modules.rag.services.document_service import DocumentService
from app.modules.rag.services.openai_service import OpenAIService
from app.modules.rag.services.vector_store_manager import VectorStoreManager


@pytest.mark.asyncio
async def test_process_question() -> None:
    mock_pdf_manager = MagicMock(spec=PDFContentManager)
    mock_docx_manager = MagicMock(spec=DOCXContentManager)
    mock_vector_store = MagicMock(spec=VectorStoreManager)
    mock_openai_service = MagicMock(spec=OpenAIService)
    mock_files_repo = MagicMock(spec=FileRepository)
    mock_qa_repo = MagicMock(spec=QARepository)
    mock_chunk_repo = MagicMock(spec=DocumentChunkRepository)
    mock_image_repo = MagicMock(spec=ImageRepository)
    mock_audio_service = MagicMock(spec=AudioProcessingService)

    mock_question = MagicMock()
    mock_question.id = 1
    mock_qa_repo.create_question = AsyncMock(return_value=mock_question)

    mock_answer = MagicMock()
    mock_answer.id = 1
    mock_qa_repo.create_answer = AsyncMock(return_value=mock_answer)

    mock_vector_store.search = AsyncMock(return_value=[
        {"text": "answer", "metadata": {"file_id": 1, "chunk_index": 0}, "distance": 0.1}
    ])
    mock_openai_service.generate_answer.return_value = "Generated answer"
    mock_files_repo.get_all = AsyncMock(return_value=[])
    mock_chunk_repo.chunk_exists = AsyncMock(return_value=True)

    service = DocumentService(
        pdf_manager=mock_pdf_manager,
        docx_manager=mock_docx_manager,
        vector_store=mock_vector_store,
        openai_service=mock_openai_service,
        files_repository=mock_files_repo,
        qa_repository=mock_qa_repo,
        chunk_repository=mock_chunk_repo,
        image_repository=mock_image_repo,
        audio_service=mock_audio_service,
    )

    question = QuestionRequest(question="Test question")
    result = await service.process_question(question, user_id=1)

    assert isinstance(result, AnswerResponse)


@pytest.mark.asyncio
async def test_get_question_history() -> None:
    mock_pdf_manager = MagicMock(spec=PDFContentManager)
    mock_docx_manager = MagicMock(spec=DOCXContentManager)
    mock_vector_store = MagicMock(spec=VectorStoreManager)
    mock_openai_service = MagicMock(spec=OpenAIService)
    mock_files_repo = MagicMock(spec=FileRepository)
    mock_qa_repo = MagicMock(spec=QARepository)
    mock_chunk_repo = MagicMock(spec=DocumentChunkRepository)
    mock_image_repo = MagicMock(spec=ImageRepository)
    mock_audio_service = MagicMock(spec=AudioProcessingService)

    mock_question = MagicMock()
    mock_question.model_dump.return_value = {
        "id": 1,
        "question_text": "Test?",
        "user_id": 1,
        "session_id": "session_123",
        "context_files": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    mock_answer = MagicMock()
    mock_answer.model_dump.return_value = {
        "id": 1,
        "answer_text": "Answer",
        "question_id": 1,
        "confidence_score": 0.9,
        "sources_used": None,
        "processing_time_ms": 100,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    mock_qa_repo.get_qa_pairs = AsyncMock(return_value=[(mock_question, mock_answer)])
    mock_image_repo.get_by_chunk_id = AsyncMock(return_value=[])
    mock_chunk_repo.get_by_file_id_and_chunk_index = AsyncMock(return_value=None)

    service = DocumentService(
        pdf_manager=mock_pdf_manager,
        docx_manager=mock_docx_manager,
        vector_store=mock_vector_store,
        openai_service=mock_openai_service,
        files_repository=mock_files_repo,
        qa_repository=mock_qa_repo,
        chunk_repository=mock_chunk_repo,
        image_repository=mock_image_repo,
        audio_service=mock_audio_service,
    )

    result = await service.get_question_history(limit=50)

    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_session_history() -> None:
    mock_pdf_manager = MagicMock(spec=PDFContentManager)
    mock_docx_manager = MagicMock(spec=DOCXContentManager)
    mock_vector_store = MagicMock(spec=VectorStoreManager)
    mock_openai_service = MagicMock(spec=OpenAIService)
    mock_files_repo = MagicMock(spec=FileRepository)
    mock_qa_repo = MagicMock(spec=QARepository)
    mock_chunk_repo = MagicMock(spec=DocumentChunkRepository)
    mock_image_repo = MagicMock(spec=ImageRepository)
    mock_audio_service = MagicMock(spec=AudioProcessingService)

    mock_question = MagicMock()
    mock_question.id = 1
    mock_question.model_dump.return_value = {
        "id": 1,
        "question_text": "Test?",
        "user_id": 1,
        "session_id": "session_123",
        "context_files": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    mock_answer = MagicMock()
    mock_answer.model_dump.return_value = {
        "id": 1,
        "answer_text": "Answer",
        "question_id": 1,
        "confidence_score": 0.9,
        "sources_used": None,
        "processing_time_ms": 100,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    mock_qa_repo.get_questions_by_session = AsyncMock(return_value=[mock_question])
    mock_qa_repo.get_answers_by_question_id = AsyncMock(return_value=[mock_answer])
    mock_image_repo.get_by_chunk_id = AsyncMock(return_value=[])
    mock_chunk_repo.get_by_file_id_and_chunk_index = AsyncMock(return_value=None)

    service = DocumentService(
        pdf_manager=mock_pdf_manager,
        docx_manager=mock_docx_manager,
        vector_store=mock_vector_store,
        openai_service=mock_openai_service,
        files_repository=mock_files_repo,
        qa_repository=mock_qa_repo,
        chunk_repository=mock_chunk_repo,
        image_repository=mock_image_repo,
        audio_service=mock_audio_service,
    )

    result = await service.get_session_history("session_123")

    assert len(result) == 1


@pytest.mark.asyncio
async def test_delete_question() -> None:
    mock_pdf_manager = MagicMock(spec=PDFContentManager)
    mock_docx_manager = MagicMock(spec=DOCXContentManager)
    mock_vector_store = MagicMock(spec=VectorStoreManager)
    mock_openai_service = MagicMock(spec=OpenAIService)
    mock_files_repo = MagicMock(spec=FileRepository)
    mock_qa_repo = MagicMock(spec=QARepository)
    mock_chunk_repo = MagicMock(spec=DocumentChunkRepository)
    mock_image_repo = MagicMock(spec=ImageRepository)
    mock_audio_service = MagicMock(spec=AudioProcessingService)

    mock_qa_repo.delete_question = AsyncMock(return_value=True)

    service = DocumentService(
        pdf_manager=mock_pdf_manager,
        docx_manager=mock_docx_manager,
        vector_store=mock_vector_store,
        openai_service=mock_openai_service,
        files_repository=mock_files_repo,
        qa_repository=mock_qa_repo,
        chunk_repository=mock_chunk_repo,
        image_repository=mock_image_repo,
        audio_service=mock_audio_service,
    )

    result = await service.delete_question(1)

    assert result is True


@pytest.mark.asyncio
async def test_get_user_stats() -> None:
    mock_pdf_manager = MagicMock(spec=PDFContentManager)
    mock_docx_manager = MagicMock(spec=DOCXContentManager)
    mock_vector_store = MagicMock(spec=VectorStoreManager)
    mock_openai_service = MagicMock(spec=OpenAIService)
    mock_files_repo = MagicMock(spec=FileRepository)
    mock_qa_repo = MagicMock(spec=QARepository)
    mock_chunk_repo = MagicMock(spec=DocumentChunkRepository)
    mock_image_repo = MagicMock(spec=ImageRepository)
    mock_audio_service = MagicMock(spec=AudioProcessingService)

    mock_stats = QuestionStats(total_questions=10, total_answers=10, avg_confidence=0.9)
    mock_qa_repo.get_question_stats = AsyncMock(return_value=mock_stats)

    service = DocumentService(
        pdf_manager=mock_pdf_manager,
        docx_manager=mock_docx_manager,
        vector_store=mock_vector_store,
        openai_service=mock_openai_service,
        files_repository=mock_files_repo,
        qa_repository=mock_qa_repo,
        chunk_repository=mock_chunk_repo,
        image_repository=mock_image_repo,
        audio_service=mock_audio_service,
    )

    result = await service.get_user_stats(user_id=1)

    assert isinstance(result, QuestionStats)


@pytest.mark.asyncio
async def test_process_audio_question(mock_audio_file: MagicMock) -> None:
    mock_pdf_manager = MagicMock(spec=PDFContentManager)
    mock_docx_manager = MagicMock(spec=DOCXContentManager)
    mock_vector_store = MagicMock(spec=VectorStoreManager)
    mock_openai_service = MagicMock(spec=OpenAIService)
    mock_files_repo = MagicMock(spec=FileRepository)
    mock_qa_repo = MagicMock(spec=QARepository)
    mock_chunk_repo = MagicMock(spec=DocumentChunkRepository)
    mock_image_repo = MagicMock(spec=ImageRepository)
    mock_audio_service = MagicMock(spec=AudioProcessingService)

    mock_audio_service.transcribe_with_openai = AsyncMock(return_value=("Transcribed text", {}))
    mock_question = MagicMock()
    mock_question.id = 1
    mock_qa_repo.create_question = AsyncMock(return_value=mock_question)
    mock_answer = MagicMock()
    mock_answer.id = 1
    mock_qa_repo.create_answer = AsyncMock(return_value=mock_answer)
    mock_vector_store.search = AsyncMock(return_value=[
        {"text": "answer", "metadata": {"file_id": 1, "chunk_index": 0}, "distance": 0.1}
    ])
    mock_openai_service.generate_answer.return_value = "Generated answer"
    mock_files_repo.get_all = AsyncMock(return_value=[])
    mock_chunk_repo.chunk_exists = AsyncMock(return_value=True)

    service = DocumentService(
        pdf_manager=mock_pdf_manager,
        docx_manager=mock_docx_manager,
        vector_store=mock_vector_store,
        openai_service=mock_openai_service,
        files_repository=mock_files_repo,
        qa_repository=mock_qa_repo,
        chunk_repository=mock_chunk_repo,
        image_repository=mock_image_repo,
        audio_service=mock_audio_service,
    )

    result = await service.process_audio_question(mock_audio_file, user_id=1)

    assert isinstance(result, AnswerResponse)
