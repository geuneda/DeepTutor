"use client";

import type { MasteryEvent } from "@/lib/learning-api";

import {
  formatRelative,
  type LearningLanguage,
  type Translate,
} from "./format";

/**
 * What the tutor and the engine have actually done to this path, newest first.
 *
 * The engine commits an event for every state change, which until now nothing
 * read. Rendering them turns the path from a score into a record: when an
 * objective was posed, answered, graded, assessed, or rebuilt — and, because
 * the same feed drives the live refresh, the list grows while you watch.
 */
export function ActivityTimeline({
  events,
  objectiveNames,
  tr,
  language,
}: {
  events: MasteryEvent[];
  /** objective id → display name, so the feed reads in the learner's terms. */
  objectiveNames: Record<string, string>;
  tr: Translate;
  language: LearningLanguage;
}) {
  if (events.length === 0) {
    return (
      <p className="py-6 text-center text-xs text-[var(--muted-foreground)]">
        {tr(
          "还没有活动记录。",
          "Nothing has happened on this path yet.",
          "아직 이 경로에 활동 기록이 없습니다.",
        )}
      </p>
    );
  }
  return (
    <ol className="space-y-1.5">
      {[...events].reverse().map((event) => (
        <li key={event.id} className="flex items-baseline gap-2 text-xs">
          <span
            className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${dotClass(event)}`}
          />
          <span className="flex-1 text-[var(--foreground)]">
            {describe(event, objectiveNames, tr)}
          </span>
          <span className="shrink-0 text-[var(--muted-foreground)]">
            {formatRelative(event.created_at, language)}
          </span>
        </li>
      ))}
    </ol>
  );
}

function objectiveName(
  event: MasteryEvent,
  names: Record<string, string>,
): string {
  const id = String(event.payload?.knowledge_point_id ?? "");
  return names[id] || id;
}

function describe(
  event: MasteryEvent,
  names: Record<string, string>,
  tr: Translate,
): string {
  const name = objectiveName(event, names);
  switch (event.event_type) {
    case "path.created":
      return tr(
        "创建了这条精通之路",
        "Path created",
        "숙달 경로를 만들었습니다",
      );
    case "path.built":
    case "path.modules_replaced": {
      const modules = Number(event.payload?.module_count ?? 0);
      const points = Number(event.payload?.knowledge_point_count ?? 0);
      return event.payload?.mode === "append"
        ? tr(
            `追加了 ${modules} 个模块、${points} 个知识点`,
            `Added ${modules} modules and ${points} objectives`,
            `${modules}개 모듈과 ${points}개 학습 목표를 추가했습니다`,
          )
        : tr(
            `重建了路径：${modules} 个模块、${points} 个知识点`,
            `Rebuilt the path: ${modules} modules, ${points} objectives`,
            `경로를 다시 구성했습니다: 모듈 ${modules}개, 학습 목표 ${points}개`,
          );
    }
    case "path.reset":
      return tr("重置了进度", "Progress reset", "진행 상황을 초기화했습니다");
    case "path.renamed": {
      const renamed = String(event.payload?.name ?? "").trim();
      return renamed
        ? tr(
            `改名为「${renamed}」`,
            `Renamed to "${renamed}"`,
            `새 이름: "${renamed}"`,
          )
        : tr(
            "恢复了自动命名",
            "Restored the derived name",
            "자동 생성 이름으로 되돌렸습니다",
          );
    }
    case "interaction.registered":
      return tr(
        `出了一道题：${name}`,
        `Posed a question on ${name}`,
        `문제 출제: ${name}`,
      );
    case "interaction.awaiting_input":
      return tr(
        "等待你的回答",
        "Waiting for your answer",
        "답변을 기다리는 중입니다",
      );
    case "interaction.answered":
      return tr(
        "收到你的回答",
        "Your answer was recorded",
        "답변을 기록했습니다",
      );
    case "attempt.recorded":
      return event.payload?.is_correct
        ? tr(`${name} 答对了`, `Correct on ${name}`, `${name}: 정답`)
        : tr(`${name} 答错了`, `Missed ${name}`, `${name}: 오답`);
    case "interaction.graded":
      return tr("判分完成", "Graded", "채점을 완료했습니다");
    case "interaction.abandoned":
      return tr(
        "跳过了待回答的题目",
        "Skipped the outstanding question",
        "답변 대기 중인 문제를 건너뛰었습니다",
      );
    case "mastery.assessed":
      return event.payload?.passed
        ? tr(
            `${name} 的解释达标`,
            `Explanation accepted for ${name}`,
            `${name}: 설명이 통과 기준을 충족했습니다`,
          )
        : tr(
            `${name} 的解释还不够`,
            `Explanation not yet sufficient for ${name}`,
            `${name}: 설명이 아직 충분하지 않습니다`,
          );
    case "path.saved":
      return tr(
        "保存了路径状态",
        "Path state saved",
        "경로 상태를 저장했습니다",
      );
    default:
      return event.event_type;
  }
}

function dotClass(event: MasteryEvent): string {
  if (event.event_type === "attempt.recorded")
    return event.payload?.is_correct ? "bg-green-500" : "bg-red-500";
  if (event.event_type === "mastery.assessed")
    return event.payload?.passed ? "bg-green-500" : "bg-yellow-500";
  if (event.event_type.startsWith("path.")) return "bg-[var(--primary)]";
  return "bg-[var(--muted-foreground)]/50";
}
