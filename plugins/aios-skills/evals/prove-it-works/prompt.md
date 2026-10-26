---
plugins: ["../..", "../../../aios"]
description: A member wants proof that a plugin skill helps. The answer must use claude plugin eval with a no-plugin baseline.
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

I built a small Claude Code plugin with one skill that formats my invoices. It triggers, but how do I prove it actually makes the answers better than plain Claude? Give me the command and tell me how to read the result.
