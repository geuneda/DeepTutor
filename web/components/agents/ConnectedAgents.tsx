"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Cpu, Loader2, Plug, Plus, Trash2, X } from "lucide-react";

import { agentGlyph } from "@/components/agents/agent-icons";
import PartnerAvatar from "@/components/partners/PartnerAvatar";
import SpaceSectionHeader from "@/components/space/SpaceSectionHeader";
import {
  connectSubagent,
  detectSubagents,
  disconnectSubagent,
  listConnectablePartners,
  listSubagentConnections,
  type ConnectablePartner,
  type SubagentBackendInfo,
  type SubagentConnection,
} from "@/lib/subagents-api";

/**
 * Connected agents — live agents the chat composer can select and consult in
 * real time: Claude Code / Codex on the user's machine, or one of their
 * partners. Distinct from the imported-history agents below it: those replay
 * past transcripts, these drive the live agent now. CLI detection is
 * machine-global (is the CLI installed here); partners come from the user's
 * partner list. Consulting a partner opens a fresh session on it — every
 * consult within one DeepTutor chat is archived as one partner session.
 */

const PARTNER_KIND = "partner";

function backendLabel(kind: string, t: (key: string, options?: Record<string, unknown>) => string): string {
  if (kind === "claude_code") return "Claude Code";
  if (kind === "codex") return "Codex";
  if (kind === "gemini") return "Gemini CLI";
  if (kind === "antigravity") return "Antigravity CLI";
  if (kind === "kimi") return "Kimi CLI";
  if (kind === "opencode") return "opencode";
  if (kind === "mimo") return "MiMo Code";
  if (kind === PARTNER_KIND) return t("Partner");
  return kind;
}

