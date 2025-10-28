import openai

from app.core.config import settings


class OpenAIService:
    def __init__(self) -> None:
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_answer(self, question: str, context: str) -> str:
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

        return response.choices[0].message.content
