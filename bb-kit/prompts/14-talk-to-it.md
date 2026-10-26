# Module 14 · Talk to it: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 14.1 · Say your brief instead of typing it

**What it does:** You press the microphone in the bb chat box and say the request. bb types your words; Claude drafts the email. Say this one aloud.

**How you know it worked:** Your spoken words appear in the chat box, and the reply is a draft under 100 words.

~~~text
Write a short thank-you email to the client from today's call, and keep it under 100 words.
~~~

## Prompt 14.2 · Turn a voice memo into to-dos

**What it does:** Transcribes a voice memo with bb's own voice service, then saves each job in it as a to-do linked to this chat (BB Overlay).

**How you know it worked:** The report shows the transcript, and the jobs appear in the To-do panel (Cmd+Shift+D).

~~~text
Transcribe this voice memo and turn it into to-dos.

The memo: the audio file I attached, or else the newest audio file in `00_inbox/` (edit this line if it is somewhere else).

Here is how:
1. Find the memo. If none is attached and `00_inbox/` has no audio file, stop and tell me to attach one.
2. Transcribe it with bb's voice service: `bb voice transcribe "<path to the memo>"`. If bb has no voice service ready (it needs a bb account or a signed-in Codex), use Whisper on this computer instead, if it is installed: `whisper "<path to the memo>" --model base --language en --output_format txt --output_dir 00_inbox/`. If neither works, tell me to choose a voice service in Settings, AI services, and stop.
3. Show me the transcript.
4. Pick out each job in it. Add each one as a to-do with the `workspace_todo` tool (action `add`), one short imperative line each. If that tool is not available, BB Overlay is not installed: list the jobs instead.
5. Save the transcript next to the memo as `<memo name>_transcript_v1.md`.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m14-memo-to-todos_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m14-memo-to-todos_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 14.3 · Build a writing-voice skill from how I talk

**What it does:** Reads three transcripts of you talking, writes a short voice guide as a skill in this folder, and rewrites one post in your voice, before and after.

**How you know it worked:** `.claude/skills/my-voice/SKILL.md` exists, and the report shows the post before and after.

~~~text
Build a writing-voice skill from these three transcripts of me talking, then rewrite this post in my voice.

The transcripts: the three text files in `00_inbox/voice/` (edit this line if they are somewhere else).
The post to rewrite (edit this): "We are thrilled to announce our new brand refresh package, designed to elevate your business to new heights."

Here is how:
1. Read the three transcripts. If there are fewer than three, use what is there and say so.
2. Write `.claude/skills/my-voice/SKILL.md` in this folder: a one-line description ("Write in my voice. Use when I ask for a post, an email or a reply in my voice."), then at most 30 lines: words I use, words I never use, how long my sentences are, how I open and close, and three short real quotes from the transcripts. Never invent a quote.
3. Rewrite the post above with that guide. Show it before and after, side by side.
4. Tell me the skill loads in new chats in this folder, and how to use it: "write this in my voice".

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m14-voice-skill_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m14-voice-skill_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
