// AIOS Starter: the YOUR AIOS 2.0 prompt library inside bb.
//
// One library (prompts.ts, generated from bb-kit/prompts-src) serves three surfaces:
// - the "AIOS course" page in the sidebar (app.tsx, over RPC): read, copy or start a chat with any prompt;
// - the `bb aios-kit` command: list, show, start and star prompts from a terminal or an agent;
// - bb's built-in Prompt Library (Ctrl+R in any composer), once `bb aios-kit star` has saved every prompt there.
import { defineRpcContract, type BbPluginApi } from "@get-bb/plugin-sdk";
import { z } from "zod";
import library from "./prompts";

export interface LibraryPrompt {
  id: string;
  title: string;
  what: string;
  check: string;
  body: string;
}
export interface LibraryModule {
  number: string;
  title: string;
  slug: string;
  pack: string;
  prompts: LibraryPrompt[];
}

const MODULES: LibraryModule[] = (library as { modules: LibraryModule[] }).modules;
const PROMPT_LIBRARY = "bb--prompt-library";

const promptSchema = z.object({
  id: z.string(),
  title: z.string(),
  what: z.string(),
  check: z.string(),
  body: z.string(),
});
const moduleSchema = z.object({
  number: z.string(),
  title: z.string(),
  slug: z.string(),
  pack: z.string(),
  prompts: z.array(promptSchema),
});
const projectSchema = z.object({ id: z.string(), name: z.string() });

export const rpcContract = defineRpcContract({
  library: {
    input: z.null(),
    output: z.object({
      modules: z.array(moduleSchema),
      projects: z.array(projectSchema),
      defaultProjectId: z.string().nullable(),
    }),
  },
  start: {
    input: z.object({ promptId: z.string().min(1).max(20), projectId: z.string().min(1).max(80) }),
    output: z.object({ threadId: z.string() }),
  },
  star_all: {
    input: z.null(),
    output: z.object({ starred: z.number(), skipped: z.string().nullable() }),
  },
});

export function findPrompt(id: string): { module: LibraryModule; prompt: LibraryPrompt } | null {
  for (const module of MODULES) {
    const prompt = module.prompts.find((p) => p.id === id);
    if (prompt) return { module, prompt };
  }
  return null;
}

export function starTitle(module: LibraryModule, prompt: LibraryPrompt): string {
  return `AIOS ${prompt.id} · ${prompt.title}`.slice(0, 120);
}

export function listText(): string {
  const lines: string[] = [];
  for (const module of MODULES) {
    lines.push(`Module ${Number(module.number)} · ${module.title}  (pack: ${module.pack})`);
    for (const p of module.prompts) lines.push(`  ${p.id.padEnd(6)} ${p.title}`);
  }
  return lines.join("\n");
}

