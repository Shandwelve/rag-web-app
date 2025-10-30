import json
import time
from typing import Annotated, Any

from fastapi import Depends, UploadFile

from app.core.logging import get_logger
from app.modules.files.repository import FileRepository
from app.modules.files.schema import FileType
from app.modules.rag.models import Answer, Question
from app.modules.rag.repository import QARepository
from app.modules.rag.schema import (
    AnswerCreate,
    AnswerResponse,
    ImageReference,
    QuestionCreate,
    QuestionRequest,
    QuestionStats,
    RAGResult,
    SourceReference,
)
from app.modules.rag.services.audio_processing_service import AudioProcessingService
from app.modules.rag.services.openai_service import OpenAIService
from app.modules.rag.services.content_manager import PDFContentManager, DOCXContentManager
from app.modules.rag.services.vector_store_manager import VectorStoreManager

logger = get_logger(__name__)


class DocumentService:
    def __init__(
        self,
        pdf_manager: Annotated[PDFContentManager, Depends(PDFContentManager)],
        docx_manager: Annotated[DOCXContentManager, Depends(DOCXContentManager)],
        vector_store: Annotated[VectorStoreManager, Depends(VectorStoreManager)],
        openai_service: Annotated[OpenAIService, Depends(OpenAIService)],
        files_repository: Annotated[FileRepository, Depends(FileRepository)],
        qa_repository: Annotated[QARepository, Depends(QARepository)],
        audio_service: Annotated[AudioProcessingService, Depends(AudioProcessingService)],
    ) -> None:
        self.pdf_manager = pdf_manager
        self.docx_manager = docx_manager
        self.vector_store = vector_store
        self.openai_service = openai_service
        self.files_repository = files_repository
        self.qa_repository = qa_repository
        self.audio_service = audio_service
        self.processed_files = {}

    async def process_question(self, question: QuestionRequest, user_id: int = 1) -> AnswerResponse:
        start_time = time.time()
        logger.info(f"Processing question for user {user_id}: {question.question[:100]}...")

        question_record = await self._create_question_record(question, user_id)

        try:
            rag_result = await self._process_rag_query(question.question)
            processing_time = self._calculate_processing_time(start_time)

            await self._create_answer_record(question_record.id, rag_result, processing_time)

            logger.info(f"Successfully processed question {question_record.id} in {processing_time}ms")
            return self._build_response(question_record.id, rag_result)

        except Exception as e:
            processing_time = self._calculate_processing_time(start_time)
            error_result = self._create_error_result(str(e))

            logger.error(f"Error processing question {question_record.id}: {str(e)}")
            await self._create_answer_record(question_record.id, error_result, processing_time)

            return self._build_response(question_record.id, error_result)

    async def _create_question_record(self, question: QuestionRequest, user_id: int) -> Question:
        return await self.qa_repository.create_question(
            QuestionCreate(
                question_text=question.question,
                user_id=user_id,
                session_id=question.session_id,
            )
        )

    async def _process_rag_query(self, question_text: str) -> RAGResult:
        logger.debug(f"Processing RAG query: {question_text[:100]}...")
        documents = await self._get_available_documents()
        logger.debug(f"Found {len(documents)} available documents")

        if not documents:
            logger.warning("No documents available for RAG query")
            return self._create_no_documents_result()

        await self._process_documents(documents)
        logger.debug("Executing vector store search")
        search_results = await self.vector_store.search(question_text, n_results=5)

        if not search_results:
            logger.warning("No search results found in vector store")
            return self._create_no_results_result()

        logger.debug(f"Found {len(search_results)} search results, generating RAG response")
        return await self._generate_rag_response(question_text, search_results)

    async def _get_available_documents(self) -> list:
        files = await self.files_repository.get_all()
        documents = [file for file in files if file.file_type in [FileType.PDF, FileType.DOCX]]
        logger.debug(f"Retrieved {len(documents)} documents (PDF/DOCX) from {len(files)} total files")
        return documents

    def _create_no_documents_result(self) -> RAGResult:
        return {
            "answer_text": "No documents available for processing.",
            "sources": [],
            "images": [],
            "confidence_score": 0.0,
        }

    def _create_no_results_result(self) -> RAGResult:
        return {
            "answer_text": "No relevant information found in the documents.",
            "sources": [],
            "images": [],
            "confidence_score": 0.0,
        }

    async def _generate_rag_response(self, question_text: str, search_results: list) -> RAGResult:
        context = self._build_context(search_results)
        answer_text = self.openai_service.generate_answer(question_text, context)
        sources = self._build_sources(search_results)
        images = await self._build_images(search_results)
        confidence_score = self._calculate_confidence(search_results)

        return {
            "answer_text": answer_text,
            "sources": sources,
            "images": images,
            "confidence_score": confidence_score,
        }

    def _create_error_result(self, error_message: str) -> RAGResult:
        return {
            "answer_text": f"An error occurred while processing your question: {error_message}",
            "sources": [],
            "images": [],
            "confidence_score": 0.0,
        }

    def _calculate_processing_time(self, start_time: float) -> int:
        return int((time.time() - start_time) * 1000)

    async def _create_answer_record(self, question_id: int, rag_result: RAGResult, processing_time: int) -> Answer:
        return await self.qa_repository.create_answer(
            AnswerCreate(
                answer_text=rag_result["answer_text"],
                question_id=question_id,
                confidence_score=rag_result["confidence_score"],
                sources_used=self._serialize_sources(rag_result["sources"]),
                images_used=self._serialize_images(rag_result["images"]),
                processing_time_ms=processing_time,
            )
        )

    def _serialize_sources(self, sources: list) -> str | None:
        return json.dumps([s.model_dump() for s in sources]) if sources else None

    def _serialize_images(self, images: list) -> str | None:
        return json.dumps([i.model_dump() for i in images]) if images else None

    def _build_response(self, question_id: int, rag_result: RAGResult) -> AnswerResponse:
        return AnswerResponse(
            answer=rag_result["answer_text"],
            sources=rag_result["sources"],
            images=rag_result["images"],
            confidence_score=rag_result["confidence_score"],
            question_id=question_id,
        )

    async def get_question_history(self, user_id: int, limit: int = 50) -> list[dict]:
        qa_pairs = await self.qa_repository.get_qa_pairs_by_user(user_id, limit)
        return [{"question": qa_pair[0], "answer": qa_pair[1]} for qa_pair in qa_pairs]

    async def get_session_history(self, session_id: str) -> list[dict]:
        questions = await self.qa_repository.get_questions_by_session(session_id)
        qa_pairs = []

        for question in questions:
            answers = await self.qa_repository.get_answers_by_question_id(question.id)
            if answers:
                qa_pairs.append({"question": question, "answer": answers[0]})

        return qa_pairs

    async def delete_question(self, question_id: int) -> bool:
        return await self.qa_repository.delete_question(question_id)

    async def get_user_stats(self, user_id: int) -> QuestionStats:
        return await self.qa_repository.get_question_stats(user_id)

    async def process_audio_question(
        self, audio_file: UploadFile, user_id: int = 1, session_id: str = None
    ) -> AnswerResponse:
        start_time = time.time()
        logger.info(f"Processing audio question for user {user_id}")

        try:
            audio_data = await audio_file.read()
            transcribed_text, audio_metadata = await self.audio_service.transcribe_with_openai(
                audio_data, audio_file.filename
            )

            logger.info(f"Transcribed audio: '{transcribed_text[:100]}...'")

            question_record = await self._create_audio_question_record(
                transcribed_text, user_id, session_id, audio_metadata
            )

            rag_result = await self._process_rag_query(transcribed_text)
            processing_time = self._calculate_processing_time(start_time)

            rag_result["audio_metadata"] = audio_metadata

            await self._create_answer_record(question_record.id, rag_result, processing_time)

            logger.info(f"Successfully processed audio question {question_record.id} in {processing_time}ms")
            return self._build_response(question_record.id, rag_result)

        except Exception as e:
            processing_time = self._calculate_processing_time(start_time)
            error_result = self._create_error_result(f"Audio processing failed: {str(e)}")

            logger.error(f"Error processing audio question: {str(e)}")

            try:
                question_record = await self._create_audio_question_record(
                    f"[Audio processing failed: {str(e)}]", user_id, session_id, {}
                )
                await self._create_answer_record(question_record.id, error_result, processing_time)
                return self._build_response(question_record.id, error_result)
            except Exception:
                return AnswerResponse(
                    answer=f"Failed to process audio question: {str(e)}",
                    sources=[],
                    images=[],
                    confidence_score=0.0,
                    question_id=0,
                )

    async def _create_audio_question_record(
        self,
        transcribed_text: str,
        user_id: int,
        session_id: str = None,
        audio_metadata: dict = None,
    ) -> Question:
        context_files = json.dumps(audio_metadata) if audio_metadata else None

        return await self.qa_repository.create_question(
            QuestionCreate(
                question_text=transcribed_text,
                user_id=user_id,
                session_id=session_id,
                context_files=context_files,
            )
        )

    async def _process_documents(self, files: list[Any]) -> None:
        logger.info(f"Processing {len(files)} documents")
        for file in files:
            if file.id in self.processed_files:
                logger.debug(f"File {file.id} ({file.original_filename}) already processed, skipping")
                continue

            try:
                logger.info(f"Processing file {file.id}: {file.original_filename} (type: {file.file_type})")
                if file.file_type == FileType.PDF:
                    texts, images = self.pdf_manager.process(file.file_path)
                elif file.file_type == FileType.DOCX:
                    texts, images = self.docx_manager.process(file.file_path)
                else:
                    logger.warning(f"Unsupported file type: {file.file_type} for file {file.original_filename}")
                    continue

                chunk_images = {}
                for i, text in enumerate(texts):
                    page_number = getattr(text.metadata, "page_number", None)
                    chunk_images[i] = []

                    for img_b64 in images:
                        img_page = (
                            getattr(img_b64, "metadata", {}).get("page_number", None)
                            if hasattr(img_b64, "metadata")
                            else None
                        )
                        if page_number is None or img_page is None or page_number == img_page:
                            chunk_images[i].append(img_b64)

                self.processed_files[file.id] = {
                    "texts": texts,
                    "chunk_images": chunk_images,
                    "filename": file.original_filename,
                }

                documents = []
                for i, text in enumerate(texts):
                    doc_id = f"{file.id}_{i}"
                    documents.append(
                        {
                            "id": doc_id,
                            "text": str(text),
                            "metadata": {
                                "file_id": file.id,
                                "filename": file.original_filename,
                                "chunk_index": i,
                                "page_number": getattr(text.metadata, "page_number", None),
                            },
                        }
                    )

                if documents:
                    logger.debug(f"Adding {len(documents)} document chunks to vector store for file {file.id}")
                    await self.vector_store.add_documents(documents)
                else:
                    logger.warning(f"No documents extracted from file {file.original_filename}")

            except Exception as e:
                logger.error(f"Error processing file {file.original_filename} (id: {file.id}): {str(e)}", exc_info=True)
                continue

    def _build_context(self, search_results: list[dict[str, Any]]) -> str:
        context_parts = []
        for result in search_results:
            context_parts.append(f"Source: {result['metadata'].get('filename', 'Unknown')}\n{result['text']}\n")
        return "\n".join(context_parts)

    def _build_sources(self, search_results: list[dict[str, Any]]) -> list[SourceReference]:
        sources = []
        top_results = search_results[:3]
        relevance_threshold = 0.6
        
        for result in top_results:
            distance = result.get("distance", 1.0)
            if distance > relevance_threshold:
                continue
                
            metadata = result["metadata"]
            sources.append(
                SourceReference(
                    file_id=metadata.get("file_id", 0),
                    filename=metadata.get("filename", "Unknown"),
                    page_number=metadata.get("page_number"),
                    chunk_index=metadata.get("chunk_index", 0),
                    relevance_score=1.0 - distance,
                )
            )
        return sources

    async def _build_images(self, search_results: list[dict[str, Any]]) -> list[ImageReference]:
        images = []
        seen_image_b64 = set()
        top_results = search_results[:3]
        min_relevance_score = 0.4
        
        for result in top_results:
            distance = result.get("distance", 1.0)
            relevance_score = 1.0 - distance
            
            if relevance_score < min_relevance_score:
                continue
                
            metadata = result["metadata"]
            file_id = metadata.get("file_id")
            chunk_index = metadata.get("chunk_index")

            if file_id in self.processed_files:
                file_data = self.processed_files[file_id]
                chunk_images = file_data.get("chunk_images", {})
                filename = file_data["filename"]

                if chunk_index in chunk_images:
                    for img_b64 in chunk_images[chunk_index]:
                        images.append(
                            ImageReference(
                                image_path=f"data:image/png;base64,{img_b64}",
                                description=f"Image from {filename} (chunk {chunk_index})",
                                page_number=metadata.get("page_number"),
                                file_id=file_id,
                            )
                        )

        return images[:5]

    def _calculate_confidence(self, search_results: list[dict[str, Any]]) -> float:
        if not search_results:
            return 0.0

        distances = [result.get("distance", 1.0) for result in search_results]
        avg_distance = sum(distances) / len(distances)
        return max(0.0, min(1.0, 1.0 - avg_distance))
