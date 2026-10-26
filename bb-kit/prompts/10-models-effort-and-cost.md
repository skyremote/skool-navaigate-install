# Module 10 · Models, effort and cost: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 10.1 · See which model you are on and set medium effort

**What it does:** Shows which model, effort and login each harness uses and where each setting comes from, then sets medium effort as your default.

**How you know it worked:** `models-check` shows `effort medium` for Claude Code, and the report lists the three commands you type yourself.

~~~text
Set up module 10 on this computer: see my models, then set a sensible default.

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-models@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-models/*/bin | tail -1)/models-check"`. Below, `models-check` means that full path.

1. Run `models-check`. For each harness, show me the login, model and effort lines, and where each was set. If it warns that `ANTHROPIC_API_KEY` is set, tell me plainly that this terminal bills the paid API, and ask whether I meant that.
2. Set my Claude Code effort to medium the way the pack's `models` skill says. Change only that one setting, and back up the settings file first.
3. Run `models-check` again and show the effort line for Claude Code. It should say medium.
4. Explain the split in four short lines: Sonnet for daily building, Opus for planning, hard bugs and reviews, Haiku for summaries and volume work, and Codex for GPT models.
5. List the commands I type myself in Claude Code, because an agent cannot run them for me: `/model sonnet`, `/effort medium`, `/advisor opus` and `/usage`. Say in one line what each does.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m10-models_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m10-models_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 10.2 · Prepare a second login (only if you have a second plan)

**What it does:** Prepares a second Claude login in its own folder, with a short command to start it, so you can switch when one plan runs out. You do the sign-in yourself.

**How you know it worked:** The report shows the sign-in command and the alias line to add. After you sign in, `models-check` counts two logins.

~~~text
I have a second Claude subscription. Prepare a second login called "work" so I can switch to it when my main plan runs out.

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-models@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-models/*/bin | tail -1)/models-check"`. Below, `models-check` means that full path.

1. Run `models-check login add work`. Show me the sign-in command and the alias line it prints.
2. Do not run the sign-in yourself: it opens a browser and needs me. Tell me to run it in a terminal.
3. Tell me where to add the alias line (`~/.zshrc` on a Mac) and to open a new terminal after.
4. Tell me how to check it: run the alias, then `/status`, and run `models-check`, which should end with `Claude logins ready for failover: 2`.
5. Remind me that plugins are per login, so I install my AIOS packs inside the second login too.

If I do not have a second subscription, this prompt is not for me: say so and stop.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m10-second-login_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m10-second-login_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
