import tempfile
from typing import Any

import aiofiles
import openai

from app.core.logging import get_logger

logger = get_logger(__name__)


class AudioProcessingService:
    async def transcribe_with_openai(self, audio_data: bytes, filename: str = None) -> tuple[str, dict[str, Any]]:
        logger.info(f"Starting audio transcription for file: {filename}, size: {len(audio_data)} bytes")
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()

                async with aiofiles.open(temp_file.name, "rb") as f:
                    logger.debug(f"Calling OpenAI Whisper API for transcription")
                    transcript = openai.Audio.transcribe("whisper-1", f)
                    transcribed_text = transcript.text.strip()

                logger.info(f"Transcription completed. Text length: {len(transcribed_text)} characters")

                metadata = {"provider": "openai", "filename": filename}

                return transcribed_text, metadata
        except Exception as e:
            logger.error(f"Error during audio transcription for file {filename}: {str(e)}", exc_info=True)
            raise
