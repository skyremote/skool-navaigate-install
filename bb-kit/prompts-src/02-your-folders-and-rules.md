# 02 · Your folders and your rules
pack: aios-rules
cmd: aios-rules

## 2.1 · Set up your folders and your AGENTS.md
what: Creates the folder map and one short AGENTS.md (the rules file every agent reads), filled in with your business details.
check: The report shows `CLAUDE CODE: OK` from the budget check, AGENTS.md under 150 lines with no gaps left, and CLAUDE.md pointing at AGENTS.md.
~~~
About my business (edit these lines before you send):
- Business: Acme Studio, a two-person brand design studio in Leeds.
- Owner: Sam Lee.
- What we do: logos, websites and print for small companies.
- Who buys: owners of small companies with 2 to 50 staff.
- Never: send anything to a client without my approval.

Set up module 2, my folders and my rules, in this folder.

<<INSTALL>>

1. Run `ls -A`. If this folder already has my own top-level folders, add `--no-folders` to the commands in steps 2 and 3.
2. Preview the set-up: `aios-rules init --business "<Business>" --owner "<Owner>" --dry-run`, using my details above. Show me the CREATED and KEPT lines, then check with `ls -A` that nothing new exists yet.
3. Run the same command without `--dry-run`.
4. Fill in AGENTS.md from my details: replace every gap written as two curly brackets. For "Checks this folder can run", keep the rules budget line and delete the example line. For "Gotchas", delete the example line. Add my "Never" line to "Rules that never break".
5. Check: `grep -n "{{" AGENTS.md` prints nothing, `wc -l AGENTS.md` is under 150, and `cat CLAUDE.md` prints `@AGENTS.md`. If my old CLAUDE.md was kept, show me the one line to add at the top, and do not add it yourself.
6. Run `aios-rules check`. It must say `CLAUDE CODE: OK`.
7. Run `aios-rules cursor-rules`, then `aios-rules check --harness all`, and show the result for each harness.

<<RULES>>

<<FINISH m02-folders-and-rules>>
~~~

## 2.2 · Add a rule for one folder and prove Claude reads it
what: Adds a rule that loads only when Claude works in your offers folder, then asks a fresh Claude, without opening files, where invoices go.
check: The new rule shows under "On demand" in the budget check, and the fresh Claude quotes the `30_finance/` line from your AGENTS.md.
~~~
Module 2, part two. My folders and AGENTS.md are already set up in this folder (if they are not, stop and tell me to run prompt 2.1 first).

<<INSTALL>>

1. Show me the top of the finance rule: `head -5 .claude/rules/finance.md`. Explain in one sentence when it loads.
2. Make a rule for my offers folder, which has none yet: run `ls .claude/rules` first. If `offers.md` already exists, keep it and skip to step 3. Otherwise copy `.claude/rules/finance.md` to `.claude/rules/offers.md`, change its path to `20_offers/**`, and replace its rule lines with two short rules: "Every price shows its currency and the date it was set." and "Never send an offer to a client; drafts only."
3. Run `aios-rules check`. Show that `offers.md` is listed under "On demand", not in the always-loaded list.
4. Prove a fresh Claude reads AGENTS.md: run `claude -p "Without reading any file, quote the line in your instructions that says where invoices go."` and show the answer. It should quote the `30_finance/` line.

<<RULES>>

<<FINISH m02-folder-rule>>
~~~

## 2.3 · Run your first monthly rules audit
what: Runs the monthly audit, which reads your rules and writes a dated report. It takes a few minutes and uses your own Claude plan.
check: A file `80_aios/audits/<date>_rules-audit_v1.md` exists, and each part says ok, unavailable, failed or skipped.
~~~
Run my monthly rules audit for this folder. My folders and AGENTS.md are already set up (if not, stop and tell me to run prompt 2.1 first).

<<INSTALL>>

1. Run `aios-rules audit`. It takes a few minutes. Wait for it.
2. Open the file it wrote under `80_aios/audits/`. Tell me the status of each part.
3. If a part says `/skill-doctor` is unavailable, tell me that I can run `/skill-doctor` myself in Claude Code later and paste its report under that heading. Do not do it for me.
4. Check with `git status` or `ls -l` that nothing in my rules changed: the audit only reads.
5. Suggest the first working day of each month as my audit day, and write that date into section 4 of the audit file.

<<RULES>>

<<FINISH m02-rules-audit>>
~~~
