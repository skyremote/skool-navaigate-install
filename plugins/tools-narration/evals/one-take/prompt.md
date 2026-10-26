---
plugins: ["../..", "../../../aios"]
max_turns: 8
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
---

Narrate my 12-slide deck. Just do each slide as its own request so if one fails we only redo that one.
