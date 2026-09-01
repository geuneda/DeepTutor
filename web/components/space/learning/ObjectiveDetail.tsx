"use client";

import { Check, X } from "lucide-react";

import type { ObjectiveReport } from "@/lib/learning-api";

import {
  formatAbsolute,
  formatRelative,
  type LearningLanguage,
  type Translate,
} from "./format";

/**
 * The evidence behind one objective.
 *
 * The map answers "am I through the gate"; this answers "why" — which
 * questions were asked, what the learner said, what the engine did with it,
 * and when it comes back for review. The gate itself is shown as a bar with
 * the threshold marked, because a hard gate is only legible if you can see how
 * far away it is.
 */
export function ObjectiveDetail({
  report,
  tr,
  language,
}: {
  report: ObjectiveReport;
  tr: Translate;
  language: LearningLanguage;
}) {
  const qualitative = report.gate === "qualitative";
  return (
    <div className="mt-1 mb-2 ml-5 space-y-3 border-l border-[var(--border)] pl-3">
      <GateBar report={report} tr={tr} />

      {report.review && (
        <Row label={tr("间隔复习", "Spaced review", "간격 반복")}>
          {report.review.due_at
            ? tr(
                `${formatRelative(report.review.due_at, language)}复习 · ${formatAbsolute(report.review.due_at, language)}`,
                `Due ${formatRelative(report.review.due_at, language)} · ${formatAbsolute(report.review.due_at, language)}`,
                `${formatRelative(report.review.due_at, language)} 복습 · ${formatAbsolute(report.review.due_at, language)}`,
              )
            : tr("未排期", "Not scheduled", "일정 없음")}
          <span className="ml-2 text-[var(--muted-foreground)]">
            {tr(
              `第 ${report.review.interval_index + 1} 档 · 连对 ${report.review.consecutive_correct}`,
              `interval ${report.review.interval_index + 1} · ${report.review.consecutive_correct} in a row`,
              `${report.review.interval_index + 1}단계 · ${report.review.consecutive_correct}회 연속 정답`,
            )}
          </span>
        </Row>
      )}

      {qualitative && report.explanation && (
        <Row label={tr("你的解释", "Your explanation", "내 설명")}>
          <span className="italic">{report.explanation}</span>
        </Row>
      )}

      {report.attempts.length > 0 && (
        <div>
          <div className="text-xs text-[var(--muted-foreground)]">
            {tr(
              `作答记录（${report.correct_count}/${report.attempts.length} 正确）`,
              `Attempts (${report.correct_count}/${report.attempts.length} correct)`,
              `시도 기록(${report.correct_count}/${report.attempts.length} 정답)`,
            )}
          </div>
          <ul className="mt-1 space-y-1.5">
            {[...report.attempts].reverse().map((attempt, index) => (
              <li
                key={`${attempt.question_id}-${index}`}
                className="flex gap-2 text-xs"
              >
                {attempt.is_correct ? (
                  <Check className="mt-0.5 h-3 w-3 shrink-0 text-green-500" />
                ) : (
                  <X className="mt-0.5 h-3 w-3 shrink-0 text-red-500" />
                )}
                <div className="min-w-0">
                  <div className="text-[var(--foreground)]">
                    {attempt.prompt ||
                      tr(
                        "（题面已不可用）",
                        "(prompt unavailable)",
                        "(문제 내용 없음)",
                      )}
                  </div>
                  <div className="text-[var(--muted-foreground)]">
                    {tr("你答：", "You said: ", "내 답변: ")}
                    {attempt.answer || tr("（空）", "(blank)", "(비어 있음)")}
                    <span className="ml-2">
                      {formatRelative(attempt.at, language)}
                    </span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {report.errors.length > 0 && (
        <Row label={tr("错因", "Error diagnosis", "오류 진단")}>
          {report.errors.map((record) => (
            <span key={record.id} className="mr-2">
              {tr(
                ERROR_TYPE_CN[record.error_type] ?? record.error_type,
                record.error_type,
                ERROR_TYPE_KO[record.error_type] ?? record.error_type,
              )}
              {record.retries > 0 &&
                tr(
                  ` · 重试 ${record.retries} 次`,
                  ` · ${record.retries} retries`,
                  ` · ${record.retries}회 재시도`,
                )}
              {record.status === "graduated" &&
                tr(" · 已订正", " · cleared", " · 교정 완료")}
            </span>
          ))}
        </Row>
      )}

      {report.attempts.length === 0 && !report.explanation && (
        <p className="text-xs text-[var(--muted-foreground)]">
          {tr(
            "还没有作答记录。在对话里继续辅导后，这里会出现题目、你的回答和判分。",
            "No attempts yet. Once you tutor this in Chat, the questions, your answers, and the grading show up here.",
            "아직 시도 기록이 없습니다. 채팅에서 학습을 계속하면 문제, 답변, 채점 결과가 여기에 표시됩니다.",
          )}
        </p>
      )}
    </div>
  );
}

/** Mastery against the gate it has to clear. */
function GateBar({ report, tr }: { report: ObjectiveReport; tr: Translate }) {
  const pct = Math.round(report.mastery * 100);
  const thresholdPct = Math.round(report.threshold * 100);
  return (
    <div>
      <div className="flex items-baseline justify-between text-xs">
        <span className="text-[var(--muted-foreground)]">
          {report.gate === "qualitative"
            ? tr(
                "定性门槛：用自己的话讲清楚",
                "Qualitative gate: explain it in your own words",
                "정성 통과 기준: 자신의 말로 설명하기",
              )
            : tr(
                `定量门槛：${thresholdPct}%`,
                `Quantitative gate: ${thresholdPct}%`,
                `정량 통과 기준: ${thresholdPct}%`,
              )}
        </span>
        <span
          className={
            report.mastered
              ? "text-green-500"
              : "text-[var(--muted-foreground)]"
          }
        >
          {pct}%
        </span>
      </div>
      <div className="relative mt-1 h-1.5 w-full overflow-hidden rounded-full bg-[var(--accent)]">
        <div
          className={`h-full ${report.mastered ? "bg-green-500" : "bg-yellow-500"}`}
          style={{ width: `${pct}%` }}
        />
        {report.gate === "quantitative" && (
          <div
            className="absolute inset-y-0 w-px bg-[var(--foreground)]/40"
            style={{ left: `${thresholdPct}%` }}
          />
        )}
      </div>
    </div>
  );
}

function Row({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="text-xs">
      <div className="text-[var(--muted-foreground)]">{label}</div>
      <div className="mt-0.5 text-[var(--foreground)]">{children}</div>
    </div>
  );
}

const ERROR_TYPE_CN: Record<string, string> = {
  structural: "知识结构性",
  deviation: "理解偏差",
  application: "应用错误",
  metacognitive: "元认知",
};

const ERROR_TYPE_KO: Record<string, string> = {
  structural: "지식 구조",
  deviation: "이해 편차",
  application: "적용 오류",
  metacognitive: "메타인지",
};
