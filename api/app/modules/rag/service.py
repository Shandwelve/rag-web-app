from typing import Annotated

from fastapi import Depends

from app.modules.files.repository import FileRepository
from app.modules.files.schema import FileType
from app.modules.rag.managers import PDFContentManager
from app.modules.rag.schema import QuestionRequest, AnswerResponse


class DocumentService:
   def __init__(self,
                pdf_manager: Annotated[PDFContentManager, Depends(PDFContentManager)],
                files_repository: Annotated[FileRepository, Depends(FileRepository)]
                ) -> None:
      self.pdf_manager = pdf_manager
      self.files_repository = files_repository

   async def process_question(self, question: QuestionRequest) -> AnswerResponse:
      files = await self.files_repository.get_all()
      content = {}
      for file in files:
         if file.file_type == FileType.PDF:
            content[file.filename] = self.pdf_manager.process(file.file_path)
      pass

