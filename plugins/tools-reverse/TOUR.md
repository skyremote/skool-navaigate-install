# Tour: module 12, tools: reverse engineering

`/aios learn 12 tools-reverse` follows these steps, one at a time. Show the real output, then check it.
Only targets the member owns or may examine. Never get round licence checks, DRM, logins or paywalls.

## Step 1: Find the command
- **Command:** `tools-reverse --version`, then `tools-reverse doctor`

## Step 2: A good investigation
- **Command:** `tools-reverse sample ~/Reverse-practice`, then `tools-reverse check ~/Reverse-practice/acme-calculator_investigation_v1.md`
- **They should see:** `PASS`.

## Step 3: See it fail
- **Do:** change one finding's status to "observed" and add "probably", or delete an Evidence part. Check again.
- **They should see:** the exact line to fix.

## Step 4: Install REA
- **Command:** `npx rea-agents setup`, review the plan, approve, restart the agent.
- **Check:** `tools-reverse doctor` finds REA's skill, and the agent lists REA tools.

## Step 5: Their own target
- **Do:** `tools-reverse new` for something they own (their own site is ideal), fill in the basis, `check`.
- **Then:** prompt 2 from prompts.md.
- **Check:** every finding has REA evidence; unknowns are listed.

## Recap
Scope, evidence, status, unknowns, check. Nothing outside the scope.
