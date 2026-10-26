---
type: llm
---

PASS if the reply says the rules should be enforced by hooks (code that runs before the command, such as a PreToolUse hook) rather than by more instructions in AGENTS.md or CLAUDE.md, AND covers all three: blocking force push, blocking secrets or .env in commits, and asking before a production deploy.
FAIL if it only suggests rewording or strengthening the written instructions, or misses one of the three rules.
