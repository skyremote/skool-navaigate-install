---
plugins: ["../..", "../../../aios"]
description: The member wants three rules enforced. The answer must use hooks, not more instructions in a rules file.
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Twice now my agent has tried to force push, and last week it committed my .env file with a live key in it. I also never want it deploying to Vercel production without asking me. I've written all of this in my AGENTS.md and it still happens. What should I do?
