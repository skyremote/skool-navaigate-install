# Tutorial source material v2

Fifteen re-recorded, ordered raw terminal clips for later **3–10 minute tutorials**, landscape
1920 x 1080, made with /navmotion and narrated in Daniel's voice. Clarity and
repeatable steps are the goal. The finished tutorials and narration are a later
edit; these files are the software evidence and command sequence.

This revision implements the 16-finding code review and keeps the removal of the
40-second cap. All 15 clips were re-recorded against the corrected code. Each clip covers one step, types its full command, keeps its
output visible, and pauses to read it. Health and cross-harness inventory use a pager
and pauses on each page so no output is skipped. Installation includes the
marketplace prerequisite; the cross-harness brain install includes adding its
command to PATH.

Read `SHOTLIST_v2.md` for the clip-to-command map, one-sentence narration outline,
prerequisites, exact sandbox context and any interface shots that need mock-ups.
`clips/manifest_v2.json` records the actual files and measured durations.

The recordings use real Claude Code, real Codex, the real installer and brain
commands from a physical disposable source copy under `/tmp`, so producer-machine
paths never appear in a software listing. Cursor's configuration is shown as the actual sandbox file; its live
private app profile is not recorded. Screenshots in `screens/` are unaltered
frames of the real sandbox terminal. They are labelled precisely: a configuration
file or CLI inventory is not presented as an authenticated chat or a loaded skill.

All data is fictional, in HOME=/tmp/aios-member-sandbox. No accounts, tokens,
personal files or portraits are included. Menlo 28 px, Catppuccin Mocha, 40 px
padding, 30 fps and 85 ms typing are used throughout. Each output has a reading pause, and both paged checks hold every page. Their
page counts are calculated from the actual sandbox output before recording.

Run `video/render_v2.sh` from the checkout to recreate the sequence. It prepares a disposable physical source copy, moves
only the named synthetic sandbox aside into a dated /tmp folder and creates a
fresh one. It rebuilds each tape, then resolves the read command's actual ref
from the earlier search before that clip runs. The final tape contains the full
real ref, not a placeholder. All harness writes and recording caches stay in
the sandbox. Set-up hidden by VHS changes only the recording environment and
prompt; all commands taught to the member are visible in the clips.

`python3 video/check_clips_v2.py` requires the complete shot-list inventory,
1920 x 1080 and positive durations. There is no maximum raw clip duration.
Never use VHS publish: nothing from phase 1 is authorised for publication.
