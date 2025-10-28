from datetime import datetime
from typing import TypedDict

from pydantic import BaseModel


class RAGResult(TypedDict):
    answer_text: str
    sources: list[str]
    images: list[str]
    confidence_score: float


class QuestionRequest(BaseModel):
    question: str
    session_id: str | None = None


class VoiceQuestionRequest(BaseModel):
    session_id: str | None = None


class SourceReference(BaseModel):
    file_id: int
    filename: str
    page_number: int | None = None
    chunk_index: int
    relevance_score: float


class ImageReference(BaseModel):
    image_path: str
    description: str | None = None
    page_number: int | None = None
    file_id: int


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
    images: list[ImageReference] = []
    confidence_score: float
    question_id: int


class QuestionHistory(BaseModel):
    id: int
    question_text: str
    answer_text: str | None
    sources: list[SourceReference]
    created_at: datetime


class DocumentProcessingStatus(BaseModel):
    file_id: int
    status: str
    chunks_created: int
    images_extracted: int
    error_message: str | None = None


class RAGStats(BaseModel):
    total_documents: int
    total_chunks: int
    total_questions: int
    total_images: int
    last_processed: datetime | None = None


class QuestionCreate(BaseModel):
    question_text: str
    user_id: int
    session_id: str | None = None
    context_files: str | None = None


class AnswerCreate(BaseModel):
    answer_text: str
    question_id: int
    confidence_score: float
    sources_used: str | None = None
    images_used: str | None = None
    processing_time_ms: int | None = None


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    user_id: int
    session_id: str | None
    context_files: str | None
    created_at: datetime
    updated_at: datetime


class QAResponse(BaseModel):
    id: int
    answer_text: str
    question_id: int
    confidence_score: float
    sources_used: str | None
    images_used: str | None
    processing_time_ms: str | None
    created_at: datetime
    updated_at: datetime


class QAPairResponse(BaseModel):
    question: QuestionResponse
    answer: QAResponse


class QuestionStats(BaseModel):
    total_questions: int
    total_answers: int
    avg_confidence: float