export default async function plugin(bb: BbPluginApi) {
  const settings = bb.settings.define({
    projectId: {
      type: "string",
      label: "AIOS project",
      description: "The bb project of your AIOS folder. New chats from the course page start there.",
      default: "",
    },
  });

  async function projects() {
    const list = await bb.sdk.projects.list();
    return list.map((p) => ({ id: p.id, name: p.name }));
  }

  async function defaultProject(): Promise<string | null> {
    const { projectId } = await settings.get();
    if (projectId) return projectId;
    const all = await projects();
    const aios = all.find((p) => /aios/i.test(p.name));
    return aios?.id ?? all[0]?.id ?? null;
  }

  async function start(promptId: string, projectId: string) {
    const found = findPrompt(promptId);
    if (!found) throw new Error(`No prompt ${promptId}. Run "bb aios-kit list" to see them.`);
    // The project's own checkout on the machine that holds it, never a new worktree: each prompt builds on the
    // files the last one made. Without a known source machine, fall back to bb's project default.
    const project = (await bb.sdk.projects.get({ projectId })) as unknown as {
      sources?: { hostId?: string | null; isDefault?: boolean }[];
      project?: { sources?: { hostId?: string | null; isDefault?: boolean }[] };
    };
    const sources = project.sources ?? project.project?.sources ?? [];
    const hostId = (sources.find((s) => s.isDefault) ?? sources[0])?.hostId ?? null;
    const thread = await bb.sdk.threads.spawn({
      projectId,
      environment: hostId
        ? { type: "host", hostId, workspace: { type: "unmanaged", path: null } }
        : { type: "project-default" },
      prompt: found.prompt.body,
      title: `AIOS ${found.prompt.id} · ${found.prompt.title}`,
      providerId: "claude-code",
    });
    return { threadId: thread.id };
  }

  async function removeStale(): Promise<number> {
    // Older kit versions starred prompts whose text has since changed: unstar every "AIOS " title not in this library.
    const current = new Set(MODULES.flatMap((m) => m.prompts.map((p) => p.body)));
    // The Prompt Library has no list call over RPC, and a search returns at most 20 starred rows: search per module.
    type Row = { id: string; kind: string; title?: string | null; prompt?: { text?: string } };
    const rows = new Map<string, Row>();
    const queries = ["AIOS", ...Array.from({ length: 20 }, (_, i) => `AIOS ${i + 1}`), "AIOS 12d", "AIOS 12i", "AIOS 12v"];
    for (const query of queries) {
      const found = (await bb.sdk.plugins.callRpc({
        pluginId: PROMPT_LIBRARY,
        method: "search",
        input: { query, scope: "global", projectId: null, threadId: null, composer: "follow-up", waitForHistory: false, refreshHistory: false },
        outputSchema: z.object({ prompts: z.array(z.object({ id: z.string(), kind: z.string() }).passthrough()) }).passthrough(),
      })) as { prompts: Row[] };
      for (const row of found.prompts) rows.set(row.id, row);
    }
    const found = { prompts: [...rows.values()] };
    let removed = 0;
    for (const row of found.prompts) {
      if (row.kind !== "starred" || !(row.title ?? "").startsWith("AIOS ")) continue;
      if (current.has(row.prompt?.text ?? "")) continue;
      await bb.sdk.plugins.callRpc({ pluginId: PROMPT_LIBRARY, method: "unstar", input: { id: row.id }, outputSchema: z.unknown() });
      removed += 1;
    }
    return removed;
  }

  async function starAll() {
    let starred = 0;
    try {
      await removeStale();
    } catch {
      // Removing stale stars is a tidy-up; starring still goes ahead.
    }
    for (const module of MODULES) {
      for (const prompt of module.prompts) {
        try {
          await bb.sdk.plugins.callRpc({
            pluginId: PROMPT_LIBRARY,
            method: "star",
            input: { prompt: { text: prompt.body, mentions: [] }, title: starTitle(module, prompt) },
            outputSchema: z.unknown(),
          });
          starred += 1;
        } catch (cause) {
          const message = cause instanceof Error ? cause.message : String(cause);
          return {
            starred,
            skipped: `Prompt Library is not running (${message.slice(0, 160)}). Enable it with "bb plugin enable ${PROMPT_LIBRARY}", then run "bb aios-kit star" again.`,
          };
        }
      }
    }
    return { starred, skipped: null };
  }

  bb.rpc.register(rpcContract, {
    library: async () => ({ modules: MODULES, projects: await projects(), defaultProjectId: await defaultProject() }),
    start: ({ promptId, projectId }) => start(promptId, projectId),
    star_all: () => starAll(),
  });

  const usage = [
    "Usage:",
    "  bb aios-kit list                       every module and prompt",
    "  bb aios-kit show <id>                  print one prompt, ready to paste (for example 2.1)",
    "  bb aios-kit start <id> [--project ID]  start a Claude chat with that prompt in your AIOS project",
    "  bb aios-kit star                       save every prompt in bb's Prompt Library (Ctrl+R)",
  ].join("\n");

  bb.cli.register({
    name: "aios-kit",
    summary: "The YOUR AIOS 2.0 prompt library: list, show, start and star prompts",
    commands: [
      { name: "list", summary: "List every module and prompt", usage: "bb aios-kit list [--json]" },
      { name: "show", summary: "Print one prompt, ready to paste", usage: "bb aios-kit show <id> [--json]" },
      {
        name: "start",
        summary: "Start a Claude chat with one prompt in your AIOS project",
        usage: "bb aios-kit start <id> [--project <id>] [--json]",
      },
      { name: "star", summary: "Save every prompt in bb's Prompt Library", usage: "bb aios-kit star [--json]" },
    ],
    async run(argv) {
      const json = argv.includes("--json");
      const args = argv.filter((a) => a !== "--json");
      const [command, ...rest] = args;
      const out = (value: unknown, text: string) => ({ exitCode: 0, stdout: json ? JSON.stringify(value) : text });
      switch (command) {
        case undefined:
        case "help":
        case "--help":
          return { exitCode: 0, stdout: usage };
        case "list":
          return out(MODULES, listText());
        case "show": {
          const found = rest[0] ? findPrompt(rest[0]) : null;
          if (!found) return { exitCode: 1, stderr: `No prompt ${rest[0] ?? ""}. Run "bb aios-kit list".` };
          return out(found.prompt, found.prompt.body);
        }
        case "start": {
          const id = rest[0];
          const flag = rest.indexOf("--project");
          const projectId = flag >= 0 ? rest[flag + 1] : await defaultProject();
          if (!id) break;
          if (!projectId) return { exitCode: 1, stderr: "No bb project yet. Add your AIOS folder as a project first." };
          try {
            const result = await start(id, projectId);
            return out(result, `Started ${result.threadId} with prompt ${id}.`);
          } catch (cause) {
            return { exitCode: 1, stderr: cause instanceof Error ? cause.message : String(cause) };
          }
        }
        case "star": {
          const result = await starAll();
          const text = result.skipped ?? `Saved ${result.starred} prompts in the Prompt Library. Press Ctrl+R in any chat box and type "AIOS".`;
          return { exitCode: result.skipped ? 1 : 0, stdout: json ? JSON.stringify(result) : text };
        }
      }
      return { exitCode: 1, stderr: usage };
    },
  });
}
