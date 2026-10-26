# Plugin eval results v1

Real claude plugin eval attempts, with a no-plugin baseline requested and publishing disabled.
The sandbox uses HOME=/tmp/aios-member-sandbox. No credentials were copied from a real harness.

```sh
claude plugin eval plugins/aios-brain --case local-setup --runs 1 --trust-plugin --no-publish --output-dir /tmp/aios-eval-local-setup_v1 --json /Users/sky/.bb/plugins/environment-git-worktree/host-data/worktrees/thr_a8ducu6yie-1/skool-navaigate-install/proof/eval-local-setup_v1.json
```
```text
Wrote /Users/sky/.bb/plugins/environment-git-worktree/host-data/worktrees/thr_a8ducu6yie-1/skool-navaigate-install/proof/eval-local-setup_v1.json
Ablation: defaulting to with-without — a plugin resolved from this path, so each case also runs a no-plugin baseline arm (2× runs) and reports Δ; graders marked with-only (including `tool_used: Skill`) become a plugin-fired indicator rather than part of the score. Pass --ablation none for the previous single-arm run and scoring.
  local-setup: mocks: "plugin:aios-brain:aios-brain" has no mock and is NOT started — its tools are unavailable this run; add mocks/<server>/ to mock it, or pass --allow-real-servers to run the plugin's real server (as you, outside the sandbox)
Report: /tmp/aios-eval-local-setup_v1/report.html
[exit 2]
```

```sh
claude plugin eval plugins/aios-brain --case silent-failure --runs 1 --trust-plugin --no-publish --output-dir /tmp/aios-eval-silent-failure_v1 --json /Users/sky/.bb/plugins/environment-git-worktree/host-data/worktrees/thr_a8ducu6yie-1/skool-navaigate-install/proof/eval-silent-failure_v1.json
```
```text
Wrote /Users/sky/.bb/plugins/environment-git-worktree/host-data/worktrees/thr_a8ducu6yie-1/skool-navaigate-install/proof/eval-silent-failure_v1.json
Ablation: defaulting to with-without — a plugin resolved from this path, so each case also runs a no-plugin baseline arm (2× runs) and reports Δ; graders marked with-only (including `tool_used: Skill`) become a plugin-fired indicator rather than part of the score. Pass --ablation none for the previous single-arm run and scoring.
  silent-failure: mocks: "plugin:aios-brain:aios-brain" has no mock and is NOT started — its tools are unavailable this run; add mocks/<server>/ to mock it, or pass --allow-real-servers to run the plugin's real server (as you, outside the sandbox)
Report: /tmp/aios-eval-silent-failure_v1/report.html
[exit 2]
```

```sh
claude plugin eval plugins/aios-brain --case media-privacy --runs 1 --trust-plugin --no-publish --output-dir /tmp/aios-eval-media-privacy_v1 --json /Users/sky/.bb/plugins/environment-git-worktree/host-data/worktrees/thr_a8ducu6yie-1/skool-navaigate-install/proof/eval-media-privacy_v1.json
```
```text
Wrote /Users/sky/.bb/plugins/environment-git-worktree/host-data/worktrees/thr_a8ducu6yie-1/skool-navaigate-install/proof/eval-media-privacy_v1.json
Ablation: defaulting to with-without — a plugin resolved from this path, so each case also runs a no-plugin baseline arm (2× runs) and reports Δ; graders marked with-only (including `tool_used: Skill`) become a plugin-fired indicator rather than part of the score. Pass --ablation none for the previous single-arm run and scoring.
  media-privacy: mocks: "plugin:aios-brain:aios-brain" has no mock and is NOT started — its tools are unavailable this run; add mocks/<server>/ to mock it, or pass --allow-real-servers to run the plugin's real server (as you, outside the sandbox)
Report: /tmp/aios-eval-media-privacy_v1/report.html
[exit 2]
```

## Scores

| Case | With plugin | No-plugin baseline | Valid result |
|---|---|---|---|
| local-setup | Unscored | Not reached | auth_failed |
| silent-failure | Unscored | Not reached | auth_failed |
| media-privacy | Unscored | Not reached | auth_failed |

The runner records zero on the aborted first arm and exits 2, but this is an authentication failure, not a measured plugin quality score. No valid WITH/WITHOUT delta exists.

Next action: sign in to the member sandbox with its own Claude subscription, then rerun the three-case suite with --no-publish. The final acceptance run should use the default three runs per arm.

The cases cover local setup commands/storage/health, detecting a misleading heartbeat and 30-day retention, and free-caption/paid-transcription/digest opt-in boundaries. Skill invocation is an indicator; output regexes score both arms.

Unit and integration checks exercise the implementation independently; they do not replace model evals.
