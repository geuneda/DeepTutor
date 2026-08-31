"""Starter suggestions — the three lines offered under the home composer.

What makes one of these worth showing is a jump, not a summary. The material
is a set of traces — a session titled "Agentic RAG retrieval flow", a quiz
question, a knowledge-base search. Restating a trace ("接着讲 Agentic RAG 的检索
流程") proposes nothing: the learner already knows they were there. Naming a
field ("探索一下检索") proposes nothing either. What earns the click is the
specific thing about that subject worth understanding next — "Agentic RAG 和
naive RAG 的检索差在哪". Same root, one step further.

So ``label`` is that proposal, and it names an idea, a distinction, a
mechanism or a question — never an activity. ``prompt`` is what gets *sent as
the learner's own message* when they click, so it is first-person, complete,
and pointed enough that answering it teaches something.

The jump has a floor: every proposal must be traceable to the material. One
step beyond what a trace literally says is the point; a subject with no root in
it is invention, and invention is worse than silence here.

Never on the request path
-------------------------
An LLM call is far too slow to sit between a click and a rendered page. So
reads are stale-while-revalidate: :func:`get_suggestions` returns whatever is
cached immediately — even if stale, even if empty — and schedules the work
behind the response. The next visit gets the new set.

Reading the cache is the *only* thing that happens synchronously: one small
JSON file. Deciding whether the material changed means walking seven surfaces,
which is cheap but not free, so that decision lives in the background task
too, throttled to at most once a minute per user.

When it regenerates
-------------------
The background pass regenerates when the material changed (a fingerprint over
the labels) or when the set is older than :data:`_TTL_SECONDS` — the first is
when the *content* should change, the second is so the same three lines do not
greet someone all week. A manual refresh bypasses both and generates
synchronously, because there a human is deliberately waiting.

Empty is a valid answer. A learner with no usable history gets no lines and no
LLM call, and the frontend renders nothing at all — generic copy in that slot
would teach people to stop reading it. But empty is only *cached* when it is
the right answer: an empty result produced despite having material is a
failure, and writing it would pin that failure in place for a whole TTL.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import hashlib
import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# How many starting points the home screen offers. One per line, so fewer than
# three reads as a stub and more turns the empty screen into a menu.
_COUNT = 3
# Long enough that the same three lines are not re-generated all afternoon,
# short enough to feel responsive to a day's work.
_TTL_SECONDS = 6 * 3600
# Floor between two background material checks for one user. Page loads can
# come in bursts (navigation, refresh, a second tab); the material cannot
# meaningfully change that fast.
_PROBE_INTERVAL_SECONDS = 60.0
_LLM_TIMEOUT = 25.0
# How far back a trace can be and still count as "what they are working on".
# A month rather than a week: labels are deduplicated and the list is cut to
# ``trace_count``, so a longer window means depth, not length — it means a
# learner who spent this week on one thing still has a history to draw on.
_LOOKBACK_DAYS = 30
# How much of L3 reaches the prompt. Generous — this is the consolidated read
# on the learner and the most useful half of the material — but bounded,
# because L3 grows without limit and this runs on a schedule.
_MAX_PROFILE_CHARS = 6000
# Below this a label carries no subject to propose anything about — a knowledge
# base named "q", a search for "q2", an untitled draft. They are real activity
# and recall is right to return them; they just cannot ground a suggestion, and
# left in they crowd out traces that can.
_MIN_TOPIC_CHARS = 3
# Titles a surface assigns before the learner (or the model) names the thing.
# They are the *newest* rows by definition — a conversation is created before
# it is titled — so without this they take the per-surface budget and leave the
# named work outside it. Mirrors ``DEFAULT_SESSION_TITLE`` in
# ``web/lib/session-title.ts``; drifting means one placeholder slips through,
# which costs a suggestion rather than breaking anything.
_PLACEHOLDER_LABELS = frozenset(
    {
        "new conversation",
        "new chat",
        "新对话",
        "untitled",
        "untitled draft",
        "无标题",
    }
)
# The line the learner reads, and the message behind it. Over-long output means
# the model ignored the brief; the item is dropped rather than truncated,
# because half a sentence is worse than one fewer starting point.
#
# These are per language because a character is not a unit of meaning. The same
# proposal is "LangGraph 中状态机与有向无环图的区别" (20 chars) or "How
# Self-Correction loops in LangGraph reduce pedagogical hallucinations" (72) —
# the same *line* on screen, three times the characters. A single bound set for
# one of them silently discards every well-formed answer in the other.
_MAX_LABEL_CHARS = {"zh": 40, "ko": 60, "en": 95}
_MAX_PROMPT_CHARS = {"zh": 160, "ko": 240, "en": 400}

# One in-flight regeneration per scope; a burst of page loads must not fan out
# into a burst of LLM calls.
_inflight: dict[str, asyncio.Task[Any]] = {}
# Last time a scope's material was checked, for the throttle above. In-process
# only: losing it on restart costs one extra walk.
_last_probe: dict[str, float] = {}


@dataclass(frozen=True, slots=True)
class Suggestion:
    """One starting point: what it says, and what it sends."""

    label: str
    prompt: str

    def to_dict(self) -> dict[str, str]:
        return {"label": self.label, "prompt": self.prompt}


@dataclass(frozen=True, slots=True)
class SuggestionSet:
    """The lines currently on offer, plus what they were generated from."""

    suggestions: tuple[Suggestion, ...]
    language: str
    generated_at: float
    fingerprint: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "suggestions": [item.to_dict() for item in self.suggestions],
            "language": self.language,
            "generated_at": self.generated_at,
            "fingerprint": self.fingerprint,
        }


# ── Cache ────────────────────────────────────────────────────────────────


def _cache_path():
    from deeptutor.services.path_service import get_path_service

    directory = get_path_service().get_workspace_dir() / "suggestions"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "starters.json"


def _scope_key() -> str:
    """Identifies whose suggestions these are.

    The cache path already resolves per user through the multi-user path
    service, so it doubles as the scope key for the in-flight and throttle
    maps — no separate notion of identity to keep in sync with the one that
    decides where the file lands.
    """
    try:
        return str(_cache_path())
    except Exception:  # pragma: no cover - defensive
        return "<unresolved>"


def _load() -> SuggestionSet | None:
    try:
        path = _cache_path()
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        items = tuple(
            Suggestion(label=str(item["label"]), prompt=str(item["prompt"]))
            for item in (raw.get("suggestions") or [])
            if isinstance(item, dict) and item.get("label") and item.get("prompt")
        )
        return SuggestionSet(
            suggestions=items,
            language=str(raw.get("language") or "en"),
            generated_at=float(raw.get("generated_at") or 0.0),
            fingerprint=str(raw.get("fingerprint") or ""),
        )
    except Exception:
        logger.debug("suggestions cache unreadable", exc_info=True)
        return None


def _save(value: SuggestionSet) -> None:
    try:
        path = _cache_path()
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(value.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(path)
    except Exception:
        logger.debug("suggestions cache unwritable", exc_info=True)


# ── Settings ─────────────────────────────────────────────────────────────


def _output_language() -> str:
    """The language these lines are written in.

    The learner's model-output setting (Settings → Appearance), the same one
    that decides what the chat agent answers in — not the UI locale. A chip
    proposing something to ask should read like the answer it will get.
    """
    try:
        from deeptutor.services.settings.interface_settings import get_response_language

        return get_response_language(default="en")
    except Exception:
        logger.debug("suggestions: response language unreadable", exc_info=True)
        return "en"


def _trace_count() -> int:
    """How many recent activities to show the model (Settings → Chat)."""
    from deeptutor.services.settings.starter_settings import (
        DEFAULT_TRACE_COUNT,
        get_starter_settings,
    )

    try:
        return int(get_starter_settings()["trace_count"])
    except Exception:
        logger.debug("suggestions: starter settings unreadable", exc_info=True)
        return DEFAULT_TRACE_COUNT


# ── Material ─────────────────────────────────────────────────────────────

# What each surface is called when it is described to the model. Deliberately
# the learner's vocabulary, not the codebase's: "错题" is a thing a learner
# recognises, "quiz surface" is not.
_SURFACE_LABELS_EN: dict[str, str] = {
    "chat": "conversation",
    "quiz": "practice question",
    "notebook": "note",
    "kb": "knowledge base",
    "book": "book",
    "cowriter": "document",
    "partner": "conversation",
}
_SURFACE_LABELS_KO: dict[str, str] = {
    "chat": "대화",
    "quiz": "연습 문제",
    "notebook": "노트",
    "kb": "지식 베이스",
    "book": "책",
    "cowriter": "문서",
    "partner": "대화",
}
_SURFACE_LABELS_ZH: dict[str, str] = {
    "chat": "对话",
    "quiz": "错题",
    "notebook": "笔记",
    "kb": "知识库",
    "book": "书",
    "cowriter": "文档",
    "partner": "对话",
}


@dataclass(frozen=True, slots=True)
class _Topic:
    surface: str
    label: str
    days_ago: int | None


@dataclass(frozen=True, slots=True)
class _Material:
    """Everything the model is given: who this learner is, and what they did.

    Two halves that answer different questions. ``profile`` is L3 — the
    consolidated read on this learner, including which topics they are still
    unsure about, which is the single most useful thing to know when proposing
    what to look at next. ``topics`` is raw recent activity, which is what
    keeps a proposal anchored to something that actually happened.
    """

    profile: str
    topics: list[_Topic]

    def __bool__(self) -> bool:
        return bool(self.profile or self.topics)


# L3 slots, most useful first. Order decides who gets the character budget when
# the documents outgrow it: ``preferences`` is tiny and absolute, ``scope``
# carries the familiar/practising/unsure split that this whole feature is
# reaching for, and ``recent`` goes last because the trace list below already
# says what happened lately, in more detail.
_L3_ORDER = ("preferences", "scope", "profile", "recent")


def _render_l3(cap: int) -> str:
    """L3 as the model should read it: sections and bullets, no citations.

    Reads through :class:`~deeptutor.services.memory.store.MemoryStore`'s
    parser rather than the raw markdown, so footnote markers and their HTML
    comments — which are addressing machinery, not content — never reach the
    prompt.

    Section names are deliberately passed through untranslated. They are
    written by the consolidator in the deployment's own language ("不确定" /
    "Unsure"), and reading them is exactly the model's job; a lookup table here
    would be a second place for that vocabulary to drift.
    """
    from deeptutor.services.memory import get_memory_store

    try:
        store = get_memory_store()
    except Exception:
        logger.debug("suggestions: memory store unavailable", exc_info=True)
        return ""

    per_slot = max(1, cap // len(_L3_ORDER))
    carry = 0
    blocks: list[str] = []
    for slot in _L3_ORDER:
        try:
            doc = store.read_doc("L3", slot)
        except Exception:
            logger.debug("suggestions: L3 %s unreadable", slot, exc_info=True)
            continue
        budget = per_slot + carry
        lines: list[str] = []
        used = 0
        for section, entries in doc.sections:
            head = f"### {section}"
            if used + len(head) > budget:
                break
            lines.append(head)
            used += len(head)
            for entry in entries:
                text = " ".join(entry.text.split())
                if not text:
                    continue
                bullet = f"- {text}"
                if used + len(bullet) > budget:
                    break
                lines.append(bullet)
                used += len(bullet)
        # Carry the unspent budget forward: preferences is a line or two, and
        # its leftover is what lets scope be shown in full.
        carry = budget - used
        if lines:
            blocks.append(f"## {doc.title or slot}\n" + "\n".join(lines))
    return "\n\n".join(blocks)


def _collect_material(trace_count: int) -> _Material:
    """L3 plus the most recent *trace_count* activities, newest first.

    The traces are deliberately flat — one list across every surface, ordered
    by time alone. What a learner touched most recently is the best signal for
    what they are in the middle of, and which surface it happened on says
    nothing about that.
    """
    from deeptutor.services.memory import recall

    seen: set[str] = set()
    topics: list[_Topic] = []

    def _add(hit) -> None:
        label = hit.label.strip()
        if len(label) < _MIN_TOPIC_CHARS or label.casefold() in _PLACEHOLDER_LABELS:
            return
        if label.casefold() in seen:
            return
        seen.add(label.casefold())
        topics.append(_Topic(surface=hit.surface, label=label, days_ago=hit.days_ago))

    hits = []
    for source, kwargs in (
        (recall.recent, {"days": _LOOKBACK_DAYS, "limit": trace_count * 3}),
        (recall.recent_queries, {"days": _LOOKBACK_DAYS, "limit": trace_count}),
    ):
        try:
            hits.extend(source(**kwargs))
        except Exception:
            logger.debug("suggestions: %s failed", source.__name__, exc_info=True)

    # One ordering across everything, then take the head. Over-fetching above
    # is what makes the cut meaningful: filtering after a limit would let a run
    # of placeholder titles eat the whole allowance.
    hits.sort(key=lambda hit: (hit.ts != "", hit.ts), reverse=True)
    for hit in hits:
        if len(topics) >= trace_count:
            break
        _add(hit)

    return _Material(profile=_render_l3(_MAX_PROFILE_CHARS), topics=topics)


def _fingerprint(material: _Material, language: str) -> str:
    digest = hashlib.sha1(usedforsecurity=False)
    digest.update(language.encode("utf-8"))
    digest.update(material.profile.encode("utf-8"))
    for topic in material.topics:
        digest.update(b"\0")
        digest.update(f"{topic.surface}:{topic.label}".encode("utf-8"))
    return digest.hexdigest()[:16]


# ── Generation ───────────────────────────────────────────────────────────


_SYSTEM_EN = """You propose the three things a learner should explore next. Each is one line they click to begin.

