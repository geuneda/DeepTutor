"""Localized display metadata for built-in tools and capabilities."""

from __future__ import annotations

_CAPABILITY_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "chat": {
        "en": "Default agentic chat with tools, retrieval, memory, and attachments.",
        "zh": "默认智能聊天，支持工具、检索、记忆和附件。",
        "ko": "도구, 검색, 메모리, 첨부 파일을 지원하는 기본 에이전트 채팅입니다.",
    },
    "deep_solve": {
        "en": "Multi-step problem solving with planning, reasoning, and final writing.",
        "zh": "多步骤解题，包含规划、推理和最终作答。",
        "ko": "계획, 추론, 최종 작성까지 아우르는 다단계 문제 풀이입니다.",
    },
    "deep_question": {
        "en": "Generate high-quality questions from templates, sources, or learning goals.",
        "zh": "基于模板、资料或学习目标生成高质量题目。",
        "ko": "템플릿, 자료, 학습 목표를 바탕으로 완성도 높은 문제를 생성합니다.",
    },
    "deep_research": {
        "en": "Iterative deep research that decomposes a topic and writes a report.",
        "zh": "迭代式深度研究，分解主题并生成研究报告。",
        "ko": "주제를 분해하고 리포트를 작성하는 반복적 심층 리서치입니다.",
    },
    "math_animator": {
        "en": "Generate math animations or storyboard images with Manim.",
        "zh": "使用 Manim 生成数学动画或分镜图。",
        "ko": "Manim으로 수학 애니메이션이나 스토리보드 이미지를 만듭니다.",
    },
    "mastery_path": {
        "en": "Structured mastery-based learning with spaced repetition.",
        "zh": "结构化掌握式学习，结合间隔复习。",
        "ko": "간격 반복을 곁들인 숙달 기반 체계적 학습입니다.",
    },
    "visualize": {
        "en": "Create visual explanations such as SVG, charts, Mermaid, HTML, or Manim.",
        "zh": "生成 SVG、图表、Mermaid、HTML 或 Manim 等可视化讲解。",
        "ko": "SVG, 차트, Mermaid, HTML, Manim 같은 시각적 설명을 만듭니다.",
    },
    "immersive_reading": {
        "en": "Read a document with the assistant, cited page by page.",
        "zh": "与助手一起阅读文档，逐页标明出处。",
        "ko": "어시스턴트와 함께 문서를 읽으며 페이지마다 출처를 밝힙니다.",
    },
}

