---
name: tools-voice
description: Build the member's OWN writing-voice skill from their own transcripts, emails and line edits (with the public voice-skill-builder), then check drafts against it and record their corrections. Use for "make it sound like me", "this sounds like AI", "build my voice", "de-slop this", or checking a draft before it ships.
---

# Your writing voice

This is the method we use for our own writing, without anyone's profile in it. The member builds a voice skill from
their own words, and every draft runs through a check before it ships. A voice is built from evidence (their own
quotes and their own corrections), never from adjectives like "warm" or "confident".

## The command

Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/tools-voice"`. Codex and Cursor: `tools-voice` (in `~/.local/bin`).

| Command | What it does |
|---|---|
| `doctor` | Says whether the public voice-skill-builder is installed, and how to install it. |
| `sample <folder>` | Fictional practice files: a transcript of Sam at Acme Studio, a good draft and a bad one. |
| `new "<first name>" [--folder ~/.claude/skills]` | Makes `<name>-voice/` with SKILL.md, PROFILE.md and EXAMPLES.md. Never overwrites. |
| `evidence <transcripts...> --speaker "<label>" --out <private file>` | Runs voice-skill-builder's evidence script on their own words. |
| `check <draft> [--profile PROFILE.md]` | FAIL or PASS: banned words, their own banned words, fragment chains, dash and adjective stacks. |
| `calibrate --profile ... --before ... --after ... --lesson ...` | Adds one of their corrections to the calibration log. |

## Build the voice (once, about an hour)

1. **Install the public tool.** `doctor`. If missing: `git clone https://github.com/skyremote/voice-skill-builder ~/.claude/skills/voice-skill-builder`
   (Codex and Cursor: `~/.agents/skills/voice-skill-builder`). MIT licence.
2. **Collect their words.** Only material they own or have permission to use: call transcripts where they are labelled,
   sent emails, drafts they corrected. 15,000 spoken words show the rhythm. Keep this folder private.
3. **Pull the evidence.** `evidence <folder> --speaker "<their label>" --out <private folder>/VOICE_EVIDENCE.md`.
   Statistics are leads, not rules.
4. **Make the skill.** `new "<first name>"`. Fill in PROFILE.md from the evidence. Each rule must change a draft and
   carry a quote. Style, not subject: "starts with So and chains clauses with and" is voice; "talks about AI" is not.
5. **Write three test pieces** in different situations (a short email, a public post, a teaching piece). The member
   edits them line by line. Record every meaningful edit with `calibrate`. Put only approved pieces in EXAMPLES.md.
6. **Prove it.** In a fresh session, ask for a new email in their voice, run `check`, and have them read it aloud.

## Every draft after that

1. Read their PROFILE.md and EXAMPLES.md before drafting.
2. Draft, then `check <draft> --profile <their PROFILE.md>`. Fix every line it flags.
3. The read-aloud test: if they could not say it on a call, rewrite it as one spoken sentence.
4. Every strong claim needs a real name or number. Never invent one; ask.
5. When they correct a line, `calibrate`. Their corrections overrule older rules.

## Checking a draft without running the command

If you cannot run `tools-voice check` in this session, check by hand against the same list, then tell the member
to run `tools-voice check <draft>` themselves before it ships. Say "not ready" when anything below appears, name
each word it uses, and offer a rewrite as one spoken sentence. Never call a draft ready if it breaks one of these.

- **Generated-text and jargon words:** "delve", "unlock", "unleash", "elevate", "game-changer", "game changer", "revolutionise", "revolutionize", "seamless", "seamlessly", "leverage", "empower", "robust", "cutting-edge", "in today's fast-paced world", "take it to the next level", "whether you're a beginner or an expert", "ever wondered", "tapestry", "testament to", "navigate the complexities", "it's important to note", "in conclusion", "synergy", "wedge", "moat", "flywheel", "north star", "land and expand".
- **Fragment chains:** three or more fragments of four words or fewer in a row ("Seamless onboarding. Zero friction.").
- **Stacks:** more than one long dash in a piece, or three adjectives in a row.

## The five rules we start everyone with (they keep, change or drop each one)

1. Chain clauses the way people speak ("and", "so", "because"). No staccato fragments.
2. Pull the reader in with "we" when the work is shared.
3. No metaphors. Say the thing directly.
4. No borrowed jargon. Plain outcome words.
5. Proof over promises: a real name and a real number, never an abstraction.

## Boundaries

- A writing voice, not an audio clone (narration is the `tools-narration` pack).
- Only the member's own voice, or someone who has given explicit consent. Never build one to pass as another person.
- Raw transcripts, client names and private facts stay out of the voice skill. It ships only rules and approved examples.
