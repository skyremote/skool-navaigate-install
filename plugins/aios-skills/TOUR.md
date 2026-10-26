# Tour: module 6, skills that earn their place

`/aios learn 6` follows these steps in the member's own AIOS folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never overwrite or delete a member's skill. If a check fails, stop, fix that one thing, and run the check again.

## Step 1: Find the command
- **Do:** check that the pack's command runs.
- **Command:** `aios-skill --version` (Codex or Cursor: `~/.local/bin/aios-skill --version`).
- **They should see:** `aios-skill 2.0.0`.
- **Check:** exit code 0. If it is missing, run `export PATH="$HOME/.local/bin:$PATH"` (Codex and Cursor),
  or in Claude Code run `/aios install aios-skills`, then `/reload-plugins`.

## Step 2: Choose the job
- **Do:** ask for one job they explain to the agent every week, and the check that proves it is done.
- **Command:** none. Write their answers down: the job, the words they type to ask for it, the check.
- **They should see:** three short answers.
- **Check:** all three are yes: weekly or repeated, a fixed format or steps, a check they can name.
  If any is no, add one line to AGENTS.md instead and skip to step 9.

## Step 3: Scaffold the skill with its evals
- **Do:** create the folder. Use their job's name and their words in the description.
- **Command:** `aios-skill new <job-name> --description "<what it does>. Use when <the words they type>."`
- **They should see:** `Created ~/.claude/skills/<job-name>` and eleven files, including three `evals/` cases.
- **Check:** `ls ~/.claude/skills/<job-name>/evals` lists `edge-case`, `should-fire`, `should-not-fire`.

## Step 4: See the check fail
- **Do:** run the checker on the fresh scaffold.
- **Command:** `aios-skill check ~/.claude/skills/<job-name>`
- **They should see:** `FAIL` and `still contains TODO` lines.
- **Check:** exit code 1 (`echo $?`). This is expected: nothing is filled in yet.

## Step 5: Fill in SKILL.md
- **Do:** replace each `TODO:` line in SKILL.md with them: the steps, exact commands, the check, the one mistake to avoid.
- **Command:** `grep -n "TODO:" ~/.claude/skills/<job-name>/SKILL.md`
- **They should see:** no lines once it is filled.
- **Check:** the body reads as steps another person could follow. A finished example is in the pack at
  `examples/meeting-actions/SKILL.md`.

## Step 6: Write the three evals
- **Do:** fill each `evals/<case>/prompt.md` with a message they would type, and each `graders/result.md`
  with a PASS and a FAIL line. Never name the skill in a should-fire prompt.
- **Command:** `grep -rn "TODO:" ~/.claude/skills/<job-name>/evals`
- **They should see:** no lines once every case is filled.
- **Check:** `should-not-fire` asks for a nearby job the skill must leave alone.

## Step 7: Pass the checker
- **Do:** run the checker again.
- **Command:** `aios-skill check ~/.claude/skills/<job-name>`
- **They should see:** `PASS`, the description length, about how many tokens it costs per turn, and `3 case(s)`.
- **Check:** exit code 0.

## Step 8: Test it against no skill
- **Do:** tell them this uses their own plan (six short runs), then run it. Answer `y` to the trust question.
- **Command:** `claude plugin eval ~/.claude/skills/<job-name> --runs 1 --no-publish`
- **They should see:** a line per case with `WITH`, `W/OUT` and `Δ`, and the skill-fired result.
- **Check:** Δ above zero on the firing cases. If `skill-fired` fails, rewrite the "Use when" words and re-run.
  If Δ is zero or below, the model already does this well: make the steps sharper or keep it hidden.

## Step 9: See what every skill costs
- **Do:** measure the listing cost and the usage.
- **Command:** `aios-skill audit` in the terminal, then `/skill-doctor` inside Claude Code.
- **They should see:** skills sorted by tokens per turn, then which ones were never used.
- **Check:** they can name one skill that costs tokens every turn and was never used.

## Step 10: Hide one they do not use
- **Do:** preview, then hide it. Nothing is deleted.
- **Command:** `aios-skill hide <skill> off --dry-run`, then `aios-skill hide <skill> off`
  (or `name-only` for one they still type themselves).
- **They should see:** `Set <skill> to off in .claude/settings.local.json` and a backup path.
- **Check:** `aios-skill audit` shows it as `off` with 0 tokens. Plugin skills are refused: use `/plugin` for those.
  In Codex or Cursor, remove the skill's link from `~/.codex/skills`, `~/.cursor/skills` or `~/.agents/skills`.

## Step 11: Use it for real
- **Do:** start a new session and ask for the job in their own words.
- **Command:** `claude`, then their usual request.
- **They should see:** the skill load, and an answer that passes the check from step 2.
- **Check:** they say whether it passed. Then `/aios` to mark module 6 done.
