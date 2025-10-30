import tempfile
from typing import Any

import openai

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AudioProcessingService:
    def __init__(self) -> None:
        logger.info("Initializing AudioProcessingService with OpenAI client")
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe_with_openai(self, audio_data: bytes, filename: str = None) -> tuple[str, dict[str, Any]]:
        logger.info(f"Starting audio transcription for file: {filename}, size: {len(audio_data)} bytes")
        try:
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                temp_file_name = temp_file.name

            logger.debug("Calling OpenAI Whisper API for transcription")
            with open(temp_file_name, "rb") as f:  # noqa: PTH123 ASYNC230
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="text",
                    language="en",
                )

            transcribed_text = transcript.strip()

            logger.info(f"Transcription completed. Text length: {len(transcribed_text)} characters")

            metadata = {"provider": "openai", "filename": filename}

            return transcribed_text, metadata
        except Exception as e:
            logger.error(
                f"Error during audio transcription for file {filename}: {str(e)}",
                exc_info=True,
            )
            raise
