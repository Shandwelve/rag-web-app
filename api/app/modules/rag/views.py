from typing import Annotated
from fastapi import APIRouter, Depends

from app.modules.auth.middleware import get_current_user
from app.modules.auth.models import User
from app.modules.rag.schema import (
    QuestionRequest, VoiceQuestionRequest, AnswerResponse, 
)
from app.modules.rag.service import DocumentService

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    rag_service: Annotated[DocumentService, Depends()]
) -> AnswerResponse:
    return await rag_service.process_question(request)


@router.post("/ask-voice", response_model=AnswerResponse)
async def ask_voice_question(
    request: VoiceQuestionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    rag_service: Annotated[DocumentService, Depends()]
) -> AnswerResponse:
    question_request = QuestionRequest(
        question=request.audio_data,
        include_images=request.include_images
    )
    return await rag_service.process_question(question_request)

