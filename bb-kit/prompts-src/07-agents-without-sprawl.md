# 07 · Agents without sprawl
pack: aios-agents
cmd: aios-agent

## 7.1 · Meet the crew and write a brief
what: Shows the three read-only helper agents, lists any agents you already have, and writes a brief (a clear hand-over note) that passes its check.
check: `aios-agent brief check` says READY, and the brief's "Done when" line names a count, a file or a command.
~~~
Set up module 7: when a helper agent is worth it, and how to brief one.

The job I might hand over (edit this line): review `20_offers/` and list anything a new client would find unclear.

<<INSTALL>>

1. Run `aios-agent crew`. Show the three agents and their tools. Point out that none of them can edit files or run commands.
2. List the agents I already have: `ls ~/.claude/agents .claude/agents 2>/dev/null`. For each one, say which reason it has: parallel work, a separate workspace, or a job whose output would flood the chat. Say "no reason" where none fits. Do not delete anything.
3. Make a brief for the job above: `aios-agent brief new --out briefs/review-offers_v1.md`.
4. Run `aios-agent brief check briefs/review-offers_v1.md`. It should say NOT READY on the empty template.
5. Fill in each part of the brief for the job above: Objective, Format, Context, Tools, Boundaries and Stop. The "Done when" line must name a count, a file or a command.
6. Run the check again. It must say READY.

<<RULES>>

<<FINISH m07-crew-and-brief>>
~~~

## 7.2 · Compare one agent with one agent plus a reviewer
what: Runs the same small coding task twice, once alone and once with a reviewer agent, and compares time, tokens and what the reviewer caught. It uses your own plan.
check: Both copies pass their tests, and `aios-agent compare` shows 0 sub-agents against 1.
~~~
Run the module 7 comparison: the same task done by one agent alone, and by one agent with a reviewer.

<<INSTALL>>

1. Copy the sample task twice: from the pack's plugin folder, copy `examples/compare-task` to `50_projects/compare-one` and to `50_projects/compare-two`. Check that `python3 -m unittest` prints OK in `50_projects/compare-one`.
2. Read `50_projects/compare-one/TASK.md`. In `50_projects/compare-one`, run its "Run 1" command. Save the JSON it writes inside that folder as `one-loop.json` (change the output path in the command if needed). Wait for it to finish.
3. In `50_projects/compare-two`, run the "Run 2" command, with the `Agent` tool allowed. Save its JSON as `with-reviewer.json` in that folder. Wait for it to finish.
4. Run `python3 -m unittest` in both folders. Both must print OK.
5. Run `aios-agent compare 50_projects/compare-one/one-loop.json 50_projects/compare-two/with-reviewer.json` and show the table. If the second run shows 0 sub-agents, the `Agent` tool was not allowed: fix it and run step 3 again.
6. Run `aios-agent result 50_projects/compare-two/with-reviewer.json` and tell me in one line what the reviewer caught that the first run missed. Then give me your view: was the reviewer worth it for this kind of change?

<<RULES>>

<<FINISH m07-compare>>
~~~