_TOOL_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "brainstorm": {
        "en": "Explore ideas broadly and organize them with rationale.",
        "zh": "广泛发散想法，并按理由组织结果。",
        "ko": "아이디어를 폭넓게 펼치고 근거에 따라 정리합니다.",
    },
    "code_execution": {
        "en": "Run sandboxed Python code for computation and data exploration.",
        "zh": "在沙箱中运行 Python，用于计算和数据探索。",
        "ko": "계산과 데이터 탐색을 위해 샌드박스에서 Python을 실행합니다.",
    },
    "exec": {
        "en": "Run shell commands inside an isolated sandbox workspace.",
        "zh": "在隔离沙箱工作区中运行 shell 命令。",
        "ko": "격리된 샌드박스 워크스페이스에서 셸 명령을 실행합니다.",
    },
    "kb_files": {
        "en": "List the documents a knowledge base holds, with the total count.",
        "zh": "列出知识库中的文档清单与总数。",
        "ko": "지식 베이스가 담고 있는 문서 목록과 총 개수를 보여줍니다.",
    },
    "paper_search": {
        "en": "Search arXiv preprints and return paper metadata.",
        "zh": "搜索 arXiv 预印本并返回论文元数据。",
        "ko": "arXiv 프리프린트를 검색해 논문 정보를 반환합니다.",
    },
    "reason": {
        "en": "Use a dedicated reasoning model call for hard reasoning tasks.",
        "zh": "调用专门的推理模型处理高难度推理任务。",
        "ko": "어려운 추론 과제를 전용 추론 모델 호출로 처리합니다.",
    },
    "web_search": {
        "en": "Search the web and return sourced results.",
        "zh": "联网搜索并返回带来源的结果。",
        "ko": "웹을 검색해 출처가 있는 결과를 반환합니다.",
    },
    "imagegen": {
        "en": "Generate images from a text prompt with the configured model.",
        "zh": "用已配置的模型，根据文字描述生成图片。",
        "ko": "설정된 모델로 텍스트 설명에서 이미지를 생성합니다.",
    },
    "videogen": {
        "en": "Generate short videos from a text prompt with the configured model.",
        "zh": "用已配置的模型，根据文字描述生成短视频。",
        "ko": "설정된 모델로 텍스트 설명에서 짧은 영상을 생성합니다.",
    },
    "cron": {
        "en": "Schedule a task to run later, list scheduled tasks, or cancel one.",
        "zh": "安排任务稍后运行、查看已排期任务或取消其中一个。",
        "ko": "작업을 나중에 실행하도록 예약하고, 예약된 작업을 확인하거나 취소합니다.",
    },
    "mastery_quiz": {
        "en": "Pose a mastery-path question and register its expected answer.",
        "zh": "为掌握路径出题，并登记预期答案。",
        "ko": "숙달 경로 문제를 내고 예상 답안을 등록합니다.",
    },
    "mastery_grade": {
        "en": "Grade the learner's answer against the registered expected answer.",
        "zh": "对照已登记的预期答案批改学习者的作答。",
        "ko": "등록된 예상 답안과 대조해 학습자의 답을 채점합니다.",
    },
    "mastery_build": {
        "en": "Create or extend the learner's mastery path from their materials.",
        "zh": "根据学习者的材料创建或扩展掌握路径。",
        "ko": "학습자의 자료를 바탕으로 숙달 경로를 만들거나 확장합니다.",
    },
    "mastery_leave": {
        "en": "Stop following the current mastery path; progress is kept.",
        "zh": "退出当前掌握路径，进度会保留。",
        "ko": "현재 숙달 경로를 중단합니다. 진행 상황은 그대로 유지됩니다.",
    },
    "solve_plan": {
        "en": "Lay out an ordered plan before working a problem.",
        "zh": "在动手解题前列出有序的解题计划。",
        "ko": "문제를 풀기 전에 순서가 있는 계획을 세웁니다.",
    },
    "obsidian_search": {
        "en": "Search the Obsidian vault for notes matching a query.",
        "zh": "在 Obsidian 仓库中检索匹配的笔记。",
        "ko": "Obsidian 볼트에서 질의와 일치하는 노트를 검색합니다.",
    },
    "obsidian_read": {
        "en": "Read a note from the Obsidian vault by name or path.",
        "zh": "按名称或路径读取 Obsidian 仓库中的一篇笔记。",
        "ko": "이름이나 경로로 Obsidian 볼트의 노트를 읽습니다.",
    },
    "obsidian_list": {
        "en": "List note paths in the vault, optionally within a folder.",
        "zh": "列出仓库中的笔记路径，可限定某个文件夹。",
        "ko": "볼트의 노트 경로를 나열합니다. 폴더로 범위를 좁힐 수 있습니다.",
    },
    "obsidian_links": {
        "en": "List the notes a given note links out to.",
        "zh": "列出某篇笔记链出的其他笔记。",
        "ko": "특정 노트가 링크로 가리키는 노트를 나열합니다.",
    },
    "obsidian_tags": {
        "en": "List every tag used across the vault, ranked by use.",
        "zh": "按使用量列出仓库中的全部标签。",
        "ko": "볼트 전체에서 쓰인 태그를 사용 빈도순으로 나열합니다.",
    },
    "obsidian_create_note": {
        "en": "Create a new note in the Obsidian vault.",
        "zh": "在 Obsidian 仓库中新建一篇笔记。",
        "ko": "Obsidian 볼트에 새 노트를 만듭니다.",
    },
    "obsidian_append": {
        "en": "Append Markdown to the end of an existing note.",
        "zh": "在已有笔记末尾追加 Markdown 内容。",
        "ko": "기존 노트 끝에 마크다운을 덧붙입니다.",
    },
    "obsidian_set_property": {
        "en": "Set one frontmatter property on an existing note.",
        "zh": "为已有笔记设置一个 frontmatter 属性。",
        "ko": "기존 노트의 프론트매터 속성 하나를 설정합니다.",
    },
    "marginnote_search": {
        "en": "Search the MarginNote 4 library for matching objects.",
        "zh": "在 MarginNote 4 库中检索匹配的内容。",
        "ko": "MarginNote 4 라이브러리에서 일치하는 항목을 검색합니다.",
    },
    "marginnote_read": {
        "en": "Read one MarginNote 4 object in full by its ID.",
        "zh": "按 ID 读取某个 MarginNote 4 对象的完整内容。",
        "ko": "ID로 MarginNote 4 항목 하나의 전체 내용을 읽습니다.",
    },
    "marginnote_list": {
        "en": "List MarginNote 4 objects, filtered by type or document.",
        "zh": "列出 MarginNote 4 对象，可按类型或来源文档筛选。",
        "ko": "MarginNote 4 항목을 유형이나 원본 문서로 걸러 나열합니다.",
    },
    "marginnote_documents": {
        "en": "List the source documents in the MarginNote library.",
        "zh": "列出 MarginNote 库中的来源文档。",
        "ko": "MarginNote 라이브러리의 원본 문서를 나열합니다.",
    },
    "marginnote_links": {
        "en": "Find MarginNote objects linked to or from a given one.",
        "zh": "查找与指定 MarginNote 对象互相链接的对象。",
        "ko": "특정 MarginNote 항목과 연결된 항목을 찾습니다.",
    },
    "marginnote_tags": {
        "en": "List every tag in the MarginNote library, ranked by use.",
        "zh": "按使用量列出 MarginNote 库中的全部标签。",
        "ko": "MarginNote 라이브러리의 태그를 사용 빈도순으로 나열합니다.",
    },
    "marginnote_cards": {
        "en": "List flashcards in the MarginNote library.",
        "zh": "列出 MarginNote 库中的闪卡。",
        "ko": "MarginNote 라이브러리의 플래시 카드를 나열합니다.",
    },
    "ima_read": {
        "en": "Read one item in full from a connected Tencent IMA knowledge base.",
        "zh": "从已连接的腾讯 IMA 知识库中读取某一条目的全文。",
        "ko": "연결된 Tencent IMA 지식 베이스에서 항목 하나의 전문을 읽습니다.",
    },
    "ima_note_search": {
        "en": "Search Tencent IMA notes, or list them newest-first.",
        "zh": "检索腾讯 IMA 笔记，或按时间倒序列出。",
        "ko": "Tencent IMA 노트를 검색하거나 최신순으로 나열합니다.",
    },
    "search_material": {
        "en": "Search the full text of the document the user is reading.",
        "zh": "全文检索用户正在阅读的文档。",
        "ko": "사용자가 읽고 있는 문서의 전문을 검색합니다.",
    },
    "read_material": {
        "en": "Read exact parts of the document the user is reading, by locator.",
        "zh": "按定位读取用户正在阅读文档的指定部分原文。",
        "ko": "위치를 지정해 사용자가 읽고 있는 문서의 해당 부분 원문을 읽습니다.",
    },
    "request_credential": {
        "en": "Ask the user for an API key or token through a secure prompt.",
        "zh": "通过安全提示向用户索取 API 密钥或令牌。",
        "ko": "안전한 입력 창을 통해 사용자에게 API 키나 토큰을 요청합니다.",
    },
    "partner_search": {
        "en": "Search your past conversations with this person by keyword.",
        "zh": "按关键词检索与该用户的历史对话。",
        "ko": "이 사람과 나눈 지난 대화를 키워드로 검색합니다.",
    },
    "mastery_status": {
        "en": "Read the learner's mastery path: what to work on next and every objective's status.",
        "zh": "读取学习者的掌握路径：下一步该做什么，以及每个目标的状态。",
        "ko": "학습자의 숙달 경로를 확인합니다: 다음에 할 것과 각 목표의 상태.",
    },
    "mastery_assess": {
        "en": "Record a judgement on a concept or design objective after a Feynman-style explanation.",
        "zh": "在学习者用自己的话讲解后，记录对概念或设计类目标的判定。",
        "ko": "학습자가 자기 말로 설명한 뒤 개념·설계 목표에 대한 판정을 기록합니다.",
    },
    "mastery_paths": {
        "en": "List every mastery path this learner has, with progress and due reviews.",
        "zh": "列出该学习者的所有掌握路径，含进度与待复习项。",
        "ko": "학습자의 모든 숙달 경로를 진행 상황·복습 예정과 함께 나열합니다.",
    },
    "mastery_switch": {
        "en": "Move this conversation onto a different mastery path.",
        "zh": "把当前对话切换到另一条掌握路径。",
        "ko": "이 대화를 다른 숙달 경로로 옮깁니다.",
    },
    "solve_finish_step": {
        "en": "Mark the current solving step done and move on to the next.",
        "zh": "标记当前解题步骤完成并进入下一步。",
        "ko": "현재 풀이 단계를 완료로 표시하고 다음으로 넘어갑니다.",
    },
    "solve_replan": {
        "en": "Replace the solving plan when the current approach has stalled.",
        "zh": "当前思路走不通时，重新制定解题计划。",
        "ko": "지금 접근이 막혔을 때 풀이 계획을 새로 세웁니다.",
    },
    "obsidian_backlinks": {
        "en": "Find the notes that link to a given note.",
        "zh": "查找链接到指定笔记的其他笔记。",
        "ko": "특정 노트를 가리키는 노트를 찾습니다.",
    },
    "consult_subagent": {
        "en": "Ask a connected external agent and stream back its full run.",
        "zh": "向已连接的外部智能体提问，并实时回传其完整运行过程。",
        "ko": "연결된 외부 에이전트에게 묻고 실행 과정 전체를 실시간으로 받아옵니다.",
    },
    "ima_list": {
        "en": "List what a connected Tencent IMA knowledge base holds.",
        "zh": "列出已连接的腾讯 IMA 知识库中的内容。",
        "ko": "연결된 Tencent IMA 지식 베이스에 담긴 내용을 나열합니다.",
    },
    "ima_add_url": {
        "en": "Add web pages or articles to a connected Tencent IMA knowledge base.",
        "zh": "把网页或文章添加到已连接的腾讯 IMA 知识库。",
        "ko": "웹 페이지나 글을 연결된 Tencent IMA 지식 베이스에 추가합니다.",
    },
    "ima_write_note": {
        "en": "Write a Markdown note into the user's Tencent IMA account.",
        "zh": "在用户的腾讯 IMA 账号中写入一条 Markdown 笔记。",
        "ko": "사용자의 Tencent IMA 계정에 마크다운 노트를 작성합니다.",
    },
    "material_outline": {
        "en": "Show the structure of the document the user is reading.",
        "zh": "展示用户正在阅读文档的结构。",
        "ko": "사용자가 읽고 있는 문서의 구조를 보여줍니다.",
    },
    "reader_goto": {
        "en": "Scroll the user's reader to a locator and highlight it.",
        "zh": "把用户的阅读器滚动到指定位置并高亮。",
        "ko": "사용자의 리더를 지정한 위치로 이동시키고 강조 표시합니다.",
    },
    "reader_annotate": {
        "en": "Mark a passage in the user's document, with an optional note.",
        "zh": "在用户的文档中标记一段内容，可附加备注。",
        "ko": "사용자의 문서에서 한 부분을 표시하고 필요하면 메모를 답니다.",
    },
    "inspect_setup": {
        "en": "Read DeepTutor's own configuration and what each setting can be.",
        "zh": "读取 DeepTutor 自身的配置，以及每项设置的可选值。",
        "ko": "DeepTutor 자체 설정과 각 항목이 가질 수 있는 값을 확인합니다.",
    },
    "apply_setting": {
        "en": "Change one DeepTutor setting to an allowed value.",
        "zh": "把 DeepTutor 的某一项设置改为允许的取值。",
        "ko": "DeepTutor 설정 하나를 허용된 값으로 변경합니다.",
    },
    "run_setup_job": {
        "en": "Install a document-parsing engine or download its model weights.",
        "zh": "安装文档解析引擎或下载其模型权重。",
        "ko": "문서 파싱 엔진을 설치하거나 모델 가중치를 내려받습니다.",
    },
    "partner_read": {
        "en": "Read your memory: the owner's shared memory plus your own.",
        "zh": "读取记忆：所有者共享的记忆加上你自己的记忆。",
        "ko": "메모리를 읽습니다: 소유자가 공유한 메모리와 자신의 메모리.",
    },
    "partner_memorize": {
        "en": "Save something worth remembering about this person.",
        "zh": "把关于这个人值得记住的事情保存下来。",
        "ko": "이 사람에 대해 기억할 만한 것을 저장합니다.",
    },
}


def capability_description_i18n(name: str, fallback: str = "") -> dict[str, str]:
    values = _CAPABILITY_DESCRIPTIONS.get(name)
    if values:
        return dict(values)
    return {"en": fallback, "zh": fallback, "ko": fallback}


def tool_description_i18n(name: str, fallback: str = "") -> dict[str, str]:
    values = _TOOL_DESCRIPTIONS.get(name)
    if values:
        return dict(values)
    return {"en": fallback, "zh": fallback, "ko": fallback}


def localized_description(values: dict[str, str], language: str) -> str:
    normalized = (language or "en").lower()
    if normalized.startswith("zh"):
        lang = "zh"
    elif normalized.startswith("ko"):
        lang = "ko"
    else:
        lang = "en"
    return values.get(lang) or values.get("en") or values.get("zh") or ""


__all__ = [
    "capability_description_i18n",
    "localized_description",
    "tool_description_i18n",
]
