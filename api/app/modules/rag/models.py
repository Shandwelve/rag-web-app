from sqlmodel import Field, Relationship

from app.core.models import BaseModel


class Question(BaseModel, table=True):
    question_text: str = Field(nullable=False, index=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    session_id: str | None = Field(nullable=True, index=True)
    context_files: str | None = Field(nullable=True)

    answers: list["Answer"] = Relationship(back_populates="question")


class Answer(BaseModel, table=True):
    answer_text: str = Field(nullable=False)
    question_id: int = Field(foreign_key="questions.id", nullable=False)
    confidence_score: float = Field(nullable=False)
    sources_used: str | None = Field(nullable=True)
    images_used: str | None = Field(nullable=True)
    processing_time_ms: int | None = Field(nullable=True)

    question: Question = Relationship(back_populates="answers")
