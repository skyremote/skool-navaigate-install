---
plugins: ["../..", "../../../aios"]
description: The member wants a PR description. It must have Testing with real output, a Risk level and How to revert.
max_turns: 8
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Write the pull request description for my change. I added a 10% discount for orders over £500 in invoice.py and five new tests. The test run printed "Ran 8 tests in 0.002s" and "OK".
