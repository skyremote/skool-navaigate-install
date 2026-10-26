# Tour: module 9, working methods

Followed by `/aios learn 9` inside the member's own project. One feature goes from idea to merged code.
Do one step at a time. Show the real output, then ask the member to confirm before the next step.
Use the member's own feature name in place of `<feature>` (short, lower case, dashes).

## Before you start

- Check: `git rev-parse --show-toplevel` prints a folder. If not, ask the member to `cd` into their project,
  or run `git init` and make a first commit there.
- Check: `aios-methods --help` lists `worktree`, `glossary`, `spec` and `loop`.
  In Codex and Cursor it is `~/.local/bin/aios-methods`. If it is missing, install the pack first (see README.md).

## Step 1: get interviewed

- Do: run the `grill` skill with the member's idea in one line.
- Expect: one question at a time, each with a suggested answer. No code.
- Check: you can say the feature back in three sentences and the member agrees.

## Step 2: write down the words

- Do:
  ```
  aios-methods glossary init
  aios-methods glossary add "<Term>" "<what it means here>" --avoid "<other words for it>"
  ```
  Add one line for each word the interview pinned down.
- Expect: `Created GLOSSARY.md`, then `Added <Term> to GLOSSARY.md` for each word.
- Check: `aios-methods glossary check` ends with `0 problems`.

## Step 3: write the spec

- Do: `aios-methods spec new <feature>`, then fill `docs/specs/<feature>.md` from the interview answers.
  Every line under "Done when" is a command in backticks the agent can run.
  Write `None` under "Open questions" only when nothing is open.
- Expect: the first check fails on the empty template. That is correct.
- Check: `aios-methods spec check docs/specs/<feature>.md` ends with `0 problem(s)`.
- Do: commit the glossary and spec: `git add GLOSSARY.md docs/specs && git commit -m "Spec for <feature>"`.

## Step 4: give the feature its own folder

- Do: `aios-methods worktree new <feature>`
- Expect: `Created worktree ../<repo>-<feature>` and `Branch work/<feature>`.
- Check: `aios-methods worktree list` shows the new folder as `clean`.
- Alternatives: `claude -w <feature>`, `codex --worktree`, `cursor-agent -w <feature>`. In bb, one thread per feature.

## Step 5: set up the loop

- Do: in the new folder, `aios-methods loop init`.
- Expect: `Created .claude/loop.md`.
- Optional: let the loop run the spec's check without asking each time by adding that command to the project's
  `.claude/settings.json` under `permissions.allow`, for example `"Bash(python3 -m unittest:*)"`.
  Never allow push, deploy or delete commands.
- Do (Claude Code only): start a session in that folder and type `/loop` (Claude picks the interval) or `/loop 10m`.
- Expect: each run names the spec line it took, runs its command, shows the real output and commits if it passes.
- Check: the transcript shows the check's output. If not, the run did not prove anything.
- Stop: ask "cancel the loop". Esc does not stop it. It also ends when Claude Code closes, or after seven days.
- Codex and Cursor: no `/loop`. Run the check in a visible shell loop instead:
  `while sleep 600; do <the check> || break; done`

## Step 6: merge and clean up

- Do: in the main folder, `git merge work/<feature>`.
- Do: `aios-methods worktree done <feature>`
- Expect: `Removed worktree ...` and `Deleted merged branch work/<feature>`.
- If it says `not merged` or `Uncommitted changes`, nothing was removed. Merge or commit first, then run it again.
- Check: `aios-methods worktree list` shows only the main folder.

## Later: the bigger methods

Third-party, free and MIT-licensed. Link to them; do not copy their files. Details in `skills/methods/references/third-party.md`.

- GSD Core, for projects with phases and a roadmap: `npx @opengsd/gsd-core@latest`, then `/gsd-new-project`.
- Compound engineering, to write down what each fix taught you:
  `/plugin marketplace add EveryInc/compound-engineering-plugin`, then `/plugin install compound-engineering`.

## Done

Module 9 is complete when the member has merged one feature this way. Ask them to confirm, then hand back to `/aios`.
