// AIOS Starter: the "AIOS course" page. Every module's prompts, with Copy and Start chat.
import { useCallback, useEffect, useState } from "react";
import { definePluginApp, experimental_copyToClipboard, useBbNavigate, useRpc } from "@get-bb/plugin-sdk/app";
import type { LibraryModule, LibraryPrompt, rpcContract } from "./server";
import { Button } from "@/components/ui/button";
import { Icon } from "@/components/ui/icon";
import { cn } from "@/lib/utils";

interface Library {
  modules: LibraryModule[];
  projects: { id: string; name: string }[];
  defaultProjectId: string | null;
}

function PromptCard({ prompt, projectId }: { prompt: LibraryPrompt; projectId: string | null }) {
  const rpc = useRpc<typeof rpcContract>();
  const navigate = useBbNavigate();
  const [open, setOpen] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const copy = async () => {
    const ok = await experimental_copyToClipboard({ text: prompt.body });
    setNote(ok ? "Copied. Paste it into a new chat." : "Copy failed. Open the prompt and select the text.");
  };
  const startChat = async () => {
    if (!projectId || busy) return;
    setBusy(true);
    try {
      const { threadId } = await rpc.call("start", { promptId: prompt.id, projectId });
      navigate.toThread(threadId);
    } catch (cause) {
      setNote(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(false);
    }
  };
  return (
    <li className="rounded-lg border border-border bg-card px-4 py-3">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 font-mono text-xs text-muted-foreground">{prompt.id}</span>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium">{prompt.title}</p>
          <p className="mt-1 text-sm text-muted-foreground">{prompt.what}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            <span className="font-medium text-foreground">Check: </span>
            {prompt.check}
          </p>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <Button size="sm" onClick={startChat} disabled={!projectId || busy}>
          <Icon name="Play" className="size-4" />
          {busy ? "Starting…" : "Start chat"}
        </Button>
        <Button size="sm" variant="outline" onClick={copy}>
          <Icon name="Copy" className="size-4" />
          Copy
        </Button>
        <Button size="sm" variant="ghost" onClick={() => setOpen(!open)} aria-expanded={open}>
          <Icon name={open ? "ChevronUp" : "ChevronDown"} className="size-4" />
          {open ? "Hide prompt" : "Read prompt"}
        </Button>
        {note === null ? null : <span className="text-xs text-muted-foreground">{note}</span>}
      </div>
      {open ? (
        <pre className="mt-3 max-h-96 overflow-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-xs">
          {prompt.body}
        </pre>
      ) : null}
    </li>
  );
}

function CoursePage() {
  const rpc = useRpc<typeof rpcContract>();
  const [lib, setLib] = useState<Library | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [openModule, setOpenModule] = useState<string | null>("01-start-here");
  const [starNote, setStarNote] = useState<string | null>(null);
  const load = useCallback(() => {
    rpc.call("library").then(
      (result) => {
        setLib(result);
        setProjectId((current) => current ?? result.defaultProjectId);
      },
      (cause) => setError(cause instanceof Error ? cause.message : String(cause)),
    );
  }, [rpc]);
  useEffect(load, [load]);
  const star = async () => {
    const result = await rpc.call("star_all");
    setStarNote(result.skipped ?? `Saved ${result.starred} prompts. Press Ctrl+R in any chat box and type "AIOS".`);
  };
  return (
    <div className="h-full min-h-0 flex-1 overflow-y-auto">
      <div className="mx-auto box-border w-full max-w-3xl px-4 pb-6 pt-3 md:px-5 md:pt-4">
        <p className="text-sm text-muted-foreground">
          One module at a time. Press <span className="font-medium text-foreground">Start chat</span> to hand a prompt to
          Claude in your AIOS project, or Copy it and paste it into any chat. Edit the lines marked "edit" first.
        </p>
        {error === null ? null : (
          <p role="alert" className="mt-3 text-sm text-destructive">
            {error}
          </p>
        )}
        {lib === null ? (
          <p className="mt-4 text-sm text-muted-foreground">Loading the course…</p>
        ) : (
          <>
            <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
              <label htmlFor="aios-project" className="text-muted-foreground">
                Start chats in
              </label>
              <select
                id="aios-project"
                className="rounded-md border border-border bg-background px-2 py-1 text-sm"
                value={projectId ?? ""}
                onChange={(event) => setProjectId(event.target.value || null)}
              >
                {lib.projects.length === 0 ? <option value="">No projects yet</option> : null}
                {lib.projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
              <Button size="sm" variant="outline" onClick={star}>
                <Icon name="Star" className="size-4" />
                Save all to Prompt Library
              </Button>
              {starNote === null ? null : <span className="text-xs text-muted-foreground">{starNote}</span>}
            </div>
            <ol className="mt-4 space-y-2">
              {lib.modules.map((module) => {
                const isOpen = openModule === module.slug;
                return (
                  <li key={module.slug} className="rounded-lg border border-border">
                    <button
                      type="button"
                      className={cn("flex w-full items-center gap-3 px-4 py-3 text-left", isOpen && "border-b border-border")}
                      onClick={() => setOpenModule(isOpen ? null : module.slug)}
                      aria-expanded={isOpen}
                    >
                      <span className="font-mono text-xs text-muted-foreground">{module.number}</span>
                      <span className="flex-1 text-sm font-medium">{module.title}</span>
                      <span className="text-xs text-muted-foreground">{module.prompts.length} prompts</span>
                      <Icon name={isOpen ? "ChevronUp" : "ChevronDown"} className="size-4 text-muted-foreground" />
                    </button>
                    {isOpen ? (
                      <ul className="space-y-2 p-3">
                        {module.prompts.map((prompt) => (
                          <PromptCard key={prompt.id} prompt={prompt} projectId={projectId} />
                        ))}
                      </ul>
                    ) : null}
                  </li>
                );
              })}
            </ol>
          </>
        )}
      </div>
    </div>
  );
}

export default definePluginApp((app) => {
  app.slots.navPanel({
    id: "aios-course",
    title: "AIOS course",
    icon: "GraduationCap",
    path: "aios-course",
    component: CoursePage,
  });
});
