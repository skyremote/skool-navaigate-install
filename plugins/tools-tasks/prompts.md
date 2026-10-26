# Prompts: tools-tasks

Paste one into Claude Code, Codex or Cursor.

## 1. What a good task looks like

```text
Use tools-tasks. Make the practice files in ~/Tasks-practice, check the task list, then show me what is overdue and the three things for today as of 26 October 2026.
```

**What it does:** checks a fictional task list and picks today's three from a practice export.
**How you know it worked:** the check says `PASS`, two tasks show as overdue by list, and exactly three are picked.

## 2. A brief into ClickUp

```text
Use tools-tasks. Turn this one-page brief into tasks with an owner, a due date and a "done when" each, show me, and after I say yes, add them to my ClickUp list "Northwind": <paste the brief>
```

**What it does:** writes and checks the task list, waits for your yes, creates the tasks in ClickUp and reads them back.
**How you know it worked:** the tasks appear in that ClickUp list with the same names, owners and dates, and you get
their links.

## 3. What should I do today?

```text
Use tools-tasks. List my overdue ClickUp tasks grouped by client and pick the three I should do today. Do not change anything in ClickUp.
```

**What it does:** reads your open tasks, groups the overdue ones and picks three.
**How you know it worked:** three tasks, each with its list and due date, and nothing in ClickUp has changed.
