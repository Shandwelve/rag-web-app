from sqlmodel import select

from app.core.repositories import Repository
from app.modules.rag.models import DocumentChunk


class DocumentChunkRepository(Repository):
    async def create_batch(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        for chunk in chunks:
            self._session.add(chunk)

        await self._session.commit()
        for chunk in chunks:
            await self._session.refresh(chunk)

        return chunks

    async def search_by_embedding(self, query_embedding: list[float], n_results: int = 5) -> list[DocumentChunk]:
        statement = (
            select(DocumentChunk).order_by(DocumentChunk.embedding.cosine_distance(query_embedding)).limit(n_results)
        )

        result = await self._session.exec(statement)
        return list(result.all())

    async def get_by_file_id(self, file_id: int) -> list[DocumentChunk]:
        statement = select(DocumentChunk).where(DocumentChunk.file_id == file_id).order_by(DocumentChunk.chunk_index)
        result = await self._session.exec(statement)
        return list(result.all())

    async def get_by_file_id_and_chunk_index(self, file_id: int, chunk_index: int) -> DocumentChunk | None:
        statement = select(DocumentChunk).where(
            DocumentChunk.file_id == file_id, DocumentChunk.chunk_index == chunk_index
        )
        result = await self._session.exec(statement)
        return result.first()

    async def chunk_exists(self, file_id: int) -> bool:
        statement = select(DocumentChunk).where(DocumentChunk.file_id == file_id).limit(1)
        result = await self._session.exec(statement)
        return result.first() is not None
