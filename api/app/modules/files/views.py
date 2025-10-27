from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.modules.files.schema import FileRead
from app.modules.files.service import FileService

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_file_view(
    file: Annotated[UploadFile, File()],
    file_service: Annotated[FileService, Depends()],
    user_id: int = 1,
) -> FileRead:
    if not file.filename:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No file provided")
    
    try:
        file_content = await file.read()
        file_record = await file_service.save_file(
            file_content, file.filename, user_id
        )
        return FileRead.model_validate(file_record)
    except Exception as e:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail="Could not save file") from e


@router.get("/")
async def get_files_view(
    file_service: Annotated[FileService, Depends()],
    user_id: int = 1,
) -> list[FileRead]:
    files = await file_service.get_user_files(user_id)
    return [FileRead.model_validate(file) for file in files]


@router.get("/{file_id}")
async def get_file_view(
    file_id: int,
    file_service: Annotated[FileService, Depends()],
    user_id: int = 1,
) -> FileRead:
    file_record = await file_service.get_file(file_id, user_id)
    
    if not file_record:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="File not found")
    
    return FileRead.model_validate(file_record)


@router.delete("/{file_id}")
async def delete_file_view(
    file_id: int,
    user_id: int,
    file_service: Annotated[FileService, Depends()],
):
    success = await file_service.delete_file(file_id, user_id)
    
    if not success:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="File not found")
    
    return {"message": "File deleted successfully"}
