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

    async def search_by_embedding(
        self, query_embedding: list[float], n_results: int = 5
    ) -> list[DocumentChunk]:
        stmt = (
            select(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(n_results)
        )
        
        result = await self._session.exec(stmt)
        return list(result.all())
