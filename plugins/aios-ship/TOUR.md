# Tour: module 11, ship it to others

Followed by `/aios learn 11` with one of the member's own skills. It ends with the pack installed in a clean home folder.
Do one step at a time. Show the real output, then ask the member to confirm before the next step.

## Before you start

- Check: `ship-pack --help` lists `new`, `from-skill`, `check`, `bump` and `marketplace`.
  In Codex and Cursor it is `~/.local/bin/ship-pack`. If it is missing, install the pack first (see README.md).
- Ask: which skill folder (it holds a `SKILL.md`)? Pick a small one first. Where should the pack live?
  Default: a new git repository, for example `~/my-tools`, never this course repository or a plugin cache.

## Step 1: make a home for the packs

- Do: `mkdir -p ~/my-tools && cd ~/my-tools && git init`
- Check: `git status` works in that folder.

## Step 2: turn the skill into a pack

- Do: `ship-pack from-skill <skill-folder> --author "<their name>"`
- Expect: `Packaged skill <name> as <name>` and a list of next steps.
- If it stops with `looks like ... key` or `personal home path`, fix that file in the skill first. The pack will be public.
- Check: `find <name> -type f | sort` shows `.claude-plugin/plugin.json`, `skills/`, `evals/` (three cases),
  `tests/`, `install.sh`, `README.md`, `CHANGELOG.md` and `MARKETPLACE_ENTRY.json`.

## Step 3: write the three test cases

- Do: `ship-pack check <name>`
- Expect: it fails, listing every placeholder. That is correct.
- Do: with the member, write `evals/happy-path`, `evals/edge-case` and `evals/must-refuse`:
  each `prompt.md` is a real request in the member's words; each `graders/result.md` pattern is a word the right
  answer always contains. Fill the README's GitHub name, repository and marketplace name.
- If the skill needs a key: add it to `userConfig` in plugin.json with `"sensitive": true`. Never in a file.
- Check: `ship-pack check <name>` ends with `0 error(s)`.

## Step 4: test and validate

- Do:
  ```
  python3 -m unittest discover <name>/tests
  claude plugin validate <name> --strict
  ```
- Expect: `OK`, then `Validation passed`. The icon warning only matters for Anthropic's directory.

## Step 5: compare with and without the pack

- Do: `claude plugin eval <name> --runs 1`
- Expect: a score with the pack, a score without it, and the difference.
- If both columns score the same, the cases are too easy: Claude manages without the skill. Add a grader that
  checks something only the skill knows (a rate, a house rule, a file it writes), then run it again.
- If the `skill-fired` result is false in every case and the pack lists `dependencies`, evaluate a copy without
  `dependencies`: the eval cannot load a pack whose dependency it cannot find.

## Step 6: list it in a marketplace

- Do:
  ```
  ship-pack marketplace <name> --file .claude-plugin/marketplace.json --name <market> --owner "<their name>"
  claude plugin validate .
  git add . && git commit -m "<name> 0.1.0"
  ```
- Check: `Validation passed`.

## Step 7: install it as a stranger would

- If `CLAUDE_CONFIG_DIR` is set in this terminal (a second login from module 10), run `unset CLAUDE_CONFIG_DIR` first,
  or the install goes into that folder instead of the empty one.
- Do:
  ```
  mkdir /tmp/new-member
  HOME=/tmp/new-member claude plugin marketplace add ~/my-tools
  HOME=/tmp/new-member claude plugin install <name>@<market>
  HOME=/tmp/new-member claude plugin list
  HOME=/tmp/new-member ./<name>/install.sh
  ```
- Expect: `Successfully installed`, the pack `enabled` at `0.1.0`, and three `Linked` lines for Codex, Cursor and agents.

## Step 8: release a fix

- Do: `ship-pack bump <name> patch --note "<what changed>"`, then commit.
- Do: `HOME=/tmp/new-member claude plugin marketplace update <market>` and
  `HOME=/tmp/new-member claude plugin update <name>@<market>`
- Expect: `updated from 0.1.0 to 0.1.1`.
- Do: remove the test home when done: `rm -rf /tmp/new-member` (only this folder, which the member created).

## Share it

Push the repository to GitHub. Members add it with `/plugin marketplace add <github-name>/<repo>`.

## Done

Module 11 is complete when one of the member's skills has passed steps 4 and 7. Ask them to confirm, then hand back to `/aios`.
