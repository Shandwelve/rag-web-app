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
            system_prompt = """You are a helpful assistant that answers questions using the provided context.
            Use all available information to give the most accurate, complete, and helpful answer possible.
            If the context gives indirect or partial clues, infer a reasonable answer.
            Only say there is not enough information if the context contains absolutely no related details.
            Be specific, factual, and confident in your reasoning.
            """

            user_prompt = f"""Context:
            {context}

            Question:
            {question}

            Instructions:
            - Use relevant details from the context to form your answer.
            - If the context partially addresses the question, summarize or infer what can be reasonably concluded.
            - Only state that information is missing if the context truly contains none related to the question.
            - Avoid generic disclaimers; provide the best possible, context-based response.
            - Be concise but complete.
            """

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
