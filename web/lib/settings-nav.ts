"use client";

import {
  AudioLines,
  Bot,
  Boxes,
  Brain,
  BrainCircuit,
  Clapperboard,
  Database,
  FileScan,
  Image as ImageIcon,
  Library,
  MessagesSquare,
  Mic,
  Network,
  Palette,
  Paperclip,
  Search,
  SlidersHorizontal,
  Sparkles,
  Wrench,
  type LucideIcon,
} from "lucide-react";

import {
  ClaudeGlyph,
  CodexGlyph,
  GeminiGlyph,
  KimiGlyph,
  MimoGlyph,
  OpencodeGlyph,
} from "@/components/agents/agent-icons";
import type { ServiceName } from "@/components/settings/SettingsContext";

/**
 * Settings information architecture.
 *
 * Two levels, deliberately unlike the flat Learning Space dashboard:
 *   • The hub (`/settings`) shows six category blocks + a resident Status
 *     module — nothing else.
 *   • Categories with several settings (Models, Chat) open a sub-hub page
 *     that lists their leaves as tiles; single-setting categories link
 *     straight to their leaf page.
 *
 * This module is the single source for the blocks, the sub-hub tiles, and the
 * breadcrumb trail rendered top-left on every page.
 */

export interface SettingsLeaf {
  key: string;
  href: string;
  /** i18n key — the English source string. */
  label: string;
  /** i18n key for the one-line descriptor. */
  blurb: string;
  icon: LucideIcon;
  /** Colored icon-tile accent for the sub-hub grid (full class strings). */
  tile: string;
  /** Model-service leaves carry a configured/not chip from the catalog. */
  service?: ServiceName;
  /** Hidden from non-admin users (the backend rejects them anyway). */
  adminOnly?: boolean;
}

export interface SettingsCategory {
  key: string;
  /** i18n key — the English source string. */
  label: string;
  /** One-line descriptor shown on the hub block, as an i18n key. */
  blurb: string;
  icon: LucideIcon;
  /** Where clicking the block lands — a sub-hub or a leaf page. */
  href: string;
  /** Leaves listed on the sub-hub page (omitted for direct-leaf categories). */
  children?: SettingsLeaf[];
}

const MODEL_CHILDREN: SettingsLeaf[] = [
  {
    key: "llm",
    href: "/settings/llm",
    label: "LLM",
    blurb: "Language model providers and active profile.",
    icon: Brain,
    tile: "bg-violet-500/10 text-violet-600 dark:text-violet-400",
    service: "llm",
  },
  {
    key: "embedding",
    href: "/settings/embedding",
    label: "Embedding",
    blurb: "Embedding model providers and dimensions.",
    icon: Database,
    tile: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
    service: "embedding",
  },
  {
    key: "search",
    href: "/settings/search",
    label: "Search",
    blurb: "Web search providers.",
    icon: Search,
    tile: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
    service: "search",
  },
  {
    key: "tts",
    href: "/settings/tts",
    label: "Text-to-Speech",
    blurb: "Text-to-speech for reading replies aloud.",
    icon: AudioLines,
    tile: "bg-rose-500/10 text-rose-600 dark:text-rose-400",
    service: "tts",
  },
  {
    key: "stt",
    href: "/settings/stt",
    label: "Speech-to-Text",
    blurb: "Speech-to-text for the composer microphone.",
    icon: Mic,
    tile: "bg-pink-500/10 text-pink-600 dark:text-pink-400",
    service: "stt",
  },
  {
    key: "imagegen",
    href: "/settings/image",
    label: "Image Generation",
    blurb: "Text-to-image model for the chat imagegen tool.",
    icon: ImageIcon,
    tile: "bg-fuchsia-500/10 text-fuchsia-600 dark:text-fuchsia-400",
    service: "imagegen",
  },
  {
    key: "videogen",
    href: "/settings/video",
    label: "Video Generation",
    blurb: "Text-to-video model for the chat videogen tool.",
    icon: Clapperboard,
    tile: "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400",
    service: "videogen",
  },
];