You are given traces of what they have been working on — conversations, practice questions, searches, documents. Your job is to see the *subject* behind those traces and name something specific about it that is worth understanding.

Each proposal is an object with two fields:
- "label": the line they read. 4 to 10 words, no ending punctuation. It names a specific idea, distinction, mechanism or question — never an activity.
- "prompt": the message sent as the learner's own words when they click. First person, complete, and pointed enough that a good answer teaches them something.

The move you are making, in one example:
  Trace: [conversation, 2d ago] Agentic RAG retrieval flow
  GOOD: "How agentic RAG differs from naive RAG"
  BAD:  "Continue the Agentic RAG conversation"  <- restates the trace; proposes nothing to understand
  BAD:  "Explore retrieval"                      <- names a field, not a question

Other good shapes: "Why the chain rule underlies backpropagation" / "Where self-attention beats a plain RNN" / "What an eigenvalue actually measures" / "When BM25 still beats embeddings"

Rules:
- Reply with ONLY a JSON array of exactly 3 such objects. No prose, no markdown fence.
- Every proposal must be traceable to the material below. Going one step beyond what it literally says is the point — but never introduce a subject with no root in it.
- The material is raw activity and some of it is noise: a scratch file, a one-word search, a conversation that went nowhere. Skip those and build on the traces that carry a real subject. Three proposals from two good traces beat three that include one about "hello".
- Make the three differ: different subjects from the material, and different kinds of question (a distinction, a mechanism, a why, a boundary case).
- No greetings, no emoji, no quotes around the fields' text."""

