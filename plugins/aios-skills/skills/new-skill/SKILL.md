---
name: new-skill
description: Scaffold a new skill folder with a short SKILL.md and three eval cases (should fire, edge case, should not fire), ready for claude plugin eval. Use when someone says make me a skill, turn this into a skill, or start a new skill.
---

# New skill, with its evals

1. Ask for the job in one line and the words the member would type to ask for it.
   If they cannot name a check that proves the job is done, stop and use `skill-craft` step 1.
2. Choose a name: lowercase and hyphens, named after the job.
3. Write the description: one or two sentences, the job first, then "Use when ...".
4. Choose where it lives:
   - personal (every project): default, `~/.claude/skills/<name>`
   - this project only: add `--project`, writes `./.claude/skills/<name>`
5. Run, with the member's words in the quotes:
   ```
   aios-skill new <name> --description "<one or two sentences>"
   ```
   In Codex or Cursor, run `~/.local/bin/aios-skill` (after `./install.sh aios-skills`).
   It never overwrites an existing folder.
6. Fill every TODO with the member: the steps, the check, the one mistake to avoid,
   and the three eval prompts and their PASS/FAIL rubrics. Write eval prompts the way
   a person would type them. Never name the skill in a should-fire prompt.
7. Run `aios-skill check <folder>` until it prints PASS.
8. Offer the baseline test (it uses the member's own plan):
   ```
   claude plugin eval <folder> --runs 1 --no-publish
   ```
   Report WITH, W/OUT and Δ exactly as printed. Never invent a score.
9. Tell them it loads in a new session, or now with `/reload-plugins`.

Codex and Cursor read the same SKILL.md from `~/.codex/skills`, `~/.cursor/skills`
or `~/.agents/skills`; link the new folder there. `claude plugin eval` runs in Claude Code only.

Finish with the folder path, the check result and one next action. British English.
