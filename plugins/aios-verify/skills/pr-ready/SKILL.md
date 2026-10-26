---
name: pr-ready
description: Write a pull request description with real Testing output, a Risk level and exact How to revert steps, after the checks pass. Use when someone asks to open a PR, write a PR description, or get a change ready for review.
---

# Get a change ready for review

1. Run `aios-verify run` (or the project's own checks). If anything fails, stop and fix it
   first, or report the failure. A PR is never opened on red checks.
2. Read `REVIEW.md` if the project has one, and `git diff <base>...HEAD --stat` for the scope.
3. Fill `.github/pull_request_template.md` (or these headings if there is none):
   - **What changed**: one or two sentences, what and why.
   - **Testing**: the exact commands and their real output, pasted. A screenshot path for anything visible.
   - **Risk**: low, medium or high using REVIEW.md's table, plus what could break and for whom.
   - **How to revert**: `git revert <merge commit>` and anything else to undo (data, settings, a deploy).
4. High risk (money, logins, personal data, database changes, deletes, deploys) needs two
   people or the owner plus the revert plan. Say so in the PR. An agent's approval never counts.
5. Open the PR only if asked, with `gh pr create --fill-first` and the body above. Pushing to
   `main` or a release branch asks the person first (the production hook).

Finish with the PR text or link, the risk level and one next action. British English.
