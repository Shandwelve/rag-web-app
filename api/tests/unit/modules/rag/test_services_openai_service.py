from unittest.mock import MagicMock, patch

import pytest

from app.modules.rag.services.openai_service import OpenAIService


def test_generate_answer() -> None:
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Generated answer"
    mock_response.usage.total_tokens = 100
    mock_client.chat.completions.create.return_value = mock_response

    with patch("app.modules.rag.services.openai_service.openai.OpenAI", return_value=mock_client):
        with patch("app.modules.rag.services.openai_service.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test_key"
            mock_settings.CHAT_MODEL = "gpt-4o-mini"
            mock_settings.MAX_TOKENS = 1000

            service = OpenAIService()
            result = service.generate_answer("Question?", "Context")

            assert result == "Generated answer"
            mock_client.chat.completions.create.assert_called_once()
