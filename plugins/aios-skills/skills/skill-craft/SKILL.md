---
name: skill-craft
description: Decide whether a job deserves a skill, then write it short, measure its context cost, hide the ones you do not use and prove it with three evals against a no-skill baseline. Use when someone asks to write, fix, trim, audit, hide or test a skill.
---

# Skills that earn their place

A skill is a folder with a SKILL.md. Its name and description are listed to the
model on every turn, used or not. The body loads only when the skill runs. So a
skill earns its place when it does a repeated job better than no skill at all,
and the description is the part that costs you every day.

## 1. Decide first
Ask the member three questions, in this order, and stop at the first "no":
1. Do you do this job at least weekly, or will you repeat it many times?
2. Does it need exact steps, a fixed format, a script or a check the model would not guess?
3. Can you name the check that proves it worked (a file, a count, a passing test)?
If any answer is no, say so. A one-line rule in AGENTS.md, or nothing, is better.

## 2. Write it short
- `name`: lowercase and hyphens, the job not the tool (`weekly-report`, not `excel-helper`).
- `description`: one or two sentences. Lead with the job, then "Use when..." with
  the words a person would actually type. Aim for under 300 characters.
- Body under 500 lines. Steps, exact commands, the check, the one mistake to avoid.
- Long reference material goes in a separate file the body points to. Scripts go in `bin/` or `scripts/`.
- To create one with its evals in one go, use the `new-skill` skill (`aios-skill new`).

## 3. Measure it
- `/skill-doctor` (Claude Code 2.1.252 or later) shows each skill's context cost and which
  ones were never invoked. Run it in the terminal; it does not work over Remote Control.
  Headless: `claude -p "/skill-doctor"`.
- `/doctor` estimates the whole skill listing's cost and names the biggest entries.
- `aios-skill audit` lists personal and project skills by listing cost, with their current state.
- `aios-skill check <folder>` checks one skill: description length and sentences, body
  lines, leftover TODOs and the eval suite. Exit 1 means something must be fixed.

## 4. Hide the long tail
For personal (`~/.claude/skills`) and project (`.claude/skills`) skills use `skillOverrides`:

| State | Listed to the model | In the / menu |
|---|---|---|
| `on` | name and description | yes |
| `name-only` | name only | yes |
| `user-invocable-only` | hidden | yes |
| `off` | hidden | hidden |

- Command: `aios-skill hide <skill> <state>` writes `.claude/settings.local.json` with a backup.
  Add `--scope project` or `--scope user` for the other files, `--dry-run` to preview.
- Or in Claude Code: `/skills`, highlight the skill, press Space to cycle, Esc to save.
- Order: never-used and most expensive first (from `/skill-doctor`), then `name-only` for
  rarely-used ones you still type yourself.
- Plugin skills ignore `skillOverrides`. Disable the plugin with `/plugin` instead.
- Codex and Cursor have no `skillOverrides`. There, remove the skill's link from
  `~/.codex/skills`, `~/.cursor/skills` or `~/.agents/skills` to hide it.

## 5. Prove it with three evals
Three cases, each in `evals/<case>/prompt.md` plus `graders/*.md`:
1. `should-fire`: a request a member would type, without naming the skill.
2. `edge-case`: the same job with a missing detail or a trap.
3. `should-not-fire`: a nearby request where the skill must stay quiet
   (`tool_used: Skill`, `min: 0`, `max: 0`, `arm: both`).
Each firing case gets one grader on the result (`regex` or a short `llm` rubric) and one
`tool_used: Skill` grader. The skill must sit in a plugin or a skills-directory plugin
(`.claude-plugin/plugin.json`) for `claude plugin eval` to find it.

Run: `claude plugin eval <plugin-folder> --runs 1 --no-publish` while drafting, then
the default three runs before you rely on it. Read `WITH`, `W/OUT` and `Δ`:
- Δ above zero: the skill helps. Keep it.
- Δ at or below zero: the model does as well without it. Fix it or hide it.
- `skill-fired` failing: the description does not match how people ask. Rewrite it.
Each run is a real model call on the member's own plan. Say so before running.

## 6. Re-check
Run `/skill-doctor` monthly and after each new model release. Delete or hide what nobody used.

## Never
- Never write a skill to look busy, or one per person or department.
- Never claim a skill works because it fired once. Show the eval result.
- Never edit `skillOverrides` by hand in a file that is not valid JSON; fix the file first.

Finish with the check result, the Δ if measured, and one next action. British English.
