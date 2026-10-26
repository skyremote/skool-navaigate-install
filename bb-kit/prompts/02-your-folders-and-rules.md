# Module 2 · Your folders and your rules: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 2.1 · Set up your folders and your AGENTS.md

**What it does:** Creates the folder map and one short AGENTS.md (the rules file every agent reads), filled in with your business details.

**How you know it worked:** The report shows `CLAUDE CODE: OK` from the budget check, AGENTS.md under 150 lines with no gaps left, and CLAUDE.md pointing at AGENTS.md.

~~~text
About my business (edit these lines before you send):
- Business: Acme Studio, a two-person brand design studio in Leeds.
- Owner: Sam Lee.
- What we do: logos, websites and print for small companies.
- Who buys: owners of small companies with 2 to 50 staff.
- Never: send anything to a client without my approval.

Set up module 2, my folders and my rules, in this folder.

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-rules@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-rules/*/bin | tail -1)/aios-rules"`. Below, `aios-rules` means that full path.

1. Run `ls -A`. If this folder already has my own top-level folders, add `--no-folders` to the commands in steps 2 and 3.
2. Preview the set-up: `aios-rules init --business "<Business>" --owner "<Owner>" --dry-run`, using my details above. Show me the CREATED and KEPT lines, then check with `ls -A` that nothing new exists yet.
3. Run the same command without `--dry-run`.
4. Fill in AGENTS.md from my details: replace every gap written as two curly brackets. For "Checks this folder can run", keep the rules budget line and delete the example line. For "Gotchas", delete the example line. Add my "Never" line to "Rules that never break".
5. Check: `grep -n "{{" AGENTS.md` prints nothing, `wc -l AGENTS.md` is under 150, and `cat CLAUDE.md` prints `@AGENTS.md`. If my old CLAUDE.md was kept, show me the one line to add at the top, and do not add it yourself.
6. Run `aios-rules check`. It must say `CLAUDE CODE: OK`.
7. Run `aios-rules cursor-rules`, then `aios-rules check --harness all`, and show the result for each harness.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m02-folders-and-rules_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m02-folders-and-rules_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 2.2 · Add a rule for one folder and prove Claude reads it

**What it does:** Adds a rule that loads only when Claude works in one folder, then asks a fresh Claude, without opening files, where invoices go.

**How you know it worked:** The new rule shows under "On demand" in the budget check, and the fresh Claude quotes the `30_finance/` line from your AGENTS.md.

~~~text
Module 2, part two. My folders and AGENTS.md are already set up in this folder (if they are not, stop and tell me to run prompt 2.1 first).

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-rules@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-rules/*/bin | tail -1)/aios-rules"`. Below, `aios-rules` means that full path.

1. Show me the top of the finance rule: `head -5 .claude/rules/finance.md`. Explain in one sentence when it loads.
2. Make a rule for my content folder: copy `.claude/rules/finance.md` to `.claude/rules/my-content.md`, change its path to `40_content/**`, and replace its lines with two short rules: "Every post has a draft date in its file name." and "Never publish; drafts only."
3. Run `aios-rules check`. Show that `my-content.md` is listed under "On demand", not in the always-loaded list.
4. Prove a fresh Claude reads AGENTS.md: run `claude -p "Without reading any file, quote the line in your instructions that says where invoices go."` and show the answer. It should quote the `30_finance/` line.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m02-folder-rule_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m02-folder-rule_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 2.3 · Run your first monthly rules audit

**What it does:** Runs the monthly audit, which reads your rules and writes a dated report. It takes a few minutes and uses your own Claude plan.

**How you know it worked:** A file `80_aios/audits/<date>_rules-audit_v1.md` exists, and each part says ok, unavailable, failed or skipped.

~~~text
Run my monthly rules audit for this folder. My folders and AGENTS.md are already set up (if not, stop and tell me to run prompt 2.1 first).

Step 0, get the pack. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-rules@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-rules/*/bin | tail -1)/aios-rules"`. Below, `aios-rules` means that full path.

1. Run `aios-rules audit`. It takes a few minutes. Wait for it.
2. Open the file it wrote under `80_aios/audits/`. Tell me the status of each part.
3. If a part says `/skill-doctor` is unavailable, tell me that I can run `/skill-doctor` myself in Claude Code later and paste its report under that heading. Do not do it for me.
4. Check with `git status` or `ls -l` that nothing in my rules changed: the audit only reads.
5. Suggest the first working day of each month as my audit day, and write that date into section 4 of the audit file.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m02-rules-audit_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m02-rules-audit_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
