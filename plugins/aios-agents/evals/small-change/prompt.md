---
plugins: ["../..", "../../../aios"]
description: A tiny, low-risk change. The answer should keep it in the main conversation rather than spawn a reviewer.
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

I've changed two lines in a CSS file to make the contact button dark blue instead of light blue. Should I spin up a separate reviewer agent to check it before I commit? Yes or no, and why.
