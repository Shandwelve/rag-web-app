from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    session_id: Optional[str] = None


class VoiceQuestionRequest(BaseModel):
    audio_data: str


class SourceReference(BaseModel):
    file_id: int
    filename: str
    page_number: Optional[int] = None
    chunk_index: int
    relevance_score: float


class ImageReference(BaseModel):
    image_path: str
    description: Optional[str] = None
    page_number: Optional[int] = None
    file_id: int


class AnswerResponse(BaseModel):
    answer: str
    sources: List[SourceReference]
    images: List[ImageReference] = []
    confidence_score: float
    question_id: int


class QuestionHistory(BaseModel):
    id: int
    question_text: str
    answer_text: Optional[str]
    sources: List[SourceReference]
    created_at: datetime


class DocumentProcessingStatus(BaseModel):
    file_id: int
    status: str
    chunks_created: int
    images_extracted: int
    error_message: Optional[str] = None


class RAGStats(BaseModel):
    total_documents: int
    total_chunks: int
    total_questions: int
    total_images: int
    last_processed: Optional[datetime] = None


class QuestionCreate(BaseModel):
    question_text: str
    user_id: int
    session_id: Optional[str] = None
    context_files: Optional[str] = None


class AnswerCreate(BaseModel):
    answer_text: str
    question_id: int
    confidence_score: float
    sources_used: Optional[str] = None
    images_used: Optional[str] = None
    processing_time_ms: Optional[int] = None


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    user_id: int
    session_id: Optional[str]
    context_files: Optional[str]
    created_at: datetime
    updated_at: datetime


class AnswerResponse(BaseModel):
    id: int
    answer_text: str
    question_id: int
    confidence_score: float
    sources_used: Optional[str]
    images_used: Optional[str]
    processing_time_ms: Optional[int]
    created_at: datetime
    updated_at: datetime


class QAPairResponse(BaseModel):
    question: QuestionResponse
    answer: AnswerResponse
