# Module 15 · Work from anywhere, and share safely: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 15.1 · Check my agents from my phone

**What it does:** Checks whether this bb is signed in to a getbb.app account (needed for your phone), tells you the one step if it is not, and sends a test notification.

**How you know it worked:** The report says whether remote access is on, gives your getbb.app link if it is, and shows the test notification result.

~~~text
Set up bb so I can check my agents from my phone, and send me a test notification.

Here is how:
1. Run `bb account --help`, then check whether this bb is signed in to a getbb.app account. If it is not, tell me the one step: run `bb account login` in a terminal (or Settings, Account in bb) and approve the code in my browser. Do not sign in for me.
2. If it is signed in, run `bb connect --help` and give me my bb's https link on getbb.app, so I can open it on my phone and add it to my home screen.
3. Send a test notification: `bb push-notifications test`, and show `bb push-notifications status`. Tell me a phone needs the getbb.app page open once, with notifications allowed.
4. Tell me what I will see on my phone: the same sidebar and chats, and a notification when a chat finishes or needs me.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m15-phone_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m15-phone_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 15.2 · Run a job on my other machine

**What it does:** Lists the machines this bb can use and starts a small job on the other one, so it keeps running with your laptop shut. If you have only one machine, it tells you how to add one.

**How you know it worked:** The report lists your machines, and either a new chat running on the other machine or the steps to add one.

~~~text
Start this job on my other machine, so it keeps going when I shut my laptop, and tell me when it is done.

The job (edit this line): write a one-page summary of this folder to `80_aios/reports/folder-summary_v1.md`.

Here is how:
1. Run `bb machine list` and show me the machines: name, status.
2. If there is only one machine, stop the job and tell me how to add one: Settings, Machines in bb, then follow the steps for a Mac at home, a mini PC or a small cloud server (VPS). Say that BB Overlay also adds "Send to my always-on machine" when I right-click a chat.
3. If there is a second machine that is connected, write the job to `80_aios/briefs/folder-summary_v1.md` and start it there: `bb thread spawn --project "$BB_PROJECT_ID" --machine "<its name>" --title "Folder summary (other machine)" --prompt-file 80_aios/briefs/folder-summary_v1.md --json`.
4. Wait for it with `bb thread wait <id> --timeout 20m` and show me its answer with `bb thread output <id>`.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m15-other-machine_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m15-other-machine_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 15.3 · Hide names before I record or share my screen

**What it does:** Turns on BB Overlay's Screen Share mode, which greys out every name, email, phone number and amount on every bb screen, then checks it is on.

**How you know it worked:** `bb screen-share status` says on, and names on your screen show as grey bars.

~~~text
Turn on screen share mode before I record, and check it is on.

Here is how:
1. Run `bb screen-share on`, then `bb screen-share status`. If the command is not available, BB Overlay's Screen Share mod is not installed: say so.
2. Tell me what it does: names, emails, phone numbers and amounts turn into grey bars on every screen that shows this bb, my phone included. The agent still sees the real text.
3. Tell me the two things it does not do: it does not change what is copied or pasted, so I never paste a key on camera; and it does not hide what is in other apps.
4. Tell me how to switch it off after recording: `bb screen-share off`, or type `/screenshare` again.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m15-screen-share_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m15-screen-share_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
