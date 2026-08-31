"""Starter suggestions must be written in the reader's own language.

``_output_language`` returns the reply-language setting, but generation used to
pick between an English and a Chinese system prompt only — so a Korean reader
got the English prompt and three English lines under the composer.
"""

from __future__ import annotations

import pytest

from deeptutor.services import suggestions as sg


@pytest.mark.parametrize(
    ("value", "expected"),
    [("ko", "ko"), ("ko-KR", "ko"), ("KO", "ko"), ("zh", "zh"), ("zh-TW", "zh"), ("fr", "en"), ("", "en")],
)
def test_language_normalisation(value: str, expected: str) -> None:
    assert sg._lang(value) == expected


def test_every_ui_locale_has_a_system_prompt() -> None:
    assert set(sg._SYSTEMS) == {"en", "zh", "ko"}
    assert "한국어" not in sg._SYSTEMS["en"]
    assert "JSON" in sg._SYSTEMS["ko"]


def test_prompt_scaffolding_covers_every_locale() -> None:
    for table in (sg._PROFILE_HEADING, sg._ACTIVITY_HEADING, sg._CLOSING, sg._SURFACE_LABELS):
        assert set(table) == {"en", "zh", "ko"}


def test_length_bounds_are_per_locale() -> None:
    # A CJK-sized bound applied to English silently rejects well-formed output.
    assert sg._bound(sg._MAX_LABEL_CHARS, "ko") != sg._bound(sg._MAX_LABEL_CHARS, "en")
    assert sg._bound(sg._MAX_LABEL_CHARS, "fr") == sg._MAX_LABEL_CHARS["en"]


def test_material_is_rendered_in_the_reader_s_language() -> None:
    topic = sg._Topic(surface="chat", label="RAG", days_ago=2)

    assert sg._render_topics([topic], "ko") == "- [대화, 2일 전] RAG"
    assert sg._render_topics([topic], "en") == "- [conversation, 2d ago] RAG"
    assert sg._render_topics([topic], "fr") == "- [conversation, 2d ago] RAG"


def test_today_reads_naturally_in_every_locale() -> None:
    topic = sg._Topic(surface="chat", label="RAG", days_ago=0)

    assert "오늘" in sg._render_topics([topic], "ko")
    assert "today" in sg._render_topics([topic], "en")
