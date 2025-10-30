from typing import Any

from sqlmodel import Column, Field, Relationship
from sqlalchemy import JSON, ForeignKey
from pgvector.sqlalchemy import Vector

from app.core.models import BaseModel


class Question(BaseModel, table=True):
    __tablename__ = "questions"
    
    question_text: str = Field(nullable=False, index=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    session_id: str | None = Field(nullable=True, index=True)
    context_files: str | None = Field(nullable=True)

    answers: list["Answer"] = Relationship(back_populates="question")


class Answer(BaseModel, table=True):
    __tablename__ = "answers"
    
    answer_text: str = Field(nullable=False)
    question_id: int = Field(foreign_key="questions.id", nullable=False)
    confidence_score: float = Field(nullable=False)
    sources_used: str | None = Field(nullable=True)
    images_used: str | None = Field(nullable=True)
    processing_time_ms: int | None = Field(nullable=True)

    question: Question = Relationship(back_populates="answers")


class DocumentChunk(BaseModel, table=True):
    __tablename__ = "document_chunks"
    
    text: str = Field(nullable=False)
    embedding: Any = Field(
        sa_column=Column(Vector(384), nullable=False),
    )
    file_id: int = Field(
        sa_column=Column(ForeignKey("file.id", ondelete="CASCADE"), nullable=False, index=True),
    )
    chunk_index: int = Field(nullable=False)
    page_number: int | None = Field(nullable=True)
    chunk_metadata: dict | None = Field(default=None, sa_column=Column(JSON))
