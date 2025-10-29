import openai

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIService:
    def __init__(self) -> None:
        logger.info(f"Initializing OpenAIService with model: {settings.CHAT_MODEL}")
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_answer(self, question: str, context: str) -> str:
        logger.info(f"Generating answer for question: {question[:100]}...")
        logger.debug(f"Context length: {len(context)} characters")
        try:
            system_prompt = """You are a helpful assistant that answers questions based on provided context. 
        Provide accurate, detailed answers based on the context. If the context doesn't contain enough information, 
        say so clearly. Be concise but comprehensive."""

            user_prompt = f"""Context: {context}
        
        Question: {question}
        
        Please provide a detailed answer based on the context above."""

            response = self.client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=settings.MAX_TOKENS,
                temperature=0.7,
            )

            answer = response.choices[0].message.content
            logger.info(f"Answer generated successfully. Length: {len(answer)} characters")
            logger.debug(f"Tokens used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            return answer
        except Exception as e:
            logger.error(f"Error generating answer with OpenAI: {str(e)}", exc_info=True)
            raise
