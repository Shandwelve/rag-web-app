from sqlmodel import select

from app.core.repositories import Repository
from app.modules.rag.models import Answer, Question
from app.modules.rag.schema import AnswerCreate, QuestionCreate, QuestionStats


class QARepository(Repository):
    async def create_question(self, question_data: QuestionCreate) -> Question:
        question = Question(**question_data.model_dump())
        self._session.add(question)
        await self._session.commit()
        await self._session.refresh(question)
        return question

    async def create_answer(self, answer_data: AnswerCreate) -> Answer:
        answer = Answer(**answer_data.model_dump())
        self._session.add(answer)
        await self._session.commit()
        await self._session.refresh(answer)
        return answer

    async def get_question_by_id(self, question_id: int) -> Question | None:
        result = await self._session.exec(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()

    async def get_answers_by_question_id(self, question_id: int) -> list[Answer]:
        result = await self._session.exec(
            select(Answer).where(Answer.question_id == question_id)
        )
        return list(result.scalars().all())

    async def get_questions_by_user(
        self, user_id: int, limit: int = 50
    ) -> list[Question]:
        result = await self._session.exec(
            select(Question)
            .where(Question.user_id == user_id)
            .order_by(Question.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_questions_by_session(self, session_id: str) -> list[Question]:
        result = await self._session.exec(
            select(Question)
            .where(Question.session_id == session_id)
            .order_by(Question.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_qa_pairs_by_user(
        self, user_id: int, limit: int = 50
    ) -> list[tuple[Question, Answer]]:
        result = await self._session.exec(
            select(Question, Answer)
            .join(Answer, Question.id == Answer.question_id)
            .where(Question.user_id == user_id)
            .order_by(Question.created_at.desc())
            .limit(limit)
        )
        return list(result.all())

    async def delete_question(self, question_id: int) -> bool:
        question = await self.get_question_by_id(question_id)
        if question:
            await self._session.delete(question)
            await self._session.commit()
            return True
        return False

    async def get_question_stats(self, user_id: int) -> QuestionStats:
        questions_result = await self._session.exec(
            select(Question).where(Question.user_id == user_id)
        )
        questions = list(questions_result.scalars().all())

        answers_result = await self._session.exec(
            select(Answer).join(Question).where(Question.user_id == user_id)
        )
        answers = list(answers_result.scalars().all())

        return QuestionStats(
            total_questions=len(questions),
            total_answers=len(answers),
            avg_confidence=(
                sum(a.confidence_score for a in answers) / len(answers)
                if answers
                else 0
            ),
        )
