from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.rag.models import Answer, Question
from app.modules.rag.repositories.qa import QARepository
from app.modules.rag.schema import AnswerCreate, QuestionCreate, QuestionStats


@pytest.mark.asyncio
async def test_create_question(mock_session: MagicMock) -> None:
    mock_session.refresh = AsyncMock()
    question_data = QuestionCreate(question_text="Test?", user_id=1)

    repo = QARepository(session=mock_session)
    result = await repo.create_question(question_data)

    assert isinstance(result, Question)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_answer(mock_session: MagicMock) -> None:
    mock_session.refresh = AsyncMock()
    answer_data = AnswerCreate(answer_text="Answer", question_id=1, confidence_score=0.9)

    repo = QARepository(session=mock_session)
    result = await repo.create_answer(answer_data)

    assert isinstance(result, Answer)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_question_by_id(mock_session: MagicMock, mock_question: Question) -> None:
    mock_result = MagicMock()
    mock_result.first.return_value = mock_question
    mock_session.exec.return_value = mock_result

    repo = QARepository(session=mock_session)
    result = await repo.get_question_by_id(1)

    assert result == mock_question


@pytest.mark.asyncio
async def test_get_answers_by_question_id(mock_session: MagicMock, mock_answer: Answer) -> None:
    answers = [mock_answer]
    mock_result = MagicMock()
    mock_result.all.return_value = answers
    mock_session.exec.return_value = mock_result

    repo = QARepository(session=mock_session)
    result = await repo.get_answers_by_question_id(1)

    assert len(result) == 1
    assert result[0] == mock_answer


@pytest.mark.asyncio
async def test_get_questions_by_user(mock_session: MagicMock) -> None:
    questions = [Question(id=i, question_text=f"Q{i}?", user_id=1) for i in range(3)]
    mock_result = MagicMock()
    mock_result.all.return_value = questions
    mock_session.exec.return_value = mock_result

    repo = QARepository(session=mock_session)
    result = await repo.get_questions_by_user(1, limit=50)

    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_questions_by_session(mock_session: MagicMock) -> None:
    questions = [Question(id=i, question_text=f"Q{i}?", user_id=1, session_id="session_123") for i in range(3)]
    mock_result = MagicMock()
    mock_result.all.return_value = questions
    mock_session.exec.return_value = mock_result

    repo = QARepository(session=mock_session)
    result = await repo.get_questions_by_session("session_123")

    assert len(result) == 3


@pytest.mark.asyncio
async def test_get_qa_pairs(mock_session: MagicMock, mock_question: Question, mock_answer: Answer) -> None:
    qa_pairs = [(mock_question, mock_answer)]
    mock_result = MagicMock()
    mock_result.all.return_value = qa_pairs
    mock_session.exec.return_value = mock_result

    repo = QARepository(session=mock_session)
    result = await repo.get_qa_pairs(limit=50)

    assert len(result) == 1
    assert result[0][0] == mock_question
    assert result[0][1] == mock_answer


@pytest.mark.asyncio
async def test_delete_question_success(mock_session: MagicMock, mock_question: Question, mock_answer: Answer) -> None:
    mock_result_question = MagicMock()
    mock_result_question.first.return_value = mock_question
    mock_result_answers = MagicMock()
    mock_result_answers.all.return_value = [mock_answer]
    mock_session.exec.side_effect = [mock_result_question, mock_result_answers]
    mock_session.delete = AsyncMock()

    repo = QARepository(session=mock_session)
    result = await repo.delete_question(1)

    assert result is True
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_question_not_found(mock_session: MagicMock) -> None:
    mock_result = MagicMock()
    mock_result.first.return_value = None
    mock_session.exec.return_value = mock_result

    repo = QARepository(session=mock_session)
    result = await repo.delete_question(999)

    assert result is False


@pytest.mark.asyncio
async def test_get_question_stats(mock_session: MagicMock) -> None:
    questions = [Question(id=i, question_text=f"Q{i}?", user_id=1) for i in range(3)]
    answers = [Answer(id=i, answer_text=f"A{i}", question_id=i, confidence_score=0.9) for i in range(3)]
    mock_result_questions = MagicMock()
    mock_result_questions.all.return_value = questions
    mock_result_answers = MagicMock()
    mock_result_answers.all.return_value = answers
    mock_session.exec.side_effect = [mock_result_questions, mock_result_answers]

    repo = QARepository(session=mock_session)
    result = await repo.get_question_stats(1)

    assert isinstance(result, QuestionStats)
    assert result.total_questions == 3
    assert result.total_answers == 3
    assert result.avg_confidence == 0.9


@pytest.mark.asyncio
async def test_get_question_stats_no_answers(mock_session: MagicMock) -> None:
    questions = [Question(id=i, question_text=f"Q{i}?", user_id=1) for i in range(3)]
    mock_result_questions = MagicMock()
    mock_result_questions.all.return_value = questions
    mock_result_answers = MagicMock()
    mock_result_answers.all.return_value = []
    mock_session.exec.side_effect = [mock_result_questions, mock_result_answers]

    repo = QARepository(session=mock_session)
    result = await repo.get_question_stats(1)

    assert result.avg_confidence == 0
