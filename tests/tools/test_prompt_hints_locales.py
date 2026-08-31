"""Guards the per-locale tool prompt hints.

``load_prompt_hints`` reads ``tools/prompting/hints/<locale>/<tool>.yaml`` and
falls back to English when a locale ships none of its own. A translation that
misses a file — or a field inside one — silently degrades to English copy in
both the LLM prompt and the Settings → Tools page, so pin the parity here.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from deeptutor.tools.prompting import ToolPromptComposer, load_prompt_hints

_HINTS = Path(__file__).resolve().parents[2] / "deeptutor" / "tools" / "prompting" / "hints"
_EN = _HINTS / "en"

_TRANSLATIONS = sorted(d.name for d in _HINTS.iterdir() if d.is_dir() and d.name != "en")
_TOOLS = sorted(p.stem for p in _EN.glob("*.yaml"))


def _load(locale: str, tool: str) -> dict:
    return yaml.safe_load((_HINTS / locale / f"{tool}.yaml").read_text(encoding="utf-8")) or {}


def test_korean_hints_ship() -> None:
    assert "ko" in _TRANSLATIONS


@pytest.mark.parametrize("locale", _TRANSLATIONS)
def test_translation_covers_every_english_tool(locale: str) -> None:
    translated = sorted(p.stem for p in (_HINTS / locale).glob("*.yaml"))
    assert translated == _TOOLS


@pytest.mark.parametrize("locale", _TRANSLATIONS)
def test_translation_matches_english_shape(locale: str) -> None:
    for tool in _TOOLS:
        en, other = _load("en", tool), _load(locale, tool)
        assert set(en) == set(other), f"{locale}/{tool}: field mismatch"
        # ``phase`` is a lookup key for _PHASE_LABELS, not display copy.
        assert en["phase"] == other["phase"], f"{locale}/{tool}: phase must not be translated"
        for field in ("short_description", "when_to_use", "input_format"):
            assert other[field].strip(), f"{locale}/{tool}: {field} is empty"


def test_korean_hints_are_translated_not_echoed() -> None:
    for tool in _TOOLS:
        en, ko = _load("en", tool), _load("ko", tool)
        assert en["short_description"] != ko["short_description"], tool


def test_load_prompt_hints_returns_korean() -> None:
    hints = load_prompt_hints("web_search", "ko")

    assert hints.short_description == _load("ko", "web_search")["short_description"]
    assert hints.phase == "expansion"


def test_unknown_locale_falls_back_to_english() -> None:
    assert (
        load_prompt_hints("web_search", "fr").short_description
        == _load("en", "web_search")["short_description"]
    )


def test_composer_labels_follow_the_locale() -> None:
    hints = load_prompt_hints("web_search", "ko")
    rendered = ToolPromptComposer("ko").format_list_with_usage([("web_search", hints)])

    assert "사용 시점:" in rendered
    assert "입력 형식:" in rendered
    assert "When to use" not in rendered
