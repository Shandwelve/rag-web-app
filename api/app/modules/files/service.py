import hashlib
import os
from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import Depends

from app.modules.files.models import File, FileType
from app.modules.files.repository import FileRepository


class FileService:
    def __init__(self, file_repository: Annotated[FileRepository, Depends()]) -> None:
        self.file_repository = file_repository
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

    async def save_file(
        self, file_content: bytes, filename: str, user_id: int
    ) -> File:
        file_type = self._get_file_type(filename)
        content_hash = hashlib.sha256(file_content).hexdigest()
        
        existing_file = await self.file_repository.get_by_hash(content_hash, user_id)
        if existing_file:
            return existing_file

        file_path = self.upload_dir / f"{user_id}_{filename}"
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)

        file_record = File(
            filename=filename,
            original_filename=filename,
            file_path=str(file_path),
            file_size=len(file_content),
            file_type=file_type,
            user_id=user_id,
            content_hash=content_hash,
        )

        return await self.file_repository.create(file_record)

    async def get_file(self, file_id: int, user_id: int) -> File | None:
        return await self.file_repository.get_by_id(file_id, user_id)

    async def get_user_files(self, user_id: int) -> list[File]:
        return await self.file_repository.get_by_user(user_id)

    async def delete_file(self, file_id: int, user_id: int) -> bool:
        file_record = await self.file_repository.get_by_id(file_id, user_id)
        if not file_record:
            return False

        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)

        return await self.file_repository.delete(file_id, user_id)

    def _get_file_type(self, filename: str) -> FileType:
        extension = Path(filename).suffix.lower()
        type_mapping = {
            ".pdf": FileType.PDF,
            ".txt": FileType.TXT,
            ".docx": FileType.DOCX,
            ".md": FileType.MD,
        }
        return type_mapping.get(extension, FileType.TXT)
