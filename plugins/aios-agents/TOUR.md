# Tour: module 7, agents without sprawl

`/aios learn 7` follows these steps in the member's own AIOS folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never create an agent for them without a named reason. If a check fails, stop, fix that one thing, and re-check.

## Step 1: Find the command
- **Do:** check that the pack's command runs.
- **Command:** `aios-agent --version` (Codex or Cursor: `~/.local/bin/aios-agent --version`).
- **They should see:** `aios-agent 2.0.0`.
- **Check:** exit code 0. If it is missing, run `export PATH="$HOME/.local/bin:$PATH"`, or in Claude Code run
  `/aios install aios-agents`, then `/reload-plugins`.

## Step 2: Meet the crew
- **Do:** list the three agents and their tools.
- **Command:** `aios-agent crew`, then `/agents` inside Claude Code.
- **They should see:** `code-reviewer`, `design-critic` and `researcher`, none with Edit, Write or Bash.
- **Check:** `/agents` shows them as `aios-agents:code-reviewer` and so on.

## Step 3: Audit their own agents
- **Do:** list any agents they already have.
- **Command:** `ls ~/.claude/agents .claude/agents 2>/dev/null`
- **They should see:** their agent files, or nothing.
- **Check:** for each one, they name the reason it exists: parallel work, isolation, or a context that would flood.
  Any agent named after a department or role with no such reason is a candidate to fold into a skill (module 6).
  Do not delete anything; write the list down.

## Step 4: Write a brief
- **Do:** pick one real job worth handing over (a review, or research with several sources). Make the brief.
- **Command:** `aios-agent brief new --out briefs/<job>_v1.md`
- **They should see:** `Wrote briefs/<job>_v1.md`.
- **Check:** the file has Objective, Format, Context, Tools, Boundaries and Stop headings.

## Step 5: Check the brief
- **Do:** run the check on the empty template first, then fill each part with them and re-run.
- **Command:** `aios-agent brief check briefs/<job>_v1.md`
- **They should see:** `NOT READY` with a list, then `READY` once filled.
- **Check:** the `Done when:` line names a count, a file or a passing command.

## Step 6: Copy the sample task twice
- **Do:** make two identical copies of the invoice app from the pack.
- **Command:** `cp -R <pack>/examples/compare-task ~/compare-one && cp -R <pack>/examples/compare-task ~/compare-two`
  (in Claude Code, `<pack>` is the plugin folder; in a checkout, `plugins/aios-agents`).
- **They should see:** `invoice.py`, `test_invoice.py` and `TASK.md` in each.
- **Check:** `cd ~/compare-one && python3 -m unittest` prints `OK`.

## Step 7: Run it in one loop
- **Do:** run the task with no sub-agents. Tell them it uses their plan.
- **Command:** `cd ~/compare-one`, then the "Run 1" command in `TASK.md`.
- **They should see:** nothing until it finishes, then a new `~/one-loop.json`.
- **Check:** `python3 -m unittest` in `~/compare-one` prints `OK`.

## Step 8: Run it with one reviewer
- **Do:** run the same task, adding the reviewer. Allow the `Agent` tool.
- **Command:** `cd ~/compare-two`, then the "Run 2" command in `TASK.md`.
- **They should see:** a new `~/with-reviewer.json`.
- **Check:** `python3 -m unittest` in `~/compare-two` prints `OK`.

## Step 9: Compare
- **Do:** put the two runs side by side.
- **Command:** `aios-agent compare ~/one-loop.json ~/with-reviewer.json`
- **They should see:** time, turns, tokens, cost and `sub-agents spawned` of 0 against 1.
- **Check:** if the second run shows 0 sub-agents, `Agent` was not allowed: fix and re-run step 8.
  For real wall-clock time, prefix both runs with `time` and add `--wall <first> <second>`.

## Step 10: Decide
- **Do:** read the reviewer's findings in the second run's reply. Write one line: what did it catch that the
  first run missed?
- **Command:** `aios-agent result ~/with-reviewer.json`
- **They should see:** the final reply, including what the reviewer found.
- **Check:** they decide, in writing, whether the reviewer earned its place for this kind of change. Then `/aios`.
