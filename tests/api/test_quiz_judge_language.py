"""The AI judge must grade in every language the interface offers."""

from __future__ import annotations

import pytest

from deeptutor.api.routers import quiz_judge


def test_every_ui_locale_has_a_judge_system_prompt() -> None:
    assert quiz_judge._JUDGE_LANGUAGES == {"en", "zh", "ko"}


def test_korean_system_prompt_asks_for_korean() -> None:
    assert "한국어로 답합니다" in quiz_judge._JUDGE_SYSTEM_PROMPTS["ko"]


@pytest.mark.parametrize("language", sorted(quiz_judge._JUDGE_LANGUAGES))
def test_user_prompt_is_built_for_every_locale(language: str) -> None:
    prompt = quiz_judge._build_judge_user_prompt(
        language=language,
        question="1 + 1 = ?",
        question_type="short_answer",
        options={"A": "1", "B": "2"},
        correct_answer="2",
        explanation="basic addition",
        user_answer="3",
        has_image=False,
    )

    assert "1 + 1 = ?" in prompt
    assert "2" in prompt


def test_korean_user_prompt_is_written_in_korean() -> None:
    prompt = quiz_judge._build_judge_user_prompt(
        language="ko",
        question="1 + 1 = ?",
        question_type="short_answer",
        options=None,
        correct_answer="2",
        explanation="",
        user_answer="",
        has_image=True,
        image_count=2,
    )

    assert "학습자의 답안:" in prompt
    assert "이미지만 제출했고" in prompt
    assert "이미지 2장" in prompt
    # An unknown language must not leak Korean into the English branch.
    assert "학습자" not in quiz_judge._build_judge_user_prompt(
        language="fr",
        question="q",
        question_type="",
        options=None,
        correct_answer="",
        explanation="",
        user_answer="a",
        has_image=False,
    )