_SYSTEM_ZH = """你要提出三个"接下来值得探索什么"。每一个都是一行字，学习者点一下就开始。

给你的是这个学习者最近留下的痕迹——对话、错题、检索、文档。你要做的是：看出这些痕迹背后是什么**学科内容**，然后点出关于它的、一个具体的、值得搞懂的东西。

每一个是一个对象，含两个字段：
- "label"：学习者读到的那行字。8 到 20 个字，结尾不加标点。它点出的是一个具体的概念、区别、机制或问题，绝不是一类活动。
- "prompt"：学习者点击后以自己的身份发出的那句话。第一人称、完整、问得足够到位，好的回答能让他真的学到东西。

你要做的这个跃迁，看一个例子：
  痕迹：[对话，2 天前] Agentic RAG 的检索流程
  好："Agentic RAG 和 naive RAG 的检索差在哪"
  差："接着讲 Agentic RAG 的检索流程"  <- 只是把痕迹复述一遍，没提出任何要搞懂的东西
  差："探索一下检索"                    <- 说的是一个领域，不是一个问题

其他好的形态："为什么链式法则是反向传播的基础" / "自注意力比 RNN 强在哪一步" / "特征值到底在度量什么" / "什么时候 BM25 反而比向量检索准"

规则：
- 只回复一个 JSON 数组，正好 3 个这样的对象。不要有任何解释文字，不要 markdown 代码块。
- 每一个都必须能追溯到下面的素材。比素材字面上说的**多走一步**正是要点——但绝不能引入素材里毫无根据的话题。
- 素材是原始活动记录，其中有噪音：随手建的文件、一个词的检索、没聊起来的对话。跳过它们，只在真正有内容的痕迹上做文章。宁可三个都从两条好素材里长出来，也不要有一个是关于 "hello" 的。
- 三个之间要有区别：取素材里不同的内容，也问不同类型的问题（一个区别、一个机制、一个为什么、一个边界情况）。
- 不要问候语、不要 emoji、字段文本里不要加引号。"""


