from typing import Annotated, Any

from fastapi import Depends

from app.modules.files.repository import FileRepository
from app.modules.files.schema import FileType
from app.modules.rag.managers import PDFContentManager, VectorStoreManager, OpenAIService
from app.modules.rag.schema import QuestionRequest, AnswerResponse, SourceReference, ImageReference


class DocumentService:
    def __init__(self,
                 pdf_manager: Annotated[PDFContentManager, Depends(PDFContentManager)],
                 vector_store: Annotated[VectorStoreManager, Depends(VectorStoreManager)],
                 openai_service: Annotated[OpenAIService, Depends(OpenAIService)],
                 files_repository: Annotated[FileRepository, Depends(FileRepository)]
                 ) -> None:
        self.pdf_manager = pdf_manager
        self.vector_store = vector_store
        self.openai_service = openai_service
        self.files_repository = files_repository
        self.processed_files = {}

    async def process_question(self, question: QuestionRequest) -> AnswerResponse:
        files = await self.files_repository.get_all()
        pdf_files = [file for file in files if file.file_type == FileType.PDF]
        
        if not pdf_files:
            return AnswerResponse(
                answer="No PDF documents available for processing.",
                sources=[],
                images=[],
                confidence_score=0.0,
                question_id=0
            )
        
        await self._process_documents(pdf_files)
        
        search_results = self.vector_store.search(question.question, n_results=5)
        
        if not search_results:
            return AnswerResponse(
                answer="No relevant information found in the documents.",
                sources=[],
                images=[],
                confidence_score=0.0,
                question_id=0
            )
        
        context = self._build_context(search_results)
        answer = self.openai_service.generate_answer(question.question, context)
        
        sources = self._build_sources(search_results)
        images = await self._build_images(search_results)
        
        confidence_score = self._calculate_confidence(search_results)
        
        return AnswerResponse(
            answer=answer,
            sources=sources,
            images=images,
            confidence_score=confidence_score,
            question_id=hash(question.question) % 1000000
        )

    async def _process_documents(self, files: list[Any]) -> None:
        for file in files:
            if file.id in self.processed_files:
                continue
                
            try:
                texts, images = self.pdf_manager.process(file.file_path)
                
                chunk_images = {}
                for i, text in enumerate(texts):
                    page_number = getattr(text.metadata, 'page_number', None)
                    chunk_images[i] = []
                    
                    for img_b64 in images:
                        img_page = getattr(img_b64, 'metadata', {}).get('page_number', None) if hasattr(img_b64, 'metadata') else None
                        if page_number is None or img_page is None or page_number == img_page:
                            chunk_images[i].append(img_b64)
                
                self.processed_files[file.id] = {
                    "texts": texts,
                    "chunk_images": chunk_images,
                    "filename": file.filename
                }
                
                documents = []
                for i, text in enumerate(texts):
                    doc_id = f"{file.id}_{i}"
                    documents.append({
                        "id": doc_id,
                        "text": str(text),
                        "metadata": {
                            "file_id": file.id,
                            "filename": file.filename,
                            "chunk_index": i,
                            "page_number": getattr(text.metadata, 'page_number', None)
                        }
                    })
                
                if documents:
                    self.vector_store.add_documents(documents)
                    
            except Exception as e:
                print(f"Error processing file {file.filename}: {str(e)}")
                continue

    def _build_context(self, search_results: list[dict[str, Any]]) -> str:
        context_parts = []
        for result in search_results:
            context_parts.append(f"Source: {result['metadata'].get('filename', 'Unknown')}\n{result['text']}\n")
        return "\n".join(context_parts)

    def _build_sources(self, search_results: list[dict[str, Any]]) -> list[SourceReference]:
        sources = []
        for result in search_results:
            metadata = result['metadata']
            sources.append(SourceReference(
                file_id=metadata.get('file_id', 0),
                filename=metadata.get('filename', 'Unknown'),
                page_number=metadata.get('page_number'),
                chunk_index=metadata.get('chunk_index', 0),
                relevance_score=1.0 - result.get('distance', 0.0)
            ))
        return sources

    async def _build_images(self, search_results: list[dict[str, Any]]) -> list[ImageReference]:
        images = []
        
        for result in search_results:
            metadata = result['metadata']
            file_id = metadata.get('file_id')
            chunk_index = metadata.get('chunk_index')
            
            if file_id in self.processed_files:
                file_data = self.processed_files[file_id]
                chunk_images = file_data.get('chunk_images', {})
                filename = file_data['filename']
                
                if chunk_index in chunk_images:
                    for img_b64 in chunk_images[chunk_index]:
                        images.append(ImageReference(
                            image_path=f"data:image/png;base64,{img_b64}",
                            description=f"Image from {filename} (chunk {chunk_index})",
                            page_number=metadata.get('page_number'),
                            file_id=file_id
                        ))
        
        return images[:5]

    def _calculate_confidence(self, search_results: list[dict[str, Any]]) -> float:
        if not search_results:
            return 0.0
        
        distances = [result.get('distance', 1.0) for result in search_results]
        avg_distance = sum(distances) / len(distances)
        return max(0.0, min(1.0, 1.0 - avg_distance))

