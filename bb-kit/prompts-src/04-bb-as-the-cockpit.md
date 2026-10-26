# 04 · bb as the cockpit
pack: aios-bb
cmd: aios-bb

## 4.1 · Turn this folder into my bb cockpit
what: Checks bb, makes this folder a git repository if it is not one, and creates the bb project and its four lanes: Backlog, In progress, Review, Done.
check: `aios-bb doctor` exits 0, the four lanes show in the bb sidebar, and running set-up again says "Kept it".
~~~
Turn this folder into my bb cockpit: a git history, and a board with Backlog, In progress, Review and Done. This chat runs inside bb.

<<INSTALL>>

1. Run `aios-bb doctor`. Show me each line. A warning about no kanban plugin is fine.
2. If doctor says this folder is not a git repository, run `git init && git add -A && git commit -m "Start"`, then show `git log --oneline -1`.
3. Preview: `aios-bb setup --dry-run --name "My AIOS"`. Then run `aios-bb setup --name "My AIOS"`. If a bb project for this folder already exists, setup keeps it; that is correct.
4. Run `aios-bb setup --name "My AIOS"` once more and show that it says "Kept it".
5. Show that the four lanes exist: if `bb kanban` works (BB Overlay's Kanban board), say the board is ready; otherwise run `bb thread section list --json` and show that Backlog, In progress, Review and Done exist.

<<RULES>>

<<FINISH m04-cockpit>>
~~~

## 4.2 · Give one job to Claude and Codex side by side
what: Writes one small real job as a brief, hands it to two new threads that each work in their own copy of the folder, and puts them in the In progress lane.
check: Two new threads appear in the bb sidebar under In progress, each in its own worktree (a separate copy of the folder).
~~~
Give this job to Claude and to Codex in two separate worktree threads, show each report inline, and move each card to Review when it is ready. The cockpit is already set up (if not, stop and tell me to run prompt 4.1 first).

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

## 4.3 · Turn my list into to-dos and show my week as a chart (BB Overlay)
what: Saves three jobs you say in plain words as to-dos linked to this chat (BB Overlay's to-do panel), and draws a bar chart of your threads inside the reply.
check: Three items appear in the To-do panel (Cmd+Shift+D) linked to this chat, and the reply shows a bar chart.
~~~
We've got three things to do this week: send the Acme proposal, renew the domain, and book the accountant. Then show me how many threads I ran this week in each harness as a bar chart.

Here is how:
1. Add the three jobs as to-dos with the `workspace_todo` tool (action `add`), one short item each. If that tool is not available, BB Overlay is not installed: say so, and list the three jobs instead.
2. Count this week's threads per harness: `bb thread list --json` (add `--project "$BB_PROJECT_ID"` if the list is long), group by provider, and keep only threads from the last seven days.
3. Show the counts as a bar chart in your reply with the `::nav-chart` directive (BB Overlay's chat charts, `bars` type). If the directive is not available, show a small table instead.

<<RULES>>

<<FINISH m04-todos-and-chart>>
~~~

## 4.4 · Run my daily loop
what: Shows today's board (waiting, review, in progress, backlog), closes what is finished and archives it.
check: The report shows the four lists and how many finished threads were archived. Archived threads can still be found with `bb thread search`.
~~~
Show me today's board, what needs me, and what I can close. The cockpit is already set up (if not, stop and tell me to run prompt 4.1 first).

<<INSTALL>>

1. Run `aios-bb today` and show me the Waiting, Review, In progress and Backlog lists.
2. For each thread in Review, show its title and the note on its card, and read the file it made (for example `20_offers/services_v1.md`). Tell me in one line whether it did the job.
3. Do not mark anything as done yourself. List the commands I can run for the ones I accept: `aios-bb card done --thread "<title>"`.
4. Run `aios-bb close` (without `--archive-done`) and show me the end-of-day summary.
5. Tell me that `aios-bb close --archive-done` archives everything in Done, and that `bb thread search "<word>"` still finds archived threads.

<<RULES>>

<<FINISH m04-daily-loop>>
~~~
