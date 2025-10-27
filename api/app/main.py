from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.core.exceptions import BaseServiceError
from app.core.logging import get_logger, setup_logging

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


@app.exception_handler(BaseServiceError)
async def http_exception_handler(request: Request, exc: BaseServiceError) -> JSONResponse:
    logger.error(f"HTTP exception occurred. {str(exc)}")
    safe_content = {
        "message": "A HTTP error occurred.",
        "detail": str(exc),
    }

    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content=jsonable_encoder(safe_content),
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"An unexpected error occurred. {str(exc)}")
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred."},
    )


@app.get("/")
def root() -> dict[str, str]:
    logger.info("Root endpoint accessed")
    return {"message": "hello world"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
