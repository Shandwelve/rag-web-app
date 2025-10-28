import tempfile
from typing import Any

import aiofiles
import openai


class AudioProcessingService:
    async def transcribe_with_openai(self, audio_data: bytes, filename: str = None) -> tuple[str, dict[str, Any]]:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()

            async with aiofiles.open(temp_file.name, "rb") as f:
                transcript = openai.Audio.transcribe("whisper-1", f)
                transcribed_text = transcript.text.strip()

            metadata = {"provider": "openai", "filename": filename}

            return transcribed_text, metadata