_SYSTEM_KO = """당신은 학습자가 다음에 살펴볼 만한 것 세 가지를 제안합니다. 각각은 클릭 한 번으로 시작되는 한 줄입니다.

학습자가 최근 남긴 흔적(대화, 연습 문제, 검색, 문서)이 주어집니다. 당신이 할 일은 그 흔적 뒤에 있는 *주제*를 알아보고, 그에 대해 이해할 가치가 있는 구체적인 무언가를 짚어내는 것입니다.

각 제안은 두 필드를 가진 객체입니다:
- "label": 학습자가 읽는 한 줄. 15~35자 사이, 끝에 문장 부호를 붙이지 않습니다. 구체적인 개념, 구분, 원리, 질문을 짚어야 하며 활동의 종류를 가리켜서는 안 됩니다.
- "prompt": 클릭했을 때 학습자 본인의 말로 전송되는 메시지. 1인칭이며, 완결되어 있고, 좋은 답변이 실제로 배움이 될 만큼 날카로워야 합니다.

당신이 해야 할 도약을 예로 들면:
  흔적: [대화, 2일 전] Agentic RAG 검색 흐름
  좋음: "Agentic RAG와 단순 RAG의 검색 방식 차이"
  나쁨: "Agentic RAG 대화 이어가기"   <- 흔적을 다시 말할 뿐, 이해할 거리를 제시하지 않음
  나쁨: "검색에 대해 살펴보기"        <- 분야를 가리킬 뿐 질문이 아님

다른 좋은 형태: "연쇄 법칙이 역전파의 바탕인 이유" / "셀프 어텐션이 RNN을 앞서는 지점" / "고윳값이 실제로 재는 것" / "BM25가 임베딩보다 나은 경우"

규칙:
- 정확히 3개의 객체로 이루어진 JSON 배열만 응답합니다. 설명 문장도, 마크다운 코드 블록도 넣지 않습니다.
- 모든 제안은 아래 자료에서 추적 가능해야 합니다. 자료가 문자 그대로 말하는 것에서 한 걸음 더 나아가는 것이 핵심이지만, 자료에 근거가 없는 주제를 끌어들여서는 안 됩니다.
- 자료는 원본 활동 기록이며 일부는 잡음입니다: 임시 파일, 한 단어짜리 검색, 이어지지 않은 대화. 그런 것은 건너뛰고 실제 주제가 담긴 흔적 위에 쌓으세요. 좋은 흔적 두 개에서 나온 제안 셋이, "hello" 같은 것을 포함한 셋보다 낫습니다.
- 세 제안은 서로 달라야 합니다: 자료 안의 다른 주제, 그리고 다른 종류의 질문(구분, 원리, 이유, 경계 사례).
- 인사말, 이모지, 필드 텍스트를 감싸는 따옴표는 넣지 않습니다."""


