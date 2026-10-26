# 04 · bb as the cockpit
pack: aios-bb
cmd: aios-bb

## 4.1 · Make this folder your bb cockpit
what: Checks bb, makes this folder a git repository if it is not one, and creates the bb project and its four lanes: Backlog, In progress, Review, Done.
check: `aios-bb doctor` exits 0, the four lanes show in the bb sidebar, and running set-up again says "Kept it".
~~~
Set up module 4: make this folder my bb cockpit. This chat runs inside bb.

<<INSTALL>>

1. Run `aios-bb doctor`. Show me each line. A warning about no kanban plugin is fine.
2. If doctor says this folder is not a git repository, run `git init && git add -A && git commit -m "Start"`, then show `git log --oneline -1`.
3. Preview: `aios-bb setup --dry-run --name "My AIOS"`. Then run `aios-bb setup --name "My AIOS"`. If a bb project for this folder already exists, setup keeps it; that is correct.
4. Run `aios-bb setup --name "My AIOS"` once more and show that it says "Kept it".
5. Run `bb thread section list --json` and show that Backlog, In progress, Review and Done exist.

<<RULES>>

<<FINISH m04-cockpit>>
~~~

## 4.2 · Hand one job to two agents side by side
what: Writes one small real job as a brief, hands it to two new threads that each work in their own copy of the folder, and puts them in the In progress lane.
check: Two new threads appear in the bb sidebar under In progress, each in its own worktree (a separate copy of the folder).
~~~
Module 4, part two. Hand one small job to two agents at once, so I can compare their work. The cockpit is already set up (if not, stop and tell me to run prompt 4.1 first).

<<INSTALL>>

1. Write `brief.md` in this folder with this job: "Write a one-page list of our services in `20_offers/services_v1.md`: three services, one line each on who it is for and what they get. When there is something for me to check, run: aios-bb card review --note 'services list ready'". Commit it: `git add brief.md && git commit -m "Brief: services list"`.
2. Run `aios-bb hand "Services list (Claude)" --prompt-file brief.md --provider claude`.
3. Check whether Codex is installed and signed in with `codex login status`. If it is, run `aios-bb hand "Services list (Codex)" --prompt-file brief.md --provider codex`. If not, hand it to Claude a second time with the title "Services list (Claude 2)", and tell me Codex was not available.
4. Show me the two "Started ..." lines. Run `bb thread list --json` and show the two new threads with their status.
5. Tell me how to open them side by side in bb: click each thread in the sidebar, or open one in a split pane.

Do not wait for the two threads to finish. They will move themselves to Review.

<<RULES>>

<<FINISH m04-two-agents>>
~~~

## 4.3 · Run the daily loop
what: Shows today's board (waiting, review, in progress, backlog), closes what is finished and archives it.
check: The report shows the four lists and how many finished threads were archived. Archived threads can still be found with `bb thread search`.
~~~
Run my daily loop in bb for this folder. The cockpit is already set up (if not, stop and tell me to run prompt 4.1 first).

<<INSTALL>>

1. Run `aios-bb today` and show me the Waiting, Review, In progress and Backlog lists.
2. For each thread in Review, show its title and the note on its card, and read the file it made (for example `20_offers/services_v1.md`). Tell me in one line whether it did the job.
3. Do not mark anything as done yourself. List the commands I can run for the ones I accept: `aios-bb card done --thread "<title>"`.
4. Run `aios-bb close` (without `--archive-done`) and show me the end-of-day summary.
5. Tell me that `aios-bb close --archive-done` archives everything in Done, and that `bb thread search "<word>"` still finds archived threads.

<<RULES>>

<<FINISH m04-daily-loop>>
~~~
