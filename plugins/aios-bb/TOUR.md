# Tour: module 4, bb as the cockpit

Run this inside your own AIOS folder, with the bb app open. Each step says what to do, the command, what you should
see, and how to check it. Use `aios-bb` in a terminal (in Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/aios-bb"`).

## Step 1. Check bb is ready
- Do: check bb, its harnesses and your folder.
- Command: `aios-bb doctor`
- You should see: OK for "bb is running", Claude Code, Codex and git. A WARN about no kanban plugin is fine.
- Check: the command exits 0. If bb is not found, run `bb settings cli-command install` inside bb first.

## Step 2. Make the folder a git repository (once)
- Do: only if doctor warned "not a git repository".
- Command: `git init && git add -A && git commit -m "Start"`
- You should see: a commit summary.
- Check: `git log --oneline -1` prints one line.

## Step 3. Create the bb project and the board
- Do: preview, then create.
- Command: `aios-bb setup --dry-run --name "<your project name>"`, then `aios-bb setup --name "<your project name>"`
- You should see: "Created the bb project" and "Created the sections: Backlog, In progress, Review, Done".
- Check: the project is in the bb sidebar, and running setup again says "Kept it".

## Step 4. Start two threads side by side
- Do: write a small real job into `brief.md`, ending with "When there is something for me to check, run: aios-bb card review --note '<what>'". Give it to both harnesses.
- Command: `aios-bb hand "<job>" --prompt-file brief.md --provider claude`, then the same with `--provider codex` and a different title
- You should see: two "Started ... It is in In progress." lines, and two new threads in bb.
- Check: in bb, each thread's environment says Worktree. Open them in split panes.

## Step 5. Move a card to Review
- Do: when a thread has something to check, move its card (the agent can do this itself).
- Command: `aios-bb card review --thread "<thread title or id>" --note "<what to check>"`
- You should see: "Moved the thread into the Review section" (or "on the kanban board" with a kanban plugin).
- Check: the thread sits under Review in the sidebar.

## Step 6. Open an inline artifact
- Do: in one of the threads, ask for the result as an HTML page shown inline.
- Command: (in the thread) "Write the result to reports/result_v1.html and show it inline with ::inline-vis."
- You should see: the page rendered inside the chat.
- Check: the line `::inline-vis{file="reports/result_v1.html"}` sits on its own line, outside a code block.

## Step 7. Run a slash command
- Do: type `/` in the message box, then filter.
- Command: `/bb-daily`
- You should see: the daily loop starting in that thread.
- Check: optional, make your own: `.bb/skills/<name>/SKILL.md` shows up as `/<name>` in new threads of this project.

## Step 8. Run the daily loop
- Do: start the day, review, close.
- Command: `aios-bb today`, then `aios-bb card done --thread "<thread title or id>"`, then `aios-bb close --archive-done`
- You should see: Waiting, Review, In progress and Backlog lists, then "Archived N finished thread(s) from Done."
- Check: archived threads are gone from the sidebar but `bb thread search "<word>"` still finds them.

## Next
Add a second Mac under Settings, Machines if you have one, and `bb account login` for remote access from your phone.
Then type `/aios` for module 5.
