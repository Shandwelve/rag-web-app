import traceback
from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from app.core.exceptions import BaseServiceError
from app.core.logging import get_logger, setup_logging
from app.modules.files.views import router as files_router

setup_logging()
logger = get_logger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.error(f"HTTP exception occurred: {exc.detail} (status: {exc.status_code})")
    safe_content = {
        "message": "A HTTP error occurred.",
        "detail": exc.detail,
    }

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(safe_content),
    )


@app.exception_handler(BaseServiceError)
async def service_exception_handler(request: Request, exc: BaseServiceError) -> JSONResponse:
    logger.error(f"Service error occurred: {str(exc)}")
    safe_content = {
        "message": "A service error occurred.",
        "detail": str(exc),
    }

    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content=jsonable_encoder(safe_content),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Fatal error occurred: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred."},
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
