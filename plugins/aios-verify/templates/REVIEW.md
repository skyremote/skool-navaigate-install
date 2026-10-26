# REVIEW.md

How changes to this project are reviewed. Claude Code's Code Review service reads this
file; people and agents reviewing by hand should follow it too.

## What every change needs
1. `aios-verify run` passes: tests, build and (for anything visible) a screenshot.
2. A pull request using `.github/pull_request_template.md`, with Testing, Risk and How to revert filled in.

## Risk decides who approves
| Risk | Examples | Approval |
|---|---|---|
| Low | Copy, styles, docs, a test that only adds coverage | Checks pass; no human approval needed |
| Medium | New feature behind a flag, a refactor with tests, a dependency bump | One person approves |
| High | Money, logins and permissions, personal data, database changes, deletes, anything that deploys | Two people approve, or the owner plus a written rollback plan |

An agent's approval never counts as a person's. Whoever asked the agent for the change owns it.

## What reviewers look for, in order
1. Does it do what the pull request says, and nothing else?
2. Correctness: wrong conditions, empty or missing input, rounding with money, time zones.
3. Safety: secrets, unchecked input, destructive commands, data loss.
4. A test that would fail if this broke.

## Rules
- Two review rounds at most. If it is still not right, talk it through or split the change.
- Report findings with file, line, what goes wrong and the smallest fix. No style nitpicks unless the project has a rule for it.
- When something breaks in production, add a test or an eval case that would have caught it.
