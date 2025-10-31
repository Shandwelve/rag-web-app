from unittest.mock import MagicMock, patch

import pytest

from app.modules.rag.services.audio_processing_service import AudioProcessingService


@pytest.mark.asyncio
async def test_transcribe_with_openai() -> None:
    mock_client = MagicMock()
    mock_transcription = MagicMock()
    mock_transcription.strip.return_value = "Transcribed text"
    mock_client.audio.transcriptions.create.return_value = mock_transcription

    with patch("app.modules.rag.services.audio_processing_service.openai.OpenAI", return_value=mock_client):
        with patch("app.modules.rag.services.audio_processing_service.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            with patch("tempfile.NamedTemporaryFile") as mock_tempfile:
                mock_file = MagicMock()
                mock_file.name = "/tmp/test.webm"
                mock_file.__enter__.return_value = mock_file
                mock_file.__exit__.return_value = None
                mock_tempfile.return_value = mock_file

                with patch("builtins.open", create=True) as mock_open:
                    mock_file_obj = MagicMock()
                    mock_open.return_value.__enter__.return_value = mock_file_obj
                    mock_open.return_value.__exit__.return_value = None

                    service = AudioProcessingService()
                    text, metadata = await service.transcribe_with_openai(b"audio_data", "test.webm")

                    assert text == "Transcribed text"
                    assert "provider" in metadata
                    assert metadata["filename"] == "test.webm"
