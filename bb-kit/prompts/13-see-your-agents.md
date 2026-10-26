# Module 13 · See what your agents are doing: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 13.1 · Research three options in parallel and let me watch

**What it does:** Hands three research jobs to three helper agents at once and writes one comparison. With BB Overlay, Helper Desk shows each helper working, with its tokens and time.

**How you know it worked:** The report holds a one-page comparison with a source per row, and `bb helper-desk show` lists three helpers for this chat.

~~~text
Research these three options in parallel and give me a one-page comparison.

The three options (edit this line): Squarespace, Wix and Webflow, as a website builder for a two-person design studio.

Here is how:
1. Give each option to its own helper agent at the same time, with the same short brief: price for a small business plan, what it is best at, one weakness, and the source page you read. Ask each for at most 150 words.
2. While they work, tell me to open Helper Desk to watch them: press + beside the tabs on the right and pick Helper Desk (BB Overlay).
3. When all three are back, write the comparison as a table: option, price, best at, weakness, source.
4. Run `bb helper-desk show "$BB_THREAD_ID"` and show me what it recorded for this chat: one line per helper, with its tokens and time. If the command is not available, BB Overlay is not installed: say so.
5. Say in one line whether three helpers were worth it here, or whether one loop would have done.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m13-parallel-research_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m13-parallel-research_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 13.2 · Tell me which chats need me

**What it does:** Checks every chat in this project and the Agent Board for this one, and tells you in plain words which ones are waiting for you.

**How you know it worked:** The report lists each chat that needs you with the reason, or says plainly that none do.

~~~text
Look at my chats and tell me if any of them, or any helper, needs me.

Here is how:
1. Run `bb thread list --project "$BB_PROJECT_ID" --json`. List the chats whose status is waiting, needs input, error or idle with an unread result. Give each one line: title, what it needs.
2. Run `bb agent-board show "$BB_THREAD_ID"` and say whether its Needs Attention column holds anything. If the command is not available, say so in one line.
3. Tell me where the board is in bb: Agent Board in the right panel, and the Kanban board in the sidebar (BB Overlay).
4. If nothing needs me, say so plainly. Do not change any chat.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m13-needs-me_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m13-needs-me_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 13.3 · Should I hand this chat off?

**What it does:** Reads this chat's cache countdown and how full its context is, and tells you whether to keep going or hand off to a fresh chat.

**How you know it worked:** The report shows the cache status, the context use, and a yes or no with one reason.

~~~text
How long until this chat's cache goes cold, how full is its context, and should I hand it off to a new chat?

Here is how:
1. Run `bb cache-clock status "$BB_THREAD_ID"` and tell me how long until the cache goes cold. Explain in one line what that means: after it goes cold, the next message costs full price again. If the command is not available, BB Overlay's Cache Clock is not installed: say so.
2. Run `bb thread context --self` and tell me how much of the context window is used and what fills it most.
3. Give me a yes or no on handing off, with one reason. Hand off when the context is more than about two-thirds full, or when the next job is a new topic.
4. Tell me how to do it if I want to: press Hand off on the Cache Clock above the chat box. It writes a brief and opens a new chat with it, ready for me to send. Do not hand off yourself.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m13-hand-off_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m13-hand-off_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