export default function ConnectedAgents() {
  const { t } = useTranslation();

  const [backends, setBackends] = useState<SubagentBackendInfo[]>([]);
  const [connections, setConnections] = useState<SubagentConnection[]>([]);
  const [partners, setPartners] = useState<ConnectablePartner[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [busyName, setBusyName] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [detected, conns, parts] = await Promise.all([
        detectSubagents().catch(() => [] as SubagentBackendInfo[]),
        listSubagentConnections().catch(() => [] as SubagentConnection[]),
        listConnectablePartners().catch(() => [] as ConnectablePartner[]),
      ]);
      setBackends(detected);
      setConnections(conns);
      setPartners(parts);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const available = useMemo(
    () => backends.filter((b) => b.available),
    [backends],
  );
  // Something is connectable when a CLI is installed here or a partner exists.
  const canConnect = available.length > 0 || partners.length > 0;
  const partnerName = useCallback(
    (id: string) => partners.find((p) => p.partner_id === id)?.name || id,
    [partners],
  );

  const handleDisconnect = useCallback(
    async (name: string) => {
      if (
        !window.confirm(
          t(
            "Disconnect “{{name}}”? This only removes the connection; your local agent is untouched.",
            { name },
          ),
        )
      )
        return;
      setBusyName(name);
      try {
        await disconnectSubagent(name);
        await load();
      } finally {
        setBusyName(null);
      }
    },
    [load, t],
  );

  return (
    <section className="space-y-4">
      <SpaceSectionHeader
        icon={Plug}
        title={t("Connected agents")}
        description={t("Bring in the Claude Code, Codex, Gemini CLI, Kimi CLI, opencode, or MiMo Code on this machine, or one of your partners — select one in chat to consult it directly, with its full run shown live.")}
        action={
          canConnect ? (
            <button
              type="button"
              onClick={() => setModalOpen(true)}
              className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--foreground)] px-3 py-1.5 text-[12px] font-medium text-[var(--background)] shadow-sm transition-opacity hover:opacity-90"
            >
              <Plus className="h-3.5 w-3.5" />
              {t("Connect agent")}
            </button>
          ) : null
        }
      />

      {loading ? (
        <div className="flex items-center gap-2 px-1 text-[12px] text-[var(--muted-foreground)]">
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          {t("Detecting local agents…")}
        </div>
      ) : !canConnect ? (
        <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--card)]/40 px-4 py-5 text-[12.5px] leading-relaxed text-[var(--muted-foreground)]">
          {t("No agent CLI detected on this machine (Claude Code, Codex, Gemini CLI, Kimi CLI, opencode, MiMo Code), and no partners yet. Install and log in to any of them, or create a partner, to connect one.")}
        </div>
      ) : connections.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--card)]/40 px-4 py-5 text-[12.5px] leading-relaxed text-[var(--muted-foreground)]">
          {t("No agents connected yet. Click “Connect agent” to bring in a detected local agent CLI, or a partner.")}
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {connections.map((conn) => {
            const Glyph = agentGlyph(conn.agent_kind);
            // A partner connection wears its own face (the avatar set on the
            // partner page), not the generic heart glyph.
            const partner =
              conn.agent_kind === PARTNER_KIND
                ? partners.find((p) => p.partner_id === conn.partner_id)
                : undefined;
            return (
              <div
                key={conn.name}
                className="group flex items-center gap-3 rounded-2xl border border-[var(--border)] bg-[var(--card)] px-4 py-3"
              >
                {partner ? (
                  <PartnerAvatar
                    name={partner.name}
                    emoji={partner.emoji}
                    color={partner.color}
                    image={partner.avatar}
                    size={40}
                    className="shrink-0"
                  />
                ) : (
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[var(--border)]/60 bg-[var(--background)] text-[var(--foreground)]">
                    {Glyph ? (
                      <Glyph size={20} />
                    ) : (
                      <Cpu size={18} strokeWidth={1.6} />
                    )}
                  </span>
                )}
                <div className="min-w-0 flex-1">
                  <div className="truncate text-[13.5px] font-semibold tracking-tight text-[var(--foreground)]">
                    {conn.name}
                  </div>
                  <div className="mt-0.5 truncate text-[11.5px] text-[var(--muted-foreground)]">
                    {backendLabel(conn.agent_kind, t)}
                    {conn.agent_kind === PARTNER_KIND
                      ? conn.partner_id
                        ? ` · ${partnerName(conn.partner_id)}`
                        : ""
                      : conn.cwd
                        ? ` · ${conn.cwd}`
                        : ""}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => void handleDisconnect(conn.name)}
                  disabled={busyName === conn.name}
                  title={t("Disconnect")}
                  aria-label={t("Disconnect")}
                  className="rounded-lg border border-[var(--border)]/50 p-2 text-[var(--muted-foreground)] transition-colors hover:border-red-300 hover:text-red-600 disabled:opacity-50 dark:hover:border-red-900 dark:hover:text-red-400"
                >
                  {busyName === conn.name ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Trash2 className="h-3.5 w-3.5" />
                  )}
                </button>
              </div>
            );
          })}
        </div>
      )}

      {modalOpen && (
        <ConnectModal
          backends={available}
          partners={partners}
          existingNames={connections.map((c) => c.name)}
          t={t}
          onClose={() => setModalOpen(false)}
          onConnected={() => {
            setModalOpen(false);
            void load();
          }}
        />
      )}
    </section>
  );
}

