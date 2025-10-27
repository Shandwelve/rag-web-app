from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class FileType(StrEnum):
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"
    MD = "md"


class FileBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    file_type: FileType
    user_id: int
    content_hash: str | None = None


class FileCreate(FileBase):
    pass


class FileRead(FileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    file_path: str


class FileUpdate(BaseModel):
    content_hash: str | None = None
