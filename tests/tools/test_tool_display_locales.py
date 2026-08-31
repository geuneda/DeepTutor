"""Every built-in tool must have display copy in every UI locale.

The Settings → Tools page renders a tool's prompt hint, falling back to its
localized display description. The base ``get_prompt_hints`` echoes the tool's
English definition for any locale with no hints file, so without the swap in
``_localised_hints`` a Korean UI shows English for the ~50 tools that ship no
hints YAML.
"""

from __future__ import annotations

import asyncio
import re

import pytest

from deeptutor.api.routers.tools import list_builtin_tools

_LOCALES = ("en", "zh", "ko")
_HANGUL = re.compile(r"[가-힣]")
_HAN = re.compile(r"[一-鿿]")


@pytest.fixture(scope="module")
def tools():
    return asyncio.run(list_builtin_tools()).tools


def _shown(tool, locale: str) -> str:
    return (
        tool.hints[locale].short_description
        or tool.description_i18n.get(locale, "")
        or tool.description
    )


def test_every_tool_reports_all_locales(tools) -> None:
    assert tools
    for tool in tools:
        assert set(tool.hints) == set(_LOCALES), tool.name
        assert set(tool.description_i18n) == set(_LOCALES), tool.name


def test_korean_ui_never_falls_back_to_english(tools) -> None:
    english = [t.name for t in tools if not _HANGUL.search(_shown(t, "ko"))]
    assert english == [], (
        "these tools render English copy in a Korean UI — add an entry to "
        f"_TOOL_DESCRIPTIONS or a hints/ko yaml: {english}"
    )


def test_chinese_ui_never_falls_back_to_english(tools) -> None:
    english = [t.name for t in tools if not _HAN.search(_shown(t, "zh"))]
    assert english == [], english


def test_english_copy_is_unchanged_by_the_localisation_swap(tools) -> None:
    # The swap must not quietly rewrite what an English reader sees into
    # something other than the tool's own copy.
    for tool in tools:
        shown = _shown(tool, "en")
        assert shown, tool.name
        assert not _HANGUL.search(shown) and not _HAN.search(shown), tool.name
