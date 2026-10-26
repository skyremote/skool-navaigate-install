---
name: agent-or-not
description: Decide whether a job needs a sub-agent or should stay in the main conversation with skills, and avoid building a crew shaped like an org chart. Use when someone asks to add an agent, build a team of agents, split work across agents, or asks why their agents feel slow or expensive.
---

# Agents without sprawl

Default: one main conversation does the work, with skills for the repeated jobs.
A sub-agent starts with an empty context, knows only its brief, and returns only a
summary. That costs a cold start, time and tokens, and detail is lost both ways.

## When a sub-agent earns its place
Say yes only for one of these three reasons, and name which one:
1. **Parallel work.** Several independent jobs that can run at the same time and
   whose working context can be thrown away afterwards (for example, research three
   suppliers at once).
2. **Isolation.** The job needs different tool limits or a fresh pair of eyes that
   has not seen your reasoning (for example, a read-only reviewer that cannot edit).
3. **A context that would flood.** The work reads far more than you need back
   (for example, scanning hundreds of files or pages for one answer).
If none applies, do it in the main conversation. If the job repeats, make it a skill
(module 6, `aios-skills`) rather than an agent.

## The org-chart trap
Do not build one agent per department or role (sales agent, marketing agent, finance
agent). Anthropic's advice of 22 October 2026, "When to fold subagents into your main
agent loop", written for teams building agents on Claude Platform, found a single agent with skills often beat both one giant prompt and a
crew of specialist sub-agents on quality, cost and speed, and warned against agent
designs that copy the org chart. The same reasoning applies to your own setup. Keep sub-agents for parallel work, isolation, or
context bloat, and fold the rest into skills.

## The small crew in this pack
All three are read-only, start without your CLAUDE.md (`omitClaudeMd: true`) and take
everything from the brief:
- `code-reviewer`: Read, Grep, Glob. Finds real bugs in a change; never edits.
- `design-critic`: Read, Grep, Glob, WebFetch. Checks a page, slide or screenshot against plain rules.
- `researcher`: WebSearch, WebFetch, Read, Grep, Glob. Returns a short cited answer.
Run `aios-agent crew` to list them with their tools. In Claude Code they appear as
`aios-agents:code-reviewer` and so on. Use them only through a brief (see `agent-brief`).

## Prove it: one loop against one loop plus a reviewer
Run the same task twice, headless, and compare:
```
claude -p "<task>. Do not use sub-agents." --output-format json > one-loop.json
claude -p "<task>. When done, send the change to the aios-agents:code-reviewer agent with a brief, then fix what it finds." --output-format json > with-reviewer.json
aios-agent compare one-loop.json with-reviewer.json
```
The table shows wall time, turns, tokens, list-price cost and sub-agents spawned.
Write down what the reviewer actually found. Keep the reviewer for this kind of job
only if it found a real problem the single loop missed, worth the extra time and tokens.

## Codex and Cursor
The decision rule and the brief work the same. The three agent files are Claude Code
plugin agents. In Codex or Cursor, open a separate chat or thread, paste the agent
file's body followed by the brief, and give it read-only access.

## Never
- Never add an agent because it looks organised. Name the reason from the three above.
- Never delegate with a one-line request. Write a brief.
- Never let a reviewer agent edit files. It reports; the main conversation fixes.

Finish with the decision, the reason, and one next action. British English.
