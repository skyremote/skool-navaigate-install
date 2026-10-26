---
name: ship
description: Package a skill or pipeline as a plugin other people can install, and keep each member's API keys out of its files with sensitive userConfig. Use for /ship, "package this", "share my skill", "make a plugin", "where does the API key go", evals, marketplaces, installers or releasing a new version.
---

# Ship it to others

Ship the process, not the member's private files. A pack must work on a stranger's machine with
their own accounts, folders and keys. Strip names, client data, home paths and keys before anything else.

Scaffold with the `ship-pack` command (this pack's `bin/`, or `~/.local/bin/ship-pack` in Codex and Cursor):

- From a skill that already works: `ship-pack from-skill <skill-folder> --author "<name>"`.
- From nothing: `ship-pack new <pack-name> --skill <skill-name>`.

Both create everything below. The `/ship-pack` skill walks a member through it step by step.

## The layout

```
my-pack/
  .claude-plugin/plugin.json     name, version, description, author, licence, dependencies, userConfig
  skills/<skill>/SKILL.md        one folder per skill; SKILL.md under 500 lines
  skills/<skill>/references/     long detail the skill reads only when needed
  bin/                           executables; on the Bash PATH while the plugin is enabled
  evals/<case>/prompt.md         three or more cases, each with graders/*.md
  tests/                         unit tests for any code in bin/ or scripts/
  install.sh                     links skills for Codex and Cursor
  README.md, CHANGELOG.md, MARKETPLACE_ENTRY.json
```

A `CLAUDE.md` at the plugin root is not loaded. Put instructions in a skill. A plugin with `bin/` cannot be
installed in claude.ai or Cowork, so keep anything those surfaces need in skills only.

## plugin.json

- `name`: lower-case with dashes. It becomes the namespace, for example `/my-pack:skill`.
- `version`: `1.2.3`. Setting it pins members to that version until you change it.
- `dependencies`: plugins that must be enabled for this one to work, for example `["aios"]`.
  Bare names resolve in the same marketplace. Add one only when the pack truly needs it.
- `userConfig`: values members enter when they enable the pack. Every key, token or password gets
  `"sensitive": true`, which stores it in the system keychain instead of `settings.json`.
  Read it as `${user_config.KEY}` in MCP config, or `CLAUDE_PLUGIN_OPTION_<KEY>` in hook processes.
  A sensitive value is not substituted into skill text, so never ask for it in the chat.

## Evals

Three cases at least, written the way a member would type, each with one grader on the result
(`regex` or `llm`) and one `tool_used: Skill` grader that proves your skill fired.

```
claude plugin eval my-pack --runs 1
```

It runs each case with and without the plugin and reports the difference. Known gap in Claude Code 2.1.310:
a path target whose `dependencies` cannot be resolved in the eval sandbox runs with no plugin at all, so the
skill never fires. Check the trace or the `skill-fired` grader. If it shows that, evaluate a copy with
`dependencies` removed and say so in your proof.

## Marketplace and installers

- Claude Code: list the pack in your repository's `.claude-plugin/marketplace.json`
  (`ship-pack marketplace my-pack --file .claude-plugin/marketplace.json --name <market> --owner <you>`).
  Members then run `/plugin marketplace add <you>/<repo>` and `/plugin install my-pack@<market>`.
- Codex and Cursor: they read skills from `~/.codex/skills`, `~/.cursor/skills` and `~/.agents/skills`.
  The scaffolded `install.sh` links each skill there and refuses to replace anything it did not create.
  `install.sh --uninstall` removes only its own links. Codex members call skills as `$skill`.

## Versions

- Bump with `ship-pack bump my-pack patch|minor|major --note "what changed"`. It updates plugin.json,
  `MARKETPLACE_ENTRY.json` and `CHANGELOG.md` together.
- Patch for a fix, minor for a new skill or option, major when a member must change something.
- `claude plugin tag my-pack` creates a `my-pack--v1.2.3` git tag after checking the versions agree.
- Members update with `claude plugin marketplace update <market>`, then `claude plugin update my-pack@<market>`.

## Validate before every share

```
ship-pack check my-pack                    # placeholders, secrets, home paths, evals, versions
python3 -m unittest discover my-pack/tests
claude plugin validate my-pack --strict    # the official check; must say Validation passed
```

Then install it in a clean sandbox as a new member would, with `HOME` pointed at an empty folder in `/tmp`,
and keep the commands and output as proof.

End with the checks that passed and the one next step, then `/aios`. British English.
