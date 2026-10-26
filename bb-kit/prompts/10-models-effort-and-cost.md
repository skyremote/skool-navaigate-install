# Module 10 · Models, effort and cost: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 10.1 · Pick the right model and effort, and set medium as my default

**What it does:** Shows which model, effort and login each harness uses and where each setting comes from, then sets medium effort as your default.

**How you know it worked:** `models-check` shows `effort medium` for Claude Code, and the report lists the three commands you type yourself.

~~~text
For each kind of job, tell me the cheapest model and effort that will do it well, and why. Then show me which model I am on now and set medium effort as my default.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-models@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-models/*/bin | tail -1)/models-check"`. Below, `models-check` means that full path.

1. Run `models-check`. For each harness, show me the login, model and effort lines, and where each was set. If it warns that `ANTHROPIC_API_KEY` is set, tell me plainly that this terminal bills the paid API, and ask whether I meant that.
2. Set my Claude Code effort to medium the way the pack's `models` skill says. Change only that one setting, and back up the settings file first.
3. Run `models-check` again and show the effort line for Claude Code. It should say medium.
4. Explain the split in four short lines: Sonnet for daily building, Opus for planning, hard bugs and reviews, Haiku for summaries and volume work, and Codex for GPT models.
5. List the commands I type myself in Claude Code, because an agent cannot run them for me: `/model sonnet`, `/effort medium`, `/advisor opus` and `/usage`. Say in one line what each does.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m10-models_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m10-models_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 10.2 · How much of my Claude week have I used?

**What it does:** Reads your plan's usage windows (the five-hour session and the week) and says in one line whether your week will last until the reset.

**How you know it worked:** The report shows each window's percentage and reset time, and one plain-English answer.

~~~text
How much of my Claude week have I used, and will it last until the reset?

Here is how:
1. Run `bb settings usage` and show me each usage window for Claude: how much is used and when it resets.
2. Work out a simple forecast: the share used so far against the share of the week gone. Say in one line whether it will last.
3. If it will not last, give me two plain options: lower effort for routine jobs, or a second login in the account pool (prompt 10.3).
4. Tell me that with BB Overlay I can hover the usage line under the chat box to see the same windows as charts.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m10-usage_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m10-usage_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 10.3 · Add my second Claude login to the account pool

**What it does:** Switches on bb's account pool and starts adding a second Claude login, so bb moves new chats to it when the first plan runs out. You finish the sign-in in your browser.

**How you know it worked:** `bb pool account list` shows both accounts enabled after you sign in.

~~~text
Add my second Claude login to the account pool and show me both accounts and how much each has left. If I do not have a second Claude subscription, say so and stop.

Here is how:
1. Read `bb pool --help` and `bb pool account add --help`.
2. Switch the pool on: `bb plugin enable account-pool`. It changes bb's settings: I allow that for this command, so if the sandbox blocks it, run it outside the sandbox.
3. Run `bb pool status` and `bb pool account list` and show me what is there now.
4. Start adding the second login: `bb pool account add --provider claude --login`. It prints a sign-in link and a session id. Do not try to sign in for me. Give me the link and the exact next command, `bb pool account login-complete --session <id> --code-stdin`, to run with the code from my browser.
5. Tell me how to check it afterwards: `bb pool account list` shows both accounts enabled, and `bb pool routing claude` shows the order. Lower priority numbers run first.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m10-account-pool_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m10-account-pool_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
