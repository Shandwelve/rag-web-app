from abc import ABC
from datetime import datetime

from sqlmodel import Field, SQLModel


class BaseModel(ABC, SQLModel):
    id: int = Field(default=None, nullable=False, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
