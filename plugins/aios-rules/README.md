# aios-rules 2.0.0

Module 2 of YOUR AIOS 2.0: your folders and your rules. Depends on `aios`.

- `/rules` sets up a folder map, a starter `AGENTS.md` (under 150 lines), a `CLAUDE.md` that holds
  only `@AGENTS.md`, and three path-scoped rules in `.claude/rules/`. It never overwrites a file.
- `aios-rules check` counts the lines and approximate tokens of everything Claude Code, Codex or
  Cursor loads into every session, and exits 1 when anything is over budget.
- `/rules-audit` runs the monthly audit: the budget check, `/doctor prompt-audit` and
  `/skill-doctor`, saved to `80_aios/audits/YYYY-MM-DD_rules-audit_v1.md`. It never edits your rules.

## Install

Claude Code (from a checkout of this repository, until 2.0 is published):

```sh
claude plugin marketplace add ./
claude plugin install aios@navaigate-aios
claude plugin install aios-rules@navaigate-aios
```

After release: `/plugin install aios-rules@navaigate-aios` once the marketplace
`skyremote/skool-navaigate-install` is added.

Codex and Cursor, from the checkout:

```sh
./install.sh aios
./install.sh aios-rules
export PATH="$HOME/.local/bin:$PATH"
```

## Commands

```sh
aios-rules init --dir . --business "Acme Studio" --owner "Sam Rivera" --dry-run
aios-rules init --dir . --business "Acme Studio" --owner "Sam Rivera"
aios-rules check                  # Claude Code view; --harness all for Codex and Cursor too
aios-rules check --json
aios-rules cursor-rules           # mirror .claude/rules into .cursor/rules/*.mdc
aios-rules audit                  # monthly; --no-claude for the budget check only
```

Budgets (change with flags): 150-line target and 200-line limit per file, 300 lines and about
4,000 tokens for everything always loaded. Tokens are characters divided by four, so treat them
as an estimate. Plugin skills, MCP tools and the system prompt are not counted: use `/context`.

Needs Python 3.9 or later. No network, no account and no key. The audit's Claude Code steps run
`claude -p` on your own sign-in with read-only tools.

## Tests

```sh
python3 -m unittest discover -s tests/aios-rules -v
claude plugin validate plugins/aios-rules --strict
claude plugin eval plugins/aios-rules --runs 1 --no-publish
```
