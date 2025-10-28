from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query

from app.modules.auth.middleware import get_current_user
from app.modules.auth.models import User
from app.modules.rag.schema import (
    QuestionRequest,
    VoiceQuestionRequest,
    AnswerResponse,
    QAPairResponse,
)
from app.modules.rag.service import DocumentService

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    rag_service: Annotated[DocumentService, Depends()],
) -> AnswerResponse:
    return await rag_service.process_question(request, current_user.id)


@router.post("/ask-voice", response_model=AnswerResponse)
async def ask_voice_question(
    request: VoiceQuestionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    rag_service: Annotated[DocumentService, Depends()],
) -> AnswerResponse:
    question_request = QuestionRequest(
        question=request.audio_data, session_id=request.session_id
    )
    return await rag_service.process_question(question_request, current_user.id)


@router.get("/history", response_model=List[QAPairResponse])
async def get_question_history(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=50, le=100),
    rag_service: Annotated[DocumentService, Depends()] = Depends(),
):
    qa_pairs = await rag_service.get_question_history(current_user.id, limit)

    return [
        QAPairResponse(question=qa_pair["question"], answer=qa_pair["answer"])
        for qa_pair in qa_pairs
    ]


@router.get("/session/{session_id}", response_model=List[QAPairResponse])
async def get_session_history(
    session_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    rag_service: Annotated[DocumentService, Depends()] = Depends(),
):
    qa_pairs = await rag_service.get_session_history(session_id)

    return [
        QAPairResponse(question=qa_pair["question"], answer=qa_pair["answer"])
        for qa_pair in qa_pairs
    ]


@router.delete("/question/{question_id}")
async def delete_question(
    question_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    rag_service: Annotated[DocumentService, Depends()] = Depends(),
):
    success = await rag_service.delete_question(question_id)

    if not success:
        raise HTTPException(status_code=404, detail="Question not found")

    return {"message": "Question deleted successfully"}


@router.get("/stats", response_model=dict)
async def get_user_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    rag_service: Annotated[DocumentService, Depends()] = Depends(),
):
    return await rag_service.get_user_stats(current_user.id)
