---
name: models
description: Choose the right model and effort for a job, set medium effort as the default, pair a main model with the advisor, check usage, and set up a second login for failover. Use for /models, "which model should I use", "my limit ran out", effort, the advisor, or cost.
---

# Models, effort and cost

Start every answer by running `/models-check` (or `models-check` in a shell) so you talk about
the member's real setup, not a guess. Never print or ask for a token or key.

## Which model does what

| Job | Use | How |
|---|---|---|
| Daily build work with a clear scope | Sonnet 5.5 | `/model sonnet` |
| Planning, a hard bug, a review before shipping | Opus 5.5 | `/model opus`, or Sonnet with an Opus advisor |
| Summaries, extraction, sorting, many small jobs | Haiku 5.5 | `/model haiku`, or `model: haiku` in a skill or subagent |
| The hardest and longest tasks | Fable | `/model fable`. It may bill usage credits, so read the consent prompt |
| Plan with Opus, build with Sonnet | `opusplan` | `/model opusplan` |
| A GPT model | Codex | `codex -m <model>`, or `model = "<model>"` in `~/.codex/config.toml`. See Codex's `/model` list |
| Grok and other models | Cursor or Grok Bot | `cursor-agent --list-models`, then `cursor-agent --model <name>`. Grok Bot uses the member's Cursor account |

Aliases (`sonnet`, `opus`, `haiku`) move to the newest version when Claude Code updates. Pin a version
with its full name, for example `claude-sonnet-5-5`, only when a job must not change.

## Effort: start on medium

Effort is how much the model thinks before it acts. Opus 5.5, Sonnet 5.5 and Haiku 5.5 default to medium,
and Anthropic's tests found Opus 5.5 at medium matches or beats Opus 5 at high.

- Set the default: `/effort medium`, then Enter. Claude Code saves it per model under `modelSettings`.
- Raise it for one task: `/effort high`, then press `s` for this session only.
- One deep turn: put `ultrathink` in the prompt. The session level does not change.
- A skill that always needs more or less: add `effort: high` or `effort: low` to its frontmatter.
- `max` is for hard problems you leave running. Test it before using it widely, because it can overthink.
- An older top-level `effortLevel` key does not apply to Opus 5.5. If `/models-check` shows `xhigh` from that key,
  run `/effort medium` to save a per-model level.
- Codex: `model_reasoning_effort = "medium"` in `~/.codex/config.toml`.

## The advisor

The advisor is a stronger model that the main model consults at key moments: before it commits to an approach,
when an error keeps coming back, and before it says it is done. It reads the whole conversation.

- Turn it on: `/advisor opus` (saved as `advisorModel`), or `claude --advisor opus` for one session.
- Good default pairing: Sonnet main with an Opus advisor. Haiku main with an Opus advisor is the cheapest strong plan.
- The advisor must be at least as capable as the main model. Opus main accepts Opus or Fable only.
- Ask for it on a hard call: "consult the advisor before you continue".
- While it runs you see an `Advising` line. Press `Ctrl+O` to read the advice.
- It needs the Anthropic API or a Claude subscription. It is not on Bedrock, Vertex or Foundry.
- Advisor tokens count against the same plan limits, and `/usage` includes them.

## Check usage

- `/usage` shows plan limits, what used them, and fixes. Press `f` when it offers a fix.
- `/status` shows the live model and the signed-in account.
- If `ANTHROPIC_API_KEY` is set, Claude Code bills the metered API instead of the subscription. `/models-check` warns about this.

## Two subscriptions, one failover

Use two subscriptions the member pays for and owns. Pick one way:

**bb account pool** (if the member uses bb). bb switches to the next account when one runs out.

```
bb pool account add --provider claude --login
bb pool account login-complete --session <id> --code-stdin
bb pool routing claude
bb pool account list
```

Lower priority numbers run first: `bb pool account priority <id> 10`. Existing conversations stay on their account.

**A second `CLAUDE_CONFIG_DIR`** (any terminal). Each folder holds its own login, settings and plugins.

```
models-check login add work
CLAUDE_CONFIG_DIR=~/.claude-work claude auth login
alias claude-work='CLAUDE_CONFIG_DIR=~/.claude-work claude'
```

When the first login hits its limit, run `claude-work` in the same project folder. The files and AGENTS.md are the
same, but chat history is kept per folder, so point the new session at the spec or notes. Install the aios packs
in the second folder too. Codex works the same way with `CODEX_HOME`.

`--fallback-model` is different: it switches model when a model is overloaded, not when a plan runs out.

## Check that it worked

`models-check` lists every login as `signed in`, effort as `medium`, the advisor you chose, and
"Claude logins ready for failover: 2". End with what changed and the one next step, then `/aios`. British English.
