from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.modules.rag.schema import AnswerResponse, QuestionRequest, QuestionStats, QAPairResponse


@pytest.mark.asyncio
async def test_ask_question(authenticated_client: AsyncClient) -> None:
    with patch("app.modules.rag.services.document_service.DocumentService.process_question") as mock_process:
        mock_answer = AnswerResponse(
            answer="Test answer",
            sources=[],
            images=[],
            confidence_score=0.9,
            question_id=1,
        )
        mock_process.return_value = mock_answer
        
        question_data = QuestionRequest(question="What is this?")
        response = await authenticated_client.post("/rag/ask", json=question_data.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "question_id" in data


@pytest.mark.asyncio
async def test_ask_question_unauthorized(client: AsyncClient) -> None:
    question_data = QuestionRequest(question="What is this?")
    response = await client.post("/rag/ask", json=question_data.model_dump())
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ask_voice_question(authenticated_client: AsyncClient) -> None:
    with patch("app.modules.rag.services.document_service.DocumentService.process_audio_question") as mock_process:
        mock_answer = AnswerResponse(
            answer="Test answer",
            sources=[],
            images=[],
            confidence_score=0.9,
            question_id=1,
        )
        mock_process.return_value = mock_answer
        
        files = {"audio_file": ("test.webm", BytesIO(b"fake audio"), "audio/webm")}
        data = {"session_id": "test_session"}
        response = await authenticated_client.post("/rag/ask-voice", files=files, data=data)
        assert response.status_code == 200
        result = response.json()
        assert "answer" in result


@pytest.mark.asyncio
async def test_ask_voice_question_unauthorized(client: AsyncClient) -> None:
    files = {"audio_file": ("test.webm", BytesIO(b"fake audio"), "audio/webm")}
    response = await client.post("/rag/ask-voice", files=files)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_question_history(admin_client: AsyncClient) -> None:
    with patch("app.modules.rag.services.document_service.DocumentService.get_question_history") as mock_get_history:
        mock_get_history.return_value = []
        
        response = await admin_client.get("/rag/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_question_history_unauthorized(authenticated_client: AsyncClient) -> None:
    response = await authenticated_client.get("/rag/history")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_question_history_with_limit(admin_client: AsyncClient) -> None:
    with patch("app.modules.rag.services.document_service.DocumentService.get_question_history") as mock_get_history:
        mock_get_history.return_value = []
        
        response = await admin_client.get("/rag/history?limit=10")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_session_history(admin_client: AsyncClient) -> None:
    with patch("app.modules.rag.services.document_service.DocumentService.get_session_history") as mock_get_session:
        mock_get_session.return_value = []
        
        response = await admin_client.get("/rag/session/test_session_id")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_session_history_unauthorized(authenticated_client: AsyncClient) -> None:
    response = await authenticated_client.get("/rag/session/test_session_id")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_question(admin_client: AsyncClient) -> None:
    with patch("app.modules.rag.services.document_service.DocumentService.delete_question") as mock_delete:
        mock_delete.return_value = True
        
        response = await admin_client.delete("/rag/question/1")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


@pytest.mark.asyncio
async def test_delete_question_not_found(admin_client: AsyncClient) -> None:
    with patch("app.modules.rag.services.document_service.DocumentService.delete_question") as mock_delete:
        mock_delete.return_value = False
        
        response = await admin_client.delete("/rag/question/99999")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_question_unauthorized(authenticated_client: AsyncClient) -> None:
    response = await authenticated_client.delete("/rag/question/1")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_stats(admin_client: AsyncClient) -> None:
    with patch("app.modules.rag.services.document_service.DocumentService.get_user_stats") as mock_get_stats:
        mock_stats = QuestionStats(total_questions=10, total_answers=10, avg_confidence=0.9)
        mock_get_stats.return_value = mock_stats
        
        response = await admin_client.get("/rag/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_questions" in data
        assert "total_answers" in data
        assert "avg_confidence" in data


@pytest.mark.asyncio
async def test_get_user_stats_unauthorized(authenticated_client: AsyncClient) -> None:
    response = await authenticated_client.get("/rag/stats")
    assert response.status_code == 403