_SYSTEMS = {"en": _SYSTEM_EN, "zh": _SYSTEM_ZH, "ko": _SYSTEM_KO}

# Section headings and the closing line of the user prompt, per locale.
_PROFILE_HEADING = {
    "en": "# What is known about this learner\n",
    "zh": "# 关于这个学习者（长期记忆）\n",
    "ko": "# 이 학습자에 대해 알려진 것(장기 메모리)\n",
}
_ACTIVITY_HEADING = {
    "en": "# Recent activity\n",
    "zh": "# 最近的活动痕迹\n",
    "ko": "# 최근 활동 흔적\n",
}
_CLOSING = {
    "en": "\nPropose the three things worth exploring next.",
    "zh": "\n请提出那三个探索方向。",
    "ko": "\n다음에 살펴볼 만한 세 가지를 제안하세요.",
}


def _lang(language: str) -> str:
    """The locale whose copy these lines are written in — en unless we ship it."""
    raw = str(language or "en").lower()
    if raw.startswith("zh"):
        return "zh"
    if raw.startswith("ko"):
        return "ko"
    return "en"


_SURFACE_LABELS = {
    "en": _SURFACE_LABELS_EN,
    "zh": _SURFACE_LABELS_ZH,
    "ko": _SURFACE_LABELS_KO,
}


