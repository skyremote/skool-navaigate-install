# Module 9 · Working methods: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 9.1 · Interview me, then write the spec before any code

**What it does:** Makes a small practice project, then writes a glossary (the words you agree on) and a spec whose every "Done when" line is a command the agent can run.

**How you know it worked:** `aios-methods glossary check` ends with `0 problems`, and `aios-methods spec check` ends with `0 problem(s)`.

~~~text
The feature I want (edit these lines before you send):
- Project: a small invoice list for Acme Studio.
- Feature: show how many days each unpaid invoice is overdue.
- Done when: an invoice 10 days past its due date shows "10 days overdue"; a paid invoice shows nothing.

Set up module 9, part one: agree the words and write the spec before any code.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-methods@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-methods/*/bin | tail -1)/aios-methods"`. Below, `aios-methods` means that full path.

1. If this folder has no practice project yet, create `50_projects/acme-invoices` with a tiny Python file `invoices.py` (a list of three sample invoices with a number, a due date and a paid flag, and a function that prints them) and a test file `test_invoices.py` with one passing test. In that folder run `git init -q && git add -A && git commit -qm Start`. Work inside that folder from now on.
2. Interview yourself on the feature above: write the three questions you would ask me and the answer my lines above give. If one of them truly needs me, ask it and stop.
3. Run `aios-methods glossary init`, then `aios-methods glossary add "<Term>" "<what it means here>" --avoid "<other words for it>"` for each word the interview pinned down (at least "Overdue" and "Paid").
4. Run `aios-methods glossary check`. It must end with `0 problems`.
5. Run `aios-methods spec new days-overdue`, then fill `docs/specs/days-overdue.md`. Every line under "Done when" is a command in backticks that the agent can run, for example `python3 -m unittest`. Write `None` under "Open questions" only if nothing is open.
6. Run `aios-methods spec check docs/specs/days-overdue.md`. It must end with `0 problem(s)`.
7. Commit: `git add GLOSSARY.md docs/specs && git commit -m "Spec for days-overdue"`.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m09-spec_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m09-spec_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 9.2 · Build the feature in its own worktree, then merge it

**What it does:** Builds the feature from the spec in a separate copy of the project (a worktree), runs each "Done when" check until all pass, merges it, and cleans up.

**How you know it worked:** Every "Done when" command passes, the feature is merged, and `aios-methods worktree list` shows only the main folder.

~~~text
Module 9, part two. Build the feature from its spec in its own worktree, then merge it. The spec must already exist in `50_projects/acme-invoices/docs/specs/days-overdue.md` (if not, stop and tell me to run prompt 9.1 first).

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-methods@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-methods/*/bin | tail -1)/aios-methods"`. Below, `aios-methods` means that full path.

1. In `50_projects/acme-invoices`, run `aios-methods worktree new days-overdue`. Show the folder and branch it made, and `aios-methods worktree list`.
2. In the new worktree folder, take the spec's "Done when" lines one at a time. For each: write the code and a test, run the line's command, show the real output, and commit only when it passes. If a check fails, fix that one thing and run it again.
3. When every "Done when" command passes, go back to the main folder and run `git merge work/days-overdue`.
4. Run `aios-methods worktree done days-overdue`. If it says "not merged" or "Uncommitted changes", fix that and run it again.
5. Run `aios-methods worktree list`. Only the main folder should be left. Run the tests once more in the main folder.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m09-worktree-build_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m09-worktree-build_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 9.3 · Every Monday, summarise last week's threads

**What it does:** Creates a bb automation that runs every Monday at 8am and writes a one-page summary of last week's threads, shown inline. It runs it once now so you see the result.

**How you know it worked:** `bb automation list` shows the automation with its next run time, and the first summary shows inline.

~~~text
Every Monday at 8am, write me a one-page summary of last week's threads and show it inline.

Here is how:
1. Read `bb automation create --help` so you use the right options.
2. Write the job's prompt to `80_aios/automations/weekly-summary_v1.md`: "List last week's threads in this bb project with `bb thread list --json` (last seven days only). Write a one-page summary to 80_aios/reports/weekly-summary_<date>.html: what was done, what is still open, what needs me. Show it inline with ::inline-vis."
3. Create the automation for this project: an agent run on a schedule of every Monday at 08:00 in my time zone, with that prompt, using Claude. Show me the command and its output.
4. Run `bb automation list` and show its name and next run time.
5. Run it once now with `bb automation run <its id>` and tell me where the first summary appears.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m09-weekly-automation_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m09-weekly-automation_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
