from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile

from app.core.schema import MessageResponse
from app.modules.auth.middleware import get_current_admin_user, get_current_user
from app.modules.auth.models import User
from app.modules.rag.schema import (
    AnswerResponse,
    QAPairResponse,
    QuestionRequest,
    QuestionStats,
)
from app.modules.rag.services import DocumentService

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ask")
async def ask_question(
    request: QuestionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(DocumentService)],
) -> AnswerResponse:
    return await document_service.process_question(request, current_user.id)


@router.post("/ask-voice")
async def ask_voice_question(
    audio_file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: Annotated[DocumentService, Depends(DocumentService)],
    session_id: str | None = Form(None),
) -> AnswerResponse:
    return await document_service.process_audio_question(audio_file, current_user.id, session_id)


@router.get("/history")
async def get_question_history(
    current_user: Annotated[User, Depends(get_current_admin_user)],
    document_service: Annotated[DocumentService, Depends(DocumentService)],
    limit: int = Query(default=50, le=100),
) -> list[QAPairResponse]:
    return await document_service.get_question_history(current_user.id, limit)


@router.get("/session/{session_id}", response_model=list[QAPairResponse])
async def get_session_history(
    session_id: str,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    document_service: Annotated[DocumentService, Depends(DocumentService)],
) -> list[QAPairResponse]:
    return await document_service.get_session_history(session_id)


@router.delete("/question/{question_id}")
async def delete_question(
    question_id: int,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    document_service: Annotated[DocumentService, Depends(DocumentService)],
) -> MessageResponse:
    success = await document_service.delete_question(question_id)

    if not success:
        raise HTTPException(status_code=404, detail="Question not found")

    return MessageResponse(message="Question deleted successfully")


@router.get("/stats")
async def get_user_stats(
    current_user: Annotated[User, Depends(get_current_admin_user)],
    document_service: Annotated[DocumentService, Depends(DocumentService)],
) -> QuestionStats:
    return await document_service.get_user_stats(current_user.id)
