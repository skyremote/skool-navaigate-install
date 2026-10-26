# aios-verify 2.0.0

Module 8 of YOUR AIOS 2.0: make it verifiable. Depends on `aios`.
Python 3.9 or later, standard library only. Screenshots need Chrome, Chromium or Edge.

## What is in the pack

| Part | What it does |
|---|---|
| `verify-setup` skill | Checks the agent runs itself, the Stop gate, the three hard rules, review in layers |
| `pr-ready` skill | A pull request with real Testing output, a Risk level and How to revert |
| `hooks/hooks.json` | PreToolUse on Bash: the three hard rules. Stop: the verify gate (only in projects with `.aios/verify.json`) |
| `aios-verify init` | Writes `.aios/verify.json`, `.claude/skills/verify/SKILL.md`, `REVIEW.md` and `.github/pull_request_template.md`. Never overwrites. `--git-hook` adds a pre-commit hook |
| `aios-verify run` | Runs every check and prints PASS or FAIL with the failure output. Exit 1 on any failure |
| `aios-verify try "<command>"` | Shows whether the hard-rule hook would allow, deny or ask, without running it |
| `aios-verify scan` | Looks for secrets in the staged change (values never printed) |
| `aios-verify screenshot` | Screenshots a URL or local HTML file with a headless browser |
| `templates/` | The verify skill, REVIEW.md, the PR template and the git pre-commit hook |
| `examples/sample-app` | A tiny price list app with tests and a build, for the lesson |

## The three hard rules

| Rule | Decision | Examples |
|---|---|---|
| No secrets in commits | deny | `git commit` adding a private key, an AWS, GitHub, Slack, Google, Stripe or Anthropic-style key, a JWT, a `password = "..."` setting, or a `.env` / `.pem` file |
| No destructive git | deny | `push --force`, `push --delete`, `reset --hard`, `clean -f`, `checkout -- .`, `restore .`, `branch -D`, `stash drop`, `filter-branch`, `gc --prune` |
| Confirm before live production | ask | `vercel --prod`, `netlify deploy --prod`, `npm publish`, push to `main` or `master`, `fly deploy`, `railway up`, `firebase deploy`, `wrangler deploy`, `terraform apply`, `kubectl apply`, `docker push`, plus your own `production_commands` |

The hooks act on the agent's Bash tool. A person can still run any command in their own
terminal. `git push --force-with-lease` is allowed.

## Install

Claude Code, once `aios` is installed (module 1):

```
/aios install aios-verify
```

It says what the pack adds, asks before installing, shows the proof, and then you type
`/reload-plugins`. The direct command is `/plugin install aios-verify@navaigate-aios`.

Codex and Cursor, from your checkout of this repository:

```
./install.sh aios-verify
./install.sh aios-verify --check
cd <your project> && aios-verify init --git-hook
```

Codex and Cursor get the skills, the command and the git pre-commit hook (secret scan and
checks at commit time). The PreToolUse hooks and the Stop gate are Claude Code features.

## Proof

- Unit tests: `python3 -m unittest discover -s tests/aios-verify -v` from the repository root.
- `claude plugin validate plugins/aios-verify --strict`.
- Eval suite: `evals/` (done-means-proven, hard-rules, pr-description). Run it from the repository
  root: `claude plugin eval plugins --eval-dir aios-verify/evals --runs 1 --no-publish`.
  Results and sandbox records are build evidence, kept with the course material, not in this repository.
