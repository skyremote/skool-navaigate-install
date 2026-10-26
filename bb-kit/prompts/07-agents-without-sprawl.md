# Module 7 · Agents without sprawl: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 7.1 · Meet the crew and write a brief

**What it does:** Shows the three read-only helper agents, lists any agents you already have, and writes a brief (a clear hand-over note) that passes its check.

**How you know it worked:** `aios-agent brief check` says READY, and the brief's "Done when" line names a count, a file or a command.

~~~text
Set up module 7: when a helper agent is worth it, and how to brief one.

The job I might hand over (edit this line): review `20_offers/` and list anything a new client would find unclear.

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-agents@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-agents/*/bin | tail -1)/aios-agent"`. Below, `aios-agent` means that full path.

1. Run `aios-agent crew`. Show the three agents and their tools. Point out that none of them can edit files or run commands.
2. List the agents I already have: `ls ~/.claude/agents .claude/agents 2>/dev/null`. For each one, say which reason it has: parallel work, a separate workspace, or a job whose output would flood the chat. Say "no reason" where none fits. Do not delete anything.
3. Make a brief for the job above: `aios-agent brief new --out briefs/review-offers_v1.md`.
4. Run `aios-agent brief check briefs/review-offers_v1.md`. It should say NOT READY on the empty template.
5. Fill in each part of the brief for the job above: Objective, Format, Context, Tools, Boundaries and Stop. The "Done when" line must name a count, a file or a command.
6. Run the check again. It must say READY.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m07-crew-and-brief_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m07-crew-and-brief_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 7.2 · Compare one agent with one agent plus a reviewer

**What it does:** Runs the same small coding task twice, once alone and once with a reviewer agent, and compares time, tokens and what the reviewer caught. It uses your own plan.

**How you know it worked:** Both copies pass their tests, and `aios-agent compare` shows 0 sub-agents against 1.

~~~text
Run the module 7 comparison: the same task done by one agent alone, and by one agent with a reviewer.

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-agents@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-agents/*/bin | tail -1)/aios-agent"`. Below, `aios-agent` means that full path.

1. Copy the sample task twice: from the pack's plugin folder, copy `examples/compare-task` to `50_projects/compare-one` and to `50_projects/compare-two`. Check that `python3 -m unittest` prints OK in `50_projects/compare-one`.
2. Read `50_projects/compare-one/TASK.md`. In `50_projects/compare-one`, run its "Run 1" command. Save the JSON it writes inside that folder as `one-loop.json` (change the output path in the command if needed). Wait for it to finish.
3. In `50_projects/compare-two`, run the "Run 2" command, with the `Agent` tool allowed. Save its JSON as `with-reviewer.json` in that folder. Wait for it to finish.
4. Run `python3 -m unittest` in both folders. Both must print OK.
5. Run `aios-agent compare 50_projects/compare-one/one-loop.json 50_projects/compare-two/with-reviewer.json` and show the table. If the second run shows 0 sub-agents, the `Agent` tool was not allowed: fix it and run step 3 again.
6. Run `aios-agent result 50_projects/compare-two/with-reviewer.json` and tell me in one line what the reviewer caught that the first run missed. Then give me your view: was the reviewer worth it for this kind of change?

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m07-compare_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m07-compare_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
