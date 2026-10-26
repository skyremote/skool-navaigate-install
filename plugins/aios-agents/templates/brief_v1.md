# Brief: <short name of the job>

## Objective
<One sentence: what the agent must produce.>
Done when: <a measurable test, for example "a table of exactly 3 tools with a price each", "tests pass", "a file at reviews/login_v1.md">

## Format
<Exactly what comes back: headings, a table, a list of findings with file and line, at most N words.>

## Context
<Only what the agent cannot find itself: the files, the diff, the decision so far. Paste it or name the path.>

## Tools
Use: <the tools or sources to use, for example Read, Grep, the diff below, official docs only>
Avoid: <what not to use, for example no web search, no paid APIs>

## Boundaries
You own: <the one thing this agent is responsible for>
Do not touch: <files, folders, accounts or decisions it must leave alone, for example "do not edit any file">

## Stop
Stop when <the Done when test is met>, or after <N> attempts or <N> minutes, and report what you have and what blocked you.
