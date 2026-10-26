# 14 · Talk to it
pack: aios
cmd: aios-guide

## 14.1 · Say your brief instead of typing it
what: You press the microphone in the bb chat box and say the request. bb types your words; Claude drafts the email. Say this one aloud.
check: Your spoken words appear in the chat box, and the reply is a draft under 100 words.
~~~
Write a short thank-you email to the client from today's call, and keep it under 100 words.
~~~

## 14.2 · Turn a voice memo into to-dos
what: Transcribes a voice memo with bb's own voice service, then saves each job in it as a to-do linked to this chat (BB Overlay).
check: The report shows the transcript, and the jobs appear in the To-do panel (Cmd+Shift+D).
~~~
Transcribe this voice memo and turn it into to-dos.

The memo: the audio file I attached, or else the newest audio file in `00_inbox/` (edit this line if it is somewhere else).

Here is how:
1. Find the memo. If none is attached and `00_inbox/` has no audio file, stop and tell me to attach one.
2. Transcribe it with bb's voice service: `bb voice transcribe "<path to the memo>"`. If bb has no voice service ready (it needs a bb account or a signed-in Codex), use Whisper on this computer instead, if it is installed: `whisper "<path to the memo>" --model base --language en --output_format txt --output_dir 00_inbox/`. If neither works, tell me to choose a voice service in Settings, AI services, and stop.
3. Show me the transcript.
4. Pick out each job in it. Add each one as a to-do with the `workspace_todo` tool (action `add`), one short imperative line each. If that tool is not available, BB Overlay is not installed: list the jobs instead.
5. Save the transcript next to the memo as `<memo name>_transcript_v1.md`.

<<RULES>>

<<FINISH m14-memo-to-todos>>
~~~

## 14.3 · Build a writing-voice skill from how I talk
what: Reads three transcripts of you talking, writes a short voice guide as a skill in this folder, and rewrites one post in your voice, before and after.
check: `.claude/skills/my-voice/SKILL.md` exists, and the report shows the post before and after.
~~~
Build a writing-voice skill from these three transcripts of me talking, then rewrite this post in my voice.

The transcripts: the three text files in `00_inbox/voice/` (edit this line if they are somewhere else).
The post to rewrite (edit this): "We are thrilled to announce our new brand refresh package, designed to elevate your business to new heights."

Here is how:
1. Read the three transcripts. If there are fewer than three, use what is there and say so.
2. Write `.claude/skills/my-voice/SKILL.md` in this folder: a one-line description ("Write in my voice. Use when I ask for a post, an email or a reply in my voice."), then at most 30 lines: words I use, words I never use, how long my sentences are, how I open and close, and three short real quotes from the transcripts. Never invent a quote.
3. Rewrite the post above with that guide. Show it before and after, side by side.
4. Tell me the skill loads in new chats in this folder, and how to use it: "write this in my voice".

<<RULES>>

<<FINISH m14-voice-skill>>
~~~
