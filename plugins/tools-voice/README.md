# tools-voice (AIOS 2.0, module 12: the shelf, tools)

Make AI write like you, not like AI. You install the public **voice-skill-builder** (MIT), point it at your own
transcripts and emails, and this pack gives your agent our method: a profile built from evidence, three test pieces
you correct line by line, a calibration log, and a `check` that every draft passes before it ships.

- **Your words only.** Your transcripts, your emails, your corrections. No one else's profile is included.
- **Local.** No account, no API key, no upload.
- **Checked.** `tools-voice check` flags generated-text words, your own banned words, fragment chains and stacks.

## Install

1. Install the start plugin `aios` first (module 1).
2. Install the public tool once:
   `git clone https://github.com/skyremote/voice-skill-builder ~/.claude/skills/voice-skill-builder`
   (Codex and Cursor: clone it into `~/.agents/skills/voice-skill-builder`).

**Claude Code:** `/aios install tools-voice` (or `/plugin install tools-voice@navaigate-aios`), then `/reload-plugins`.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-voice
./install.sh tools-voice --check
```

Needs Python 3.9 or later.

## Use

```
tools-voice doctor
tools-voice sample ~/Voice-practice
tools-voice check ~/Voice-practice/draft-bad_v1.md
tools-voice new "Sam"
tools-voice evidence ~/Private/transcripts --speaker "Sam" --out ~/Private/VOICE_EVIDENCE.md
tools-voice check my-email_v1.md --profile ~/.claude/skills/sam-voice/PROFILE.md
tools-voice calibrate --profile ~/.claude/skills/sam-voice/PROFILE.md --before "..." --after "..." --lesson "..."
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-voice/SKILL.md](skills/tools-voice/SKILL.md).

## Licence

MIT. voice-skill-builder is MIT and is installed by you from its own repository; this pack calls it, it does not copy it.
