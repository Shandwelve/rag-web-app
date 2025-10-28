from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


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
    status: str  # "processing", "completed", "failed"
    chunks_created: int
    images_extracted: int
    error_message: Optional[str] = None


class RAGStats(BaseModel):
    total_documents: int
    total_chunks: int
    total_questions: int
    total_images: int
    last_processed: Optional[datetime] = None
