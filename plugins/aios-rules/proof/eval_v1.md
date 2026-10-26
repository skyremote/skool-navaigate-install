# aios-rules eval, v1

One run per case, with a no-plugin baseline arm, Claude Code 2.1.310, model as configured for the account.
HOME was a sandbox (`/tmp/aios2-sandbox-a-foundations-eval`). The report stayed local (`--no-publish`).

**Why a copy:** `claude plugin eval` does not load a pack's dependencies, so with `"dependencies": ["aios"]`
the pack fails with `dependency-unsatisfied` and both arms score the same. The evaluated copy differs only
in that line. Plugin loaded without errors in this run: yes.

```sh
claude plugin eval <copy of plugins/aios-rules without dependencies> --runs 1 --trust-plugin --no-publish --output-dir /tmp/aios2-a-foundations/eval_v1 --json /tmp/aios2-a-foundations/eval_v1.json
```

| Case | With pack | Without pack | Delta | With-pack graders |
|---|---|---|---|---|
| fresh-setup | 1 | 0.25 | 0.75 | bridge pass, check pass, init pass, scoped pass, skill-fired pass |
| halfway-move | 1 | 0.5 | 0.5 | agents pass, check pass, limit pass, scoped pass, skill-fired pass |
| monthly-audit | 0.75 | 0 | 0.75 | dated-file pass, no-edit fail, prompt-audit pass, skill-doctor pass, skill-fired pass |

Overall with pack: 0.9166666666666666. Mean delta: 0.6666666666666666. Cases passed: 2 of 3. Cost: about $0.57. Runner exit 1 (it exits 1 when any case scores below 1.0).

`skill-fired` is a with-only indicator and is not part of the score.
