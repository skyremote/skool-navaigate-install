# 09 · Working methods
pack: aios-methods
cmd: aios-methods

## 9.1 · Interview me, then write the spec before any code
what: Makes a small practice project, then writes a glossary (the words you agree on) and a spec whose every "Done when" line is a command the agent can run.
check: `aios-methods glossary check` ends with `0 problems`, and `aios-methods spec check` ends with `0 problem(s)`.
~~~
The feature I want (edit these lines before you send):
- Project: a small invoice list for Acme Studio.
- Feature: show how many days each unpaid invoice is overdue.
- Done when: an invoice 10 days past its due date shows "10 days overdue"; a paid invoice shows nothing.

Set up module 9, part one: agree the words and write the spec before any code.

<<INSTALL>>

1. If this folder has no practice project yet, create `50_projects/acme-invoices` with a tiny Python file `invoices.py` (a list of three sample invoices with a number, a due date and a paid flag, and a function that prints them) and a test file `test_invoices.py` with one passing test. In that folder run `git init -q && git add -A && git commit -qm Start`. Work inside that folder from now on.
2. Interview yourself on the feature above: write the three questions you would ask me and the answer my lines above give. If one of them truly needs me, ask it and stop.
3. Run `aios-methods glossary init`, then `aios-methods glossary add "<Term>" "<what it means here>" --avoid "<other words for it>"` for each word the interview pinned down (at least "Overdue" and "Paid").
4. Run `aios-methods glossary check`. It must end with `0 problems`.
5. Run `aios-methods spec new days-overdue`, then fill `docs/specs/days-overdue.md`. Every line under "Done when" is a command in backticks that the agent can run, for example `python3 -m unittest`. Write `None` under "Open questions" only if nothing is open.
6. Run `aios-methods spec check docs/specs/days-overdue.md`. It must end with `0 problem(s)`.
7. Commit: `git add GLOSSARY.md docs/specs && git commit -m "Spec for days-overdue"`.

<<RULES>>

<<FINISH m09-spec>>
~~~

## 9.2 · Build the feature in its own worktree, then merge it
what: Builds the feature from the spec in a separate copy of the project (a worktree), runs each "Done when" check until all pass, merges it, and cleans up.
check: Every "Done when" command passes, the feature is merged, and `aios-methods worktree list` shows only the main folder.
~~~
Module 9, part two. Build the feature from its spec in its own worktree, then merge it. The spec must already exist in `50_projects/acme-invoices/docs/specs/days-overdue.md` (if not, stop and tell me to run prompt 9.1 first).

<<INSTALL>>

1. In `50_projects/acme-invoices`, run `aios-methods worktree new days-overdue`. Show the folder and branch it made, and `aios-methods worktree list`.
2. In the new worktree folder, take the spec's "Done when" lines one at a time. For each: write the code and a test, run the line's command, show the real output, and commit only when it passes. If a check fails, fix that one thing and run it again.
3. When every "Done when" command passes, go back to the main folder and run `git merge work/days-overdue`.
4. Run `aios-methods worktree done days-overdue`. If it says "not merged" or "Uncommitted changes", fix that and run it again.
5. Run `aios-methods worktree list`. Only the main folder should be left. Run the tests once more in the main folder.

<<RULES>>

<<FINISH m09-worktree-build>>
~~~

## 9.3 · Every Monday, summarise last week's threads
what: Creates a bb automation that runs every Monday at 8am and writes a one-page summary of last week's threads, shown inline. It runs it once now so you see the result.
check: `bb automation list` shows the automation with its next run time, and the first summary shows inline.
~~~
Every Monday at 8am, write me a one-page summary of last week's threads and show it inline.

Here is how:
1. Read `bb automation create --help` so you use the right options.
2. Write the job's prompt to `80_aios/automations/weekly-summary_v1.md`: "List last week's threads in this bb project with `bb thread list --json` (last seven days only). Write a one-page summary to 80_aios/reports/weekly-summary_<date>.html: what was done, what is still open, what needs me. Show it inline with ::inline-vis."
3. Create the automation for this project: an agent run on a schedule of every Monday at 08:00 in my time zone, with that prompt, using Claude. Show me the command and its output.
4. Run `bb automation list` and show its name and next run time.
5. Run it once now with `bb automation run <its id>` and tell me where the first summary appears.

<<RULES>>

<<FINISH m09-weekly-automation>>
~~~
