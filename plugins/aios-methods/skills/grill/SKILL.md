---
name: grill
description: Interview me before you build, one question at a time, then write a short spec with runnable checks and a shared glossary. Use for /grill, "grill me", "interview me first", or any vague build request.
---

# Grill me: interview before you build

The member has an idea. Your job is to find what they actually want before any code exists.
Do not write code, plans or files beyond the spec and glossary until the interview ends.

## The interview

1. Ask one question at a time. Wait for the answer. Never send a list of ten questions.
2. Offer your best guess with each question, so the member can say "yes" instead of typing:
   "Who uses this? My guess: only you, on your laptop."
3. Cover, in this order, and skip what is already clear:
   - the result: what changes for the user when this is done;
   - who uses it, and where (phone, laptop, a client's machine);
   - what "done" looks like, as checks the agent can run (a test, a build, a file that must exist);
   - what is out of scope for this round;
   - the words: when the member uses a fuzzy or double word ("customer" and "client"), ask which one
     they mean and record it in the glossary;
   - the riskiest assumption, and how we would know quickly if it is wrong.
4. Stop when you could explain the feature back in three sentences and the member agrees.
   Most interviews take five to ten questions. If you pass fifteen, summarise and ask what is still unclear.

## Write it down

Use the `aios-methods` helper from this pack. In Codex and Cursor it is `~/.local/bin/aios-methods`.

```
aios-methods glossary init            # once per project; creates GLOSSARY.md
aios-methods glossary add "Invoice" "a bill we send to one client for one month" --avoid "bill, statement"
aios-methods spec new <slug>          # creates docs/specs/<slug>.md
```

Fill the spec from the answers: Goal, Who it is for, Done when (each line a command in backticks),
Out of scope, Decisions, Open questions. Write "None" under Open questions only when there are none.

Then run both checks and show the real output:

```
aios-methods glossary check
aios-methods spec check docs/specs/<slug>.md
```

Both must exit 0 before building. If a check fails, fix the file, not the check.

## Hand over

Tell the member the spec path and the one next step. For a new feature that is usually
`aios-methods worktree new <slug>`, then a fresh session in that folder that reads the spec.
A fresh session keeps the interview's back-and-forth out of the build's context.

Keep the glossary short and in the member's own words. Use the same words in every later prompt.
British English.