const CHAT_CHILDREN: SettingsLeaf[] = [
  {
    key: "tools",
    href: "/settings/tools",
    label: "Tools",
    blurb: "Built-in tools the chat agent can invoke.",
    icon: Wrench,
    tile: "bg-orange-500/10 text-orange-600 dark:text-orange-400",
  },
  {
    key: "capabilities",
    href: "/settings/capabilities",
    label: "Capabilities",
    blurb: "Per-capability LLM parameters and runtime knobs.",
    icon: SlidersHorizontal,
    tile: "bg-lime-500/10 text-lime-600 dark:text-lime-400",
  },
  {
    key: "starters",
    href: "/settings/starters",
    label: "Starting points",
    blurb: "How much history shapes the three lines under the composer.",
    icon: Sparkles,
    tile: "bg-violet-500/10 text-violet-600 dark:text-violet-400",
  },
  {
    key: "attachments",
    href: "/settings/attachments",
    label: "Attachments",
    blurb: "Upload caps and extraction budgets for chat attachments.",
    icon: Paperclip,
    tile: "bg-teal-500/10 text-teal-600 dark:text-teal-400",
    adminOnly: true,
  },
];

const AGENT_CHILDREN: SettingsLeaf[] = [
  {
    key: "agent-claude-code",
    href: "/settings/agents/claude-code",
    label: "Claude Code",
    blurb: "Model, reasoning effort, and run params for the local Claude Code.",
    // Brand glyph shares the lucide call signature (size/className).
    icon: ClaudeGlyph as unknown as LucideIcon,
    tile: "bg-orange-500/10 text-orange-600 dark:text-orange-400",
    adminOnly: true,
  },
  {
    key: "agent-codex",
    href: "/settings/agents/codex",
    label: "Codex",
    blurb: "Model, reasoning effort, and run params for the local Codex.",
    icon: CodexGlyph as unknown as LucideIcon,
    tile: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
    adminOnly: true,
  },
  {
    key: "agent-gemini",
    href: "/settings/agents/gemini",
    label: "Gemini CLI",
    blurb: "Model and run params for the local Gemini CLI.",
    icon: GeminiGlyph as unknown as LucideIcon,
    tile: "bg-sky-500/10 text-sky-600 dark:text-sky-400",
    adminOnly: true,
  },
  {
    key: "agent-kimi",
    href: "/settings/agents/kimi",
    label: "Kimi CLI",
    blurb: "Model and run params for the local Kimi CLI.",
    icon: KimiGlyph as unknown as LucideIcon,
    tile: "bg-zinc-500/10 text-zinc-700 dark:text-zinc-300",
    adminOnly: true,
  },
  {
    key: "agent-opencode",
    href: "/settings/agents/opencode",
    label: "opencode",
    blurb: "Model, reasoning effort, and run params for the local opencode.",
    icon: OpencodeGlyph as unknown as LucideIcon,
    tile: "bg-neutral-500/10 text-neutral-700 dark:text-neutral-300",
    adminOnly: true,
  },
  {
    key: "agent-mimo",
    href: "/settings/agents/mimo",
    label: "MiMo Code",
    blurb: "Model, reasoning effort, and run params for the local MiMo Code.",
    icon: MimoGlyph as unknown as LucideIcon,
    tile: "bg-orange-500/10 text-orange-600 dark:text-orange-400",
    adminOnly: true,
  },
];