def _when(days_ago: int, lang: str) -> str:
    if lang == "zh":
        return "，今天" if days_ago == 0 else f"，{days_ago} 天前"
    if lang == "ko":
        return ", 오늘" if days_ago == 0 else f", {days_ago}일 전"
    return ", today" if days_ago == 0 else f", {days_ago}d ago"


def _render_topics(topics: list[_Topic], lang: str) -> str:
    labels = _SURFACE_LABELS.get(lang, _SURFACE_LABELS_EN)
    lines: list[str] = []
    for topic in topics:
        kind = labels.get(topic.surface, topic.surface)
        when = "" if topic.days_ago is None else _when(topic.days_ago, lang)
        lines.append(f"- [{kind}{when}] {topic.label}")
    return "\n".join(lines)


def _bound(table: dict[str, int], language: str) -> int:
    return table.get(_lang(language), table["en"])


def _sanitize(raw: str, language: str = "en") -> tuple[Suggestion, ...]:
    """Exactly :data:`_COUNT` usable lines, or nothing at all.

    Partial output is discarded rather than shown: one lonely line under the
    composer reads as a rendering bug, and rendering nothing is the honest
    alternative.

    The length bounds are per language — see :data:`_MAX_LABEL_CHARS`. Applying
    a CJK-sized bound to English silently rejects every well-formed answer,
    which looks exactly like the model failing.
    """
    from deeptutor.utils.json_parser import parse_json_response

    decoded = parse_json_response(raw, fallback=None)
    if not isinstance(decoded, list):
        return ()

    max_label = _bound(_MAX_LABEL_CHARS, language)
    max_prompt = _bound(_MAX_PROMPT_CHARS, language)
    items: list[Suggestion] = []
    seen: set[str] = set()
    for entry in decoded:
        if not isinstance(entry, dict):
            continue
        label = " ".join(str(entry.get("label") or "").split()).strip("\"'“”‘’ ")
        prompt = " ".join(str(entry.get("prompt") or "").split()).strip("\"'“”‘’ ")
        if not label or not prompt:
            continue
        if len(label) > max_label or len(prompt) > max_prompt:
            continue
        if label.casefold() in seen:
            continue
        seen.add(label.casefold())
        items.append(Suggestion(label=label, prompt=prompt))

    return tuple(items[:_COUNT]) if len(items) >= _COUNT else ()


