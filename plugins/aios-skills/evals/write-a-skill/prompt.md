---
plugins: ["../..", "../../../aios"]
description: A member wants to turn a weekly job into a skill. The answer must keep it short and come with evals.
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Every Friday I send the same status email to my clients and I keep explaining the format to Claude again. Should I make this into a skill? If yes, show me exactly what the files should contain and how I know it works.
