# Tour: module 12, tools: tasks

`/aios learn 12 tools-tasks` follows these steps, one at a time. Show the real output, then check it.
Never create or change a ClickUp task during the tour without the member's yes.

## Step 1: Find the command
- **Command:** `tools-tasks --version`

## Step 2: A good task list
- **Command:** `tools-tasks sample ~/Tasks-practice`, then `tools-tasks check ~/Tasks-practice/northwind_tasks_v1.md`
- **They should see:** `PASS`.

## Step 3: A bad one
- **Do:** add a line "- Look into pricing | Owner: Sam". Check again.
- **They should see:** too vague, no due date, no "done when".

## Step 4: Today
- **Command:** `tools-tasks today ~/Tasks-practice/open-tasks_v1.json --on 2026-10-26`
- **They should see:** two overdue, three for today.

## Step 5: Connect ClickUp
- **Do:** `/mcp`, clickup, sign in (Codex and Cursor: add the URL first).
- **Check:** the agent lists their spaces.

## Step 6: Their first real brief
- **Do:** prompt 2 from prompts.md. They say yes before anything is created.
- **Check:** the tasks are in ClickUp, read back with links.

## Recap
Verb, owner, date, done when, checked, then ClickUp. Three for today.
