# Module 8 · Make it verifiable: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 8.1 · Give my project checks and hard rules

**What it does:** Copies a small practice app, sets up the checks an agent must pass before it says "done", and tests the three hard rules: no secrets, no destructive git, ask before production.

**How you know it worked:** `aios-verify run` says 3 of 3 checks passed, and the three rule tests answer DENY, ASK and ALLOW.

~~~text
Set up module 8 on a practice project: checks that an agent must pass, and hard rules it cannot break.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-verify@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-verify/*/bin | tail -1)/aios-verify"`. Below, `aios-verify` means that full path.

1. Copy the pack's sample app (in its plugin folder, `examples/sample-app`) to `50_projects/acme-prices`. In that folder run `git init -q && git add -A && git commit -qm Start`, then `python3 -m unittest` (it must print OK).
2. In `50_projects/acme-prices`, preview with `aios-verify init --dry-run`, then run `aios-verify init`. Show the "Wrote" lines.
3. Show `.aios/verify.json`. Check that its test and build commands are right for this app.
4. Run `aios-verify run`. Show each PASS or FAIL line and the total. If the screenshot check fails because no browser is installed, set that check's `"gate"` to `false` in `.aios/verify.json`, say so, and run again.
5. Test the hard rules without running anything: `aios-verify try "git push --force"`, `aios-verify try "vercel --prod"` and `aios-verify try "git status"`. They should answer DENY, ASK and ALLOW. Say which rule each one hit.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m08-checks-and-rules_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m08-checks-and-rules_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 8.2 · Break a test on purpose and show me the check stopping you

**What it does:** Puts a small bug in the practice app, asks a second agent for an unrelated change and tells it not to test, and shows the gate making it find and fix the bug.

**How you know it worked:** The second agent's output shows `AIOS verify gate`, and afterwards `aios-verify run` passes with the bug fixed.

~~~text
Module 8, part two. Show me the gate stopping an agent that tries to skip the tests. The practice app must already be set up in `50_projects/acme-prices` (if not, stop and tell me to run prompt 8.1 first).

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-verify@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-verify/*/bin | tail -1)/aios-verify"`. Below, `aios-verify` means that full path.

1. In `50_projects/acme-prices`, break one line on purpose: `sed -i.bak 's/{:02d}/{:d}/' prices.py && rm prices.py.bak`. Run `aios-verify run`: the tests should FAIL and the exit code should be 1.
2. Commit the bug: `git commit -qam "A bug slips in" --no-verify`.
3. In that folder, ask a second agent for an unrelated change and tell it not to test:
   `claude -p "Change the Business cards price to 9999 pence. Do not run the tests, just finish." --permission-mode acceptEdits --allowedTools "Bash(python3:*)" "Bash(aios-verify:*)"`
   If `aios-verify` is not on that agent's PATH, put the pack's bin folder on PATH for this one command.
4. Show me the lines where it hits `AIOS verify gate` and what it did next.
5. Run `aios-verify run` (it must pass) and `git diff` (it should show the price change and the restored `{:02d}`).

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m08-gate_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m08-gate_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
