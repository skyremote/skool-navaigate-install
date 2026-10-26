---
plugins: ["../..", "../../../aios"]
description: A member wants one agent per department. The answer must start with one loop and skills, and name the org-chart trap.
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

I run Acme Studio, a five-person design agency. I want to set up Claude Code with a sales agent, a marketing agent, an operations agent, a finance agent and a delivery agent, all managed by a boss agent. Can you plan out the agents for me?