function ConnectModal({
  backends,
  partners,
  existingNames,
  t,
  onClose,
  onConnected,
}: {
  backends: SubagentBackendInfo[];
  partners: ConnectablePartner[];
  existingNames: string[];
  t: (key: string, options?: Record<string, unknown>) => string;
  onClose: () => void;
  onConnected: () => void;
}) {
  // The agent-type choices: each detected CLI, plus "Partner" when any exist.
  const options = useMemo(
    () => [
      ...backends.map((b) => ({ kind: b.kind, label: b.display_name })),
      ...(partners.length
        ? [{ kind: PARTNER_KIND, label: t("Partner") }]
        : []),
    ],
    [backends, partners, t],
  );

  const [kind, setKind] = useState(options[0]?.kind ?? "");
  const [name, setName] = useState("");
  const [nameTouched, setNameTouched] = useState(false);
  const [cwd, setCwd] = useState("");
  const [partnerId, setPartnerId] = useState(partners[0]?.partner_id ?? "");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const isPartner = kind === PARTNER_KIND;

  // While the user hasn't renamed the connection, mirror the chosen partner's
  // name so the connection reads as that partner by default.
  useEffect(() => {
    if (!isPartner || nameTouched) return;
    const picked = partners.find((p) => p.partner_id === partnerId);
    setName(picked?.name ?? "");
  }, [isPartner, nameTouched, partnerId, partners]);

  const submit = useCallback(async () => {
    const trimmed = name.trim();
    if (!trimmed) {
      setError(t("Please enter a name."));
      return;
    }
    if (existingNames.includes(trimmed)) {
      setError(
        t("A connection with this name already exists."),
      );
      return;
    }
    if (isPartner && !partnerId) {
      setError(t("Please pick a partner."));
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await connectSubagent(
        isPartner
          ? { name: trimmed, agent_kind: PARTNER_KIND, partner_id: partnerId }
          : { name: trimmed, agent_kind: kind, cwd: cwd.trim() },
      );
      onConnected();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSubmitting(false);
    }
  }, [name, kind, cwd, isPartner, partnerId, existingNames, onConnected, t]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-serif text-[16px] font-semibold tracking-tight text-[var(--foreground)]">
            {t("Connect an agent")}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-[var(--muted-foreground)] hover:bg-[var(--muted)]/60 hover:text-[var(--foreground)]"
            aria-label={t("Close")}
          >
            <X size={16} />
          </button>
        </div>

        <div className="space-y-3.5">
          <div>
            <label className="mb-1.5 block text-[12px] font-medium text-[var(--foreground)]">
              {t("Agent")}
            </label>
            {/* Two per row — up to six CLIs plus Partner can be on offer. */}
            <div className="grid grid-cols-2 gap-2">
              {options.map((opt) => {
                const Glyph = agentGlyph(opt.kind);
                return (
                  <button
                    key={opt.kind}
                    type="button"
                    onClick={() => setKind(opt.kind)}
                    className={`flex items-center justify-center gap-1.5 rounded-lg border px-3 py-2 text-[12.5px] font-medium transition-colors ${
                      kind === opt.kind
                        ? "border-[var(--primary)] bg-[var(--primary)]/[0.07] text-[var(--foreground)]"
                        : "border-[var(--border)] text-[var(--muted-foreground)] hover:border-[var(--border)] hover:text-[var(--foreground)]"
                    }`}
                  >
                    {Glyph ? <Glyph size={15} /> : null}
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </div>

          {isPartner && (
            <div>
              <label className="mb-1.5 block text-[12px] font-medium text-[var(--foreground)]">
                {t("Partner")}
              </label>
              <select
                value={partnerId}
                onChange={(e) => setPartnerId(e.target.value)}
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] text-[var(--foreground)] outline-none focus:border-[var(--ring)]"
              >
                {partners.map((p) => (
                  <option key={p.partner_id} value={p.partner_id}>
                    {p.emoji ? `${p.emoji} ` : ""}
                    {p.name}
                    {p.description ? ` — ${p.description}` : ""}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="mb-1.5 block text-[12px] font-medium text-[var(--foreground)]">
              {t("Name")}
            </label>
            <input
              autoFocus
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                setNameTouched(true);
              }}
              placeholder={t("e.g. My coding agent")}
              className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] text-[var(--foreground)] outline-none focus:border-[var(--ring)]"
            />
          </div>

          {!isPartner && (
            <div>
              <label className="mb-1.5 block text-[12px] font-medium text-[var(--foreground)]">
                {t("Working directory (optional)")}
              </label>
              <input
                value={cwd}
                onChange={(e) => setCwd(e.target.value)}
                placeholder={t("e.g. /Users/you/project — the agent runs here")}
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 font-mono text-[12px] text-[var(--foreground)] outline-none focus:border-[var(--ring)]"
              />
            </div>
          )}

          {isPartner && (
            <p className="text-[11.5px] leading-relaxed text-[var(--muted-foreground)]">
              {t("Consulting this partner in chat opens a session on it, just like the partner page; every consult within one chat is archived as the same session.")}
            </p>
          )}

          {error && (
            <p className="text-[12px] text-red-600 dark:text-red-400">
              {error}
            </p>
          )}
        </div>

        <div className="mt-5 flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-3 py-1.5 text-[12.5px] font-medium text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
          >
            {t("Cancel")}
          </button>
          <button
            type="button"
            onClick={() => void submit()}
            disabled={submitting}
            className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--foreground)] px-3.5 py-1.5 text-[12.5px] font-medium text-[var(--background)] shadow-sm transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {submitting ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Plug className="h-3.5 w-3.5" />
            )}
            {t("Connect")}
          </button>
        </div>
      </div>
    </div>
  );
}
