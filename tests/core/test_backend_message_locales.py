"""Backend-facing user messages must cover every UI locale.

``deeptutor.core.i18n.t`` picks its table from the interface language, so a
locale missing from ``_MESSAGES`` shows English text inside an otherwise
translated UI. ``metadata_i18n`` feeds the same surfaces from a second table.
"""

from __future__ import annotations

import pytest

from deeptutor.core import i18n
from deeptutor.i18n.metadata_i18n import (
    capability_description_i18n,
    localized_description,
    tool_description_i18n,
)

_LOCALES = ("en", "zh", "ko")


def test_every_locale_defines_the_same_message_keys() -> None:
    english = set(i18n._MESSAGES["en"])
    for locale in _LOCALES:
        assert set(i18n._MESSAGES[locale]) == english, locale


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("ko", "ko"),
        ("KO", "ko"),
        ("korean", "ko"),
        ("kr", "ko"),
        ("ko-KR", "ko"),
        ("zh", "zh"),
        ("fr", "en"),
        (None, "en"),
    ],
)
def test_language_parsing(value: str | None, expected: str) -> None:
    assert i18n._parse_language(value) == expected


def test_korean_messages_are_translated_and_interpolate() -> None:
    assert i18n.t("api.partner_not_found", language="ko") == "파트너를 찾을 수 없습니다"
    assert "12" in i18n.t("cli_apps.still_running", language="ko", app="demo", seconds=12)


def test_unknown_key_falls_back_to_the_default() -> None:
    assert i18n.t("does.not.exist", "fallback", language="ko") == "fallback"


def test_metadata_descriptions_carry_korean() -> None:
    for values in (tool_description_i18n("web_search"), capability_description_i18n("chat")):
        assert set(values) == {"en", "zh", "ko"}
        assert values["ko"] != values["en"]
        assert localized_description(values, "ko") == values["ko"]

    assert localized_description(tool_description_i18n("web_search"), "fr") == (
        tool_description_i18n("web_search")["en"]
    )


def test_unmapped_names_fall_back_across_every_locale() -> None:
    assert tool_description_i18n("nope", "raw") == {"en": "raw", "zh": "raw", "ko": "raw"}