export const SETTINGS_CATEGORIES: SettingsCategory[] = [
  {
    key: "appearance",
    label: "Appearance",
    blurb: "Theme and interface language",
    icon: Palette,
    href: "/settings/appearance",
  },
  {
    key: "network",
    label: "Network",
    blurb: "Ports, browser API base, and CORS",
    icon: Network,
    href: "/settings/network",
  },
  {
    key: "models",
    label: "Models",
    blurb: "Language, embedding, search, voice, and generation models",
    icon: Boxes,
    href: "/settings/models",
    children: MODEL_CHILDREN,
  },
  {
    key: "knowledge",
    label: "Knowledge Base",
    blurb: "Document parsing engine",
    icon: Library,
    href: "/settings/document-parsing",
  },
  {
    key: "chat",
    label: "Chat",
    blurb: "Tools, capabilities, and attachments",
    icon: MessagesSquare,
    href: "/settings/chat",
    children: CHAT_CHILDREN,
  },
  {
    key: "agents",
    label: "Partners & Agents",
    blurb: "Configure the subagents you can call on in chat",
    icon: Bot,
    href: "/settings/agents",
    children: AGENT_CHILDREN,
  },
  {
    key: "memory",
    label: "Memory",
    blurb: "Chunking, budget, dedup, and reference policies",
    icon: BrainCircuit,
    href: "/settings/memory",
  },
];

export const SETTINGS_HUB_HREF = "/settings";
const HUB_LABEL = "Settings";

/** Routes that are pure navigation (hub + sub-hubs) — no Save/Apply toolbar. */
const NAV_ONLY_ROUTES = new Set<string>([
  SETTINGS_HUB_HREF,
  ...SETTINGS_CATEGORIES.filter((c) => c.children).map((c) => c.href),
]);

export function isNavOnlyRoute(pathname: string): boolean {
  return NAV_ONLY_ROUTES.has(pathname);
}

// The on-disk file (under data/user/settings/) each leaf module persists to.
// Surfaced in the toolbar status line so every page says where its parameters
// live, without duplicating the string on each page.
const STORAGE_PATHS: Record<string, string> = {
  "/settings/appearance": "data/user/settings/interface.json",
  "/settings/network": "data/user/settings/system.json",
  "/settings/llm": "data/user/settings/model_catalog.json",
  "/settings/embedding": "data/user/settings/model_catalog.json",
  "/settings/search": "data/user/settings/model_catalog.json",
  "/settings/tts": "data/user/settings/model_catalog.json",
  "/settings/stt": "data/user/settings/model_catalog.json",
  "/settings/image": "data/user/settings/model_catalog.json",
  "/settings/video": "data/user/settings/model_catalog.json",
  "/settings/document-parsing": "data/user/settings/document_parsing.json",
  "/settings/tools": "data/user/settings/interface.json",
  "/settings/attachments": "data/user/settings/system.json",
  "/settings/capabilities": "data/user/settings/main.yaml · agents.yaml",
  "/settings/memory": "data/user/settings/main.yaml",
  "/settings/agents/claude-code": "data/user/settings/subagent.json",
  "/settings/agents/codex": "data/user/settings/subagent.json",
  "/settings/agents/gemini": "data/user/settings/subagent.json",
  "/settings/agents/kimi": "data/user/settings/subagent.json",
  "/settings/agents/opencode": "data/user/settings/subagent.json",
  "/settings/agents/mimo": "data/user/settings/subagent.json",
};

export function storagePathFor(pathname: string): string | null {
  return STORAGE_PATHS[pathname] ?? null;
}

export interface Crumb {
  label: string;
  /** Omitted on the current (last) crumb. */
  href?: string;
}

/**
 * The breadcrumb trail for a settings route, e.g.
 *   /settings/llm  →  设置 / 模型 / LLM
 *   /settings/network  →  设置 / 网络
 * Returns just [设置] for the hub itself.
 */
export function breadcrumbFor(pathname: string): Crumb[] {
  const root: Crumb = { label: HUB_LABEL, href: SETTINGS_HUB_HREF };
  if (pathname === SETTINGS_HUB_HREF) return [{ label: HUB_LABEL }];

  // Direct-leaf or sub-hub category landed on its own href.
  const category = SETTINGS_CATEGORIES.find((c) => c.href === pathname);
  if (category) return [root, { label: category.label }];

  // A leaf inside a sub-hub category.
  for (const c of SETTINGS_CATEGORIES) {
    const leaf = c.children?.find((l) => l.href === pathname);
    if (leaf) {
      return [root, { label: c.label, href: c.href }, { label: leaf.label }];
    }
  }

  // Unknown sub-route (e.g. a legacy redirect target rendered directly).
  return [root];
}
