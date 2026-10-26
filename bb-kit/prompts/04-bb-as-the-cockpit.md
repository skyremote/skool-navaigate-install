# Module 4 · bb as the cockpit: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 4.1 · Make this folder your bb cockpit

**What it does:** Checks bb, makes this folder a git repository if it is not one, and creates the bb project and its four lanes: Backlog, In progress, Review, Done.

**How you know it worked:** `aios-bb doctor` exits 0, the four lanes show in the bb sidebar, and running set-up again says "Kept it".

~~~text
Set up module 4: make this folder my bb cockpit. This chat runs inside bb.

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-bb@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-bb/*/bin | tail -1)/aios-bb"`. Below, `aios-bb` means that full path.

1. Run `aios-bb doctor`. Show me each line. A warning about no kanban plugin is fine.
2. If doctor says this folder is not a git repository, run `git init && git add -A && git commit -m "Start"`, then show `git log --oneline -1`.
3. Preview: `aios-bb setup --dry-run --name "My AIOS"`. Then run `aios-bb setup --name "My AIOS"`. If a bb project for this folder already exists, setup keeps it; that is correct.
4. Run `aios-bb setup --name "My AIOS"` once more and show that it says "Kept it".
5. Run `bb thread section list --json` and show that Backlog, In progress, Review and Done exist.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m04-cockpit_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m04-cockpit_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 4.2 · Hand one job to two agents side by side

**What it does:** Writes one small real job as a brief, hands it to two new threads that each work in their own copy of the folder, and puts them in the In progress lane.

**How you know it worked:** Two new threads appear in the bb sidebar under In progress, each in its own worktree (a separate copy of the folder).

~~~text
Module 4, part two. Hand one small job to two agents at once, so I can compare their work. The cockpit is already set up (if not, stop and tell me to run prompt 4.1 first).

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-bb@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-bb/*/bin | tail -1)/aios-bb"`. Below, `aios-bb` means that full path.

1. Write `brief.md` in this folder with this job: "Write a one-page list of our services in `20_offers/services_v1.md`: three services, one line each on who it is for and what they get. When there is something for me to check, run: aios-bb card review --note 'services list ready'". Commit it: `git add brief.md && git commit -m "Brief: services list"`.
2. Run `aios-bb hand "Services list (Claude)" --prompt-file brief.md --provider claude`.
3. Check whether Codex is installed and signed in with `codex login status`. If it is, run `aios-bb hand "Services list (Codex)" --prompt-file brief.md --provider codex`. If not, hand it to Claude a second time with the title "Services list (Claude 2)", and tell me Codex was not available.
4. Show me the two "Started ..." lines. Run `bb thread list --json` and show the two new threads with their status.
5. Tell me how to open them side by side in bb: click each thread in the sidebar, or open one in a split pane.

Do not wait for the two threads to finish. They will move themselves to Review.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m04-two-agents_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m04-two-agents_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 4.3 · Run the daily loop

**What it does:** Shows today's board (waiting, review, in progress, backlog), closes what is finished and archives it.

**How you know it worked:** The report shows the four lists and how many finished threads were archived. Archived threads can still be found with `bb thread search`.

~~~text
Run my daily loop in bb for this folder. The cockpit is already set up (if not, stop and tell me to run prompt 4.1 first).

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-bb@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-bb/*/bin | tail -1)/aios-bb"`. Below, `aios-bb` means that full path.

1. Run `aios-bb today` and show me the Waiting, Review, In progress and Backlog lists.
2. For each thread in Review, show its title and the note on its card, and read the file it made (for example `20_offers/services_v1.md`). Tell me in one line whether it did the job.
3. Do not mark anything as done yourself. List the commands I can run for the ones I accept: `aios-bb card done --thread "<title>"`.
4. Run `aios-bb close` (without `--archive-done`) and show me the end-of-day summary.
5. Tell me that `aios-bb close --archive-done` archives everything in Done, and that `bb thread search "<word>"` still finds archived threads.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m04-daily-loop_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m04-daily-loop_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
