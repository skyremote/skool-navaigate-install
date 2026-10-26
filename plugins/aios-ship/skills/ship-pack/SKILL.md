---
name: ship-pack
description: Scaffold a new pack, or turn an existing skill folder into one, with a skill, three eval cases, tests, an installer, a changelog and a marketplace entry, then check it. Use for /ship-pack, "scaffold a plugin", or "turn this skill into a pack".
---

# /ship-pack

Use the `ship-pack` command. In Claude Code it is on the Bash PATH from this plugin's `bin/`.
In Codex and Cursor it is `~/.local/bin/ship-pack` after `./install.sh aios-ship`.

## Pick the start

- An existing skill folder (it has a `SKILL.md`): `ship-pack from-skill <skill-folder> --dir <where>`.
  It refuses if the skill has a key, a token or a personal home path in it. Fix those first, because the pack
  will be public.
- Nothing yet: `ship-pack new <pack-name> --skill <skill-name> --description "<one or two sentences>" --dir <where>`.
- Add `--depends aios` (or another plugin) only if the pack needs it. Add `--author "<name>"`.

Ask the member for the name and where the pack should live if they have not said. Default to a folder in
their own repository, never inside this course repository or a plugin cache.

## Fill the placeholders

The scaffold marks every line the member must write with a placeholder that `ship-pack check` reports.
Work through them with the member:

1. `skills/<skill>/SKILL.md`: description first (one or two sentences with the words a member would type), then steps.
2. Three eval cases in `evals/`: `happy-path`, `edge-case` and `must-refuse`. Write each prompt the way a member
   would type it, and set each `graders/result.md` pattern to a word or command the right answer must contain.
3. `README.md`: the member's GitHub name, repository and marketplace name.
4. Secrets: if the skill needs a key, add it to `userConfig` in plugin.json with `"sensitive": true`. Never in a file.

## Check, in this order

```
ship-pack check <pack>
python3 -m unittest discover <pack>/tests
claude plugin validate <pack> --strict
claude plugin eval <pack> --runs 1
```

Show the real output of each. Do not move on while one fails. `ship-pack check` exits 1 until every placeholder
is filled, so a fresh scaffold failing it is expected.

## Share it

```
ship-pack marketplace <pack> --file .claude-plugin/marketplace.json --name <market> --owner "<name>"
claude plugin validate .
```

For a new version: `ship-pack bump <pack> patch --note "what changed"`, then check and validate again.

End with the pack path, which checks passed, and the install line a member would use. British English.
