---
plugins: ["../..", "../../../aios"]
description: The member wants the agent to stop claiming done while tests fail. The answer must set up runnable checks and a Stop gate.
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Claude Code keeps telling me a change is finished when the tests in my project are actually failing. How do I set my project up so it can't say it's done until the tests and the build pass? Give me the exact steps.
