# 13 · See what your agents are doing
pack: aios
cmd: aios-guide

## 13.1 · Research three options in parallel and let me watch
what: Hands three research jobs to three helper agents at once and writes one comparison. With BB Overlay, Helper Desk shows each helper working, with its tokens and time.
check: The report holds a one-page comparison with a source per row, and `bb helper-desk show` lists three helpers for this chat.
~~~
Research these three options in parallel and give me a one-page comparison.

The three options (edit this line): Squarespace, Wix and Webflow, as a website builder for a two-person design studio.

Here is how:
1. Give each option to its own helper agent at the same time, with the same short brief: price for a small business plan, what it is best at, one weakness, and the source page you read. Ask each for at most 150 words.
2. While they work, tell me to open Helper Desk to watch them: press + beside the tabs on the right and pick Helper Desk (BB Overlay).
3. When all three are back, write the comparison as a table: option, price, best at, weakness, source.
4. Run `bb helper-desk show "$BB_THREAD_ID"` and show me what it recorded for this chat: one line per helper, with its tokens and time. If the command is not available, BB Overlay is not installed: say so.
5. Say in one line whether three helpers were worth it here, or whether one loop would have done.

<<RULES>>

<<FINISH m13-parallel-research>>
~~~

## 13.2 · Tell me which chats need me
what: Checks every chat in this project and the Agent Board for this one, and tells you in plain words which ones are waiting for you.
check: The report lists each chat that needs you with the reason, or says plainly that none do.
~~~
Look at my chats and tell me if any of them, or any helper, needs me.

Here is how:
1. Run `bb thread list --project "$BB_PROJECT_ID" --json`. List the chats whose status is waiting, needs input, error or idle with an unread result. Give each one line: title, what it needs.
2. Run `bb agent-board show "$BB_THREAD_ID"` and say whether its Needs Attention column holds anything. If the command is not available, say so in one line.
3. Tell me where the board is in bb: Agent Board in the right panel, and the Kanban board in the sidebar (BB Overlay).
4. If nothing needs me, say so plainly. Do not change any chat.

<<RULES>>

<<FINISH m13-needs-me>>
~~~

## 13.3 · Should I hand this chat off?
what: Reads this chat's cache countdown and how full its context is, and tells you whether to keep going or hand off to a fresh chat.
check: The report shows the cache status, the context use, and a yes or no with one reason.
~~~
How long until this chat's cache goes cold, how full is its context, and should I hand it off to a new chat?

Here is how:
1. Run `bb cache-clock status "$BB_THREAD_ID"` and tell me how long until the cache goes cold. Explain in one line what that means: after it goes cold, the next message costs full price again. If the command is not available, BB Overlay's Cache Clock is not installed: say so.
2. Run `bb thread context --self` and tell me how much of the context window is used and what fills it most.
3. Give me a yes or no on handing off, with one reason. Hand off when the context is more than about two-thirds full, or when the next job is a new topic.
4. Tell me how to do it if I want to: press Hand off on the Cache Clock above the chat box. It writes a brief and opens a new chat with it, ready for me to send. Do not hand off yourself.

<<RULES>>

<<FINISH m13-hand-off>>
~~~
