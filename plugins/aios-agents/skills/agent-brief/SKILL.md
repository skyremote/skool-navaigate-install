---
name: agent-brief
description: Write a brief for a sub-agent with a measurable objective, a return format, tools, boundaries and a stopping point, then check it before sending. Use when handing work to a sub-agent, a reviewer, a researcher or another thread.
---

# Brief a sub-agent

A sub-agent knows only what the brief says. A vague one-liner comes back as a vague
answer, or as work you did not ask for.

1. Confirm the job passes `agent-or-not` (parallel work, isolation, or a context that
   would flood). If not, do it in the main conversation.
2. Start from the template:
   ```
   aios-agent brief new --out briefs/<job>_v1.md
   ```
   (or `aios-agent brief new` to print it). In Codex or Cursor use `~/.local/bin/aios-agent`.
3. Fill every section:
   - **Objective**: one sentence, then `Done when:` with a measurable test (a count,
     a file, a passing command).
   - **Format**: exactly what comes back, with a length limit.
   - **Context**: only what the agent cannot find itself: the diff, the files, the decision so far.
   - **Tools**: `Use:` and `Avoid:` lines.
   - **Boundaries**: `You own:` and `Do not touch:` lines.
   - **Stop**: when to stop (the Done when test) and a limit (attempts or minutes).
4. Check it:
   ```
   aios-agent brief check briefs/<job>_v1.md
   ```
   `READY` means send it. `NOT READY` lists what is missing; fix and re-check.
5. Send it to the agent (in Claude Code, for example "Use the aios-agents:code-reviewer
   agent with this brief: ..."). Ask for the result in the format the brief set.
6. When it returns, check the result against `Done when` yourself before you use it.

Example `Done when` lines:
- "a table of exactly 3 UK accounting tools for a sole trader, each with a monthly price and a link"
- "a list of findings with file and line, or the words No findings"
- "the test command `python3 -m unittest` passes"

Finish with the brief's path, the check result and one next action. British English.
