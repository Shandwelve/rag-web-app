from sqlmodel import select

from app.core.repositories import Repository
from app.modules.rag.models import Image


class ImageRepository(Repository):
    async def create_batch(self, images: list[Image]) -> list[Image]:
        for image in images:
            self._session.add(image)

        await self._session.commit()
        for image in images:
            await self._session.refresh(image)

        return images

    async def get_by_chunk_id(self, chunk_id: int) -> list[Image]:
        statement = select(Image).where(Image.chunk_id == chunk_id).order_by(Image.image_index)
        result = await self._session.exec(statement)
        return list(result.all())

    async def get_by_chunk_ids(self, chunk_ids: list[int]) -> list[Image]:
        statement = select(Image).where(Image.chunk_id.in_(chunk_ids)).order_by(Image.chunk_id, Image.image_index)
        result = await self._session.exec(statement)
        return list(result.all())

    async def get_by_file_id(self, file_id: int) -> list[Image]:
        statement = select(Image).where(Image.file_id == file_id).order_by(Image.image_index)
        result = await self._session.exec(statement)
        return list(result.all())

    async def delete_by_file_id(self, file_id: int) -> int:
        statement = select(Image).where(Image.file_id == file_id)
        result = await self._session.exec(statement)
        images = list(result.all())
        for image in images:
            await self._session.delete(image)
        await self._session.commit()
        return len(images)
