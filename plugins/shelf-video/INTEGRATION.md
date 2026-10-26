# shelf-video: integration notes for the chief of staff

## Where the pack came from, and what it ships

| Source | Owner and licence | What this pack took |
|---|---|---|
| `cutroom-starter` (`skyremote/cutroom-starter`) | NavAIgate, MIT | The approach only: source SHA-256 fingerprint, frames snapped inwards, a member approval gate that an agent must not fake, new versions for every change. Code rewritten, attribution kept in `shelf_video/core.py` and the README. |
| `cutroom` engine (`skyremote/navaigate-team-plugins`, `plugins/navaigate-video`) | Daniel, private repo, no licence file (all rights reserved) | Ideas only: keep the original untouched, keep fillers in the source transcript, a verify step on the real file. No code, corpus, references or brand copied. |
| openai-whisper, whisper.cpp | OpenAI and Georgi Gerganov, MIT | Not bundled. Linked, with install commands. Called as CLIs. |
| FFmpeg | LGPL/GPL | Not bundled. Install command given. Called as a CLI. |
| Pillow | MIT-CMU | Not bundled. pip install command given. |

## Left out, and why

| Left out | Why |
|---|---|
| ElevenLabs Scribe transcription | Paid API with Daniel's key. Replaced with local Whisper. |
| The Shorts graphics engine, three-options-per-beat planning, GSAP/HyperFrames renders | Daniel's private production engine and house style. Not generic, and too heavy for a first pack. |
| The review room web app and its capability tokens | Replaced with a static `review_vN.html`, no server. |
| Premiere XML export and native project handoff | Needs Adobe Premiere; out of scope for a free member pack. |
| Pop-out matting, the macOS Vision helper | Private engine feature. |
| GIPHY discovery and research assets | Third-party API terms, and Daniel's private corpus. |
| ClickUp tracking and the cost ledger | Daniel's own operations. |
| The `corpus/` folder (worked examples, AIOS and Annual film projects, brand) | Daniel's private films, transcripts and brand. |
| NavMotion, Daniel's trained voice, nav-voiceover | Private by ruling of the programme brief. The pack never clones or generates a voice. |
| Vertical shorts (9:16 reframing) | Planned for a later version; it needs face tracking to do well. |

## Shared-file changes needed (I did not edit these)

1. **`.claude-plugin/marketplace.json`**: add the object in `plugins/shelf-video/MARKETPLACE_ENTRY.json` to `plugins`.
2. **`scripts/install_pack.py`**: apply `plugins/shelf-video/install_pack.diff` (`patch -p0 < plugins/shelf-video/install_pack.diff`
   from the repo root). It does three things, and covers `shelf-decks` and `shelf-invoices` too:
   - builds the pack list from `plugins/*/.claude-plugin/plugin.json` instead of the fixed `['aios','aios-brain']`;
   - makes every pack except `aios` require `aios` first (the brain's existing check, generalised);
   - links each file in a shelf pack's `bin/` into `~/.local/bin`, refusing to replace anything that is not ours.
   The sandbox proof runs with this diff applied, so `build-proof/shelf-video/sandbox_v1.md` (outside the repo) is the evidence it works.
3. **`README.md` and `ROADMAP.md`**: list `shelf-video` under module 12, with one line: "Edit a talking-head
   recording locally: Whisper transcript, fillers out, captions in."
4. **`plugins/aios/skills/aios/SKILL.md`**: line 12 of the path can name the shipped shelf packs:
   "12. The shelf — `shelf-video`, `shelf-decks`, `shelf-invoices` (more to come)."
5. **Tests in CI**: `python3 -m unittest discover -s tests/shelf-video` (30 tests, about 2 seconds; the end-to-end
   test needs FFmpeg and skips without it).

## Known limits

- Whisper sometimes drops a quiet "um". The skill tells the member to try a larger model or cut by hand.
- Word times from Whisper are close, not sample-exact. `pad` and the 12 ms audio fades at each join prevent clicks;
  the member can raise `pad` if a word is clipped.
- Captions are drawn with Pillow and composited with FFmpeg's `overlay`, because Homebrew's FFmpeg has no libass.
  This works on any FFmpeg build.

## Kept out of the repo (Daniel's ruling, 26 October 2026)

The repo holds the pack, its README and install steps, tests and evals. Course content and build evidence live
in the classroom folder on the NAS (local mirror `~/NAS_Local/150_Navbot_Classroom/aios-2/`), never in Git:

| Kept out | Where it lives |
|---|---|
| `lessons/` (lesson Markdown and paste-ready HTML) | `lessons_v2/12-shelf-video/` |
| `video/` (tutorial scripts, shot lists, SRTs, clips) | `tutorials_v2/12-shelf-video/`; films in the NavMotion project's `deliver/` |
| `plugins/*/proof/` (sandbox install proof, eval results) | `build-proof/shelf-video/` |

`tests/shelf-video/sandbox_proof.py` and `tests/shelf-video/eval_report.py` write there by default
(`AIOS2_PROOF_DIR` changes it).