async def _generate(language: str, material: _Material) -> SuggestionSet:
    """Build a fresh set from *material*. Always returns one — empty on failure.

    Takes the material rather than collecting it, so one pass reads memory once
    and every downstream decision — the fingerprint, whether an empty result is
    meaningful — is made about the same snapshot.
    """
    fingerprint = _fingerprint(material, language)
    empty = SuggestionSet(
        suggestions=(),
        language=language,
        generated_at=time.time(),
        fingerprint=fingerprint,
    )
    if not material:
        # Nothing to ground a suggestion in. Say so instead of asking a model
        # to invent a learning history.
        return empty

    lang = _lang(language)
    sections: list[str] = []
    if material.profile:
        sections.append(_PROFILE_HEADING.get(lang, _PROFILE_HEADING["en"]) + material.profile)
    if material.topics:
        sections.append(
            _ACTIVITY_HEADING.get(lang, _ACTIVITY_HEADING["en"])
            + _render_topics(material.topics, lang)
        )
    closing = _CLOSING.get(lang, _CLOSING["en"])
    user_prompt = "\n\n".join(sections) + "\n" + closing

    try:
        from deeptutor.services.llm import complete

        raw = await asyncio.wait_for(
            complete(
                prompt=user_prompt,
                system_prompt=_SYSTEMS.get(lang, _SYSTEM_EN),
                temperature=0.8,  # suggestions may vary; these are not facts
                max_tokens=500,
            ),
            timeout=_LLM_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logger.debug("suggestions LLM call timed out")
        return empty
    except Exception:
        logger.debug("suggestions LLM call failed", exc_info=True)
        return empty

    return SuggestionSet(
        suggestions=_sanitize(raw, language),
        language=language,
        generated_at=time.time(),
        fingerprint=fingerprint,
    )


# ── Public API ───────────────────────────────────────────────────────────


def _is_fresh(cached: SuggestionSet | None, language: str, *, now: float) -> bool:
    return (
        cached is not None
        and cached.language == language
        and now - cached.generated_at <= _TTL_SECONDS
    )


async def _generate_and_cache(language: str, material: _Material) -> SuggestionSet:
    """Generate from *material* and cache the result — unless it is a failure.

    An empty result is only written when it is the *right* answer: there was no
    material to work from, and saying so costs nothing to repeat. An empty
    result produced *despite* having material means the call failed or the
    model ignored the brief, and writing that would pin the failure in place
    for a full TTL — the fingerprint would keep matching, so the background
    pass would see nothing due and never retry. Those are dropped instead, and
    the next visit tries again.
    """
    value = await _generate(language, material)
    if value.suggestions or not material:
        _save(value)
    return value


async def refresh_suggestions() -> SuggestionSet:
    """Generate a new set now and cache it. For the manual reroll."""
    language = _output_language()
    return await _generate_and_cache(language, _collect_material(_trace_count()))


async def _regenerate_if_due() -> None:
    """The background pass: work out whether anything is due, then do it.

    Reading memory to fingerprint the material happens here rather than on the
    request path — the answer only decides whether to spend an LLM call, and
    acting on it one page load later is exactly what stale-while-revalidate
    means.
    """
    language = _output_language()
    material = _collect_material(_trace_count())
    fingerprint = _fingerprint(material, language)
    cached = _load()
    if _is_fresh(cached, language, now=time.time()) and cached.fingerprint == fingerprint:
        return
    await _generate_and_cache(language, material)


def _schedule_probe(*, force: bool = False) -> None:
    """Check (and maybe regenerate) in the background, throttled and deduped.

    ``force`` skips the interval, not the in-flight guard. The throttle exists
    because page loads arrive in bursts and the material rarely changes between
    them — but when the caller already *knows* the cached set is unusable (the
    output language was just changed), waiting out the interval means up to a
    minute of empty screen with nothing working to fill it.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    key = _scope_key()
    now = time.monotonic()
    pending = _inflight.get(key)
    if pending is not None and not pending.done():
        return
    if not force and now - _last_probe.get(key, 0.0) < _PROBE_INTERVAL_SECONDS:
        return
    _last_probe[key] = now

    async def _go() -> None:
        try:
            await _regenerate_if_due()
        except Exception:
            logger.debug("background suggestion refresh failed", exc_info=True)
        finally:
            if _inflight.get(key) is task:
                _inflight.pop(key, None)

    task = loop.create_task(_go())
    _inflight[key] = task


async def get_suggestions() -> dict[str, Any]:
    """The lines to show now, plus whether a fresher set is being made.

    Returns immediately, reading one small JSON file. An empty list is a real
    answer — a learner with nothing in memory has nothing to suggest from — and
    ``stale`` tells the caller whether it is worth looking again shortly.

    Takes no language: the output language is the learner's own model-output
    setting, read here. A caller-supplied language would let the UI's own
    locale — which can resolve before the user's settings load — decide what a
    model writes, and with one cache per user the two would overwrite each
    other on every visit.
    """
    language = _output_language()
    cached = _load()
    fresh = _is_fresh(cached, language, now=time.time())
    # A cache in another language is not stale, it is unusable: the learner
    # just changed the setting and is looking at an empty slot right now.
    _schedule_probe(force=cached is not None and cached.language != language)

    if cached is not None and cached.language == language:
        return {**cached.to_dict(), "stale": not fresh}
    return {
        "suggestions": [],
        "language": language,
        "generated_at": 0.0,
        "fingerprint": "",
        "stale": True,
    }


__all__ = [
    "Suggestion",
    "SuggestionSet",
    "get_suggestions",
    "refresh_suggestions",
]
