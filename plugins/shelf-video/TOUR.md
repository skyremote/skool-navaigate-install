# Tour: module 12, the shelf: video

`/aios learn 12 video` follows these steps in the member's own folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never change or move the member's original recording. If a check fails, stop, fix that one thing, and check again.

## Step 1: Find the command
- **Do:** check that the pack's command runs.
- **Command:** `shelf-video --version` (Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/shelf-video" --version`).
- **They should see:** `shelf-video 2.0.0`.
- **Check:** exit code 0. If the command is missing, run `export PATH="$HOME/.local/bin:$PATH"` (Codex and Cursor),
  or restart Claude Code after `/plugin install shelf-video@navaigate-aios`.

## Step 2: Check the three tools
- **Do:** confirm FFmpeg, Whisper and Pillow are installed.
- **Command:** `ffmpeg -version | head -1 && whisper --help | head -1 && python3 -c "import PIL; print('Pillow', PIL.__version__)"`
- **They should see:** an FFmpeg version line, a Whisper usage line and a Pillow version.
- **Check:** if one fails, install it: `brew install ffmpeg` (Linux: `sudo apt install ffmpeg`) and
  `python3 -m pip install --user Pillow openai-whisper`. Run the command again.

## Step 3: Make a practice clip
- **Do:** make the 30-second sample, so the first run is not on their own face.
- **Command:** `shelf-video sample --out ~/Videos/practice/sam_acme_v1.mp4`
- **They should see:** `Sample recording: .../sam_acme_v1.mp4`.
- **Check:** they can play it. A drawn presenter, Sam from Acme Studio, says "um" and "uh" and pauses.

## Step 4: Start a project
- **Do:** make the project folder beside the clip.
- **Command:** `shelf-video init ~/Videos/practice/sam_acme_v1.mp4`
- **They should see:** `Project: .../sam_acme_v1_EDIT_v1`, then the size, frame rate and length.
- **Check:** `ls ~/Videos/practice` shows the clip and the new `_EDIT_v1` folder. The clip is unchanged.

## Step 5: Transcribe
- **Do:** run Whisper on this machine. Say first that the model download is about 460 MB, once.
- **Command:** `shelf-video transcribe --project ~/Videos/practice/sam_acme_v1_EDIT_v1`
- **They should see:** `Wrote .../words_v1.json`, then a count of words and filler words.
- **Check:** `cat ~/Videos/practice/sam_acme_v1_EDIT_v1/transcript/words_v1.txt` reads like what Sam said, ums included.

## Step 6: Read the plan
- **Do:** make the plan and read the table together.
- **Command:** `shelf-video plan --project ~/Videos/practice/sam_acme_v1_EDIT_v1 --show`
- **They should see:** numbered rows. CUT rows are selected. "keep (proposed)" rows are suggestions.
- **Check:** they open `plans/review_v1.html` in a browser and press "Hear it" on two rows.

## Step 7: The member approves
- **Do:** ask which numbers to keep in the film. Wait for their answer. Never approve for them.
- **Command:** `shelf-video approve --project ~/Videos/practice/sam_acme_v1_EDIT_v1 --yes` (add `--drop 3` to keep proposal 3)
- **They should see:** `Approved plan_v1.json: N removals, X s out, new length Y s.`
- **Check:** `ls ~/Videos/practice/sam_acme_v1_EDIT_v1/approvals` shows `approval_v1.json`.

## Step 8: Render
- **Do:** cut, caption and export.
- **Command:** `shelf-video render --project ~/Videos/practice/sam_acme_v1_EDIT_v1`
- **They should see:** `Rendered .../exports/edit_v1/edited.mp4`, the caption count and `burnt in: yes`.
- **Check:** `captions.srt` sits beside the MP4.

## Step 9: Verify, then watch it
- **Do:** check the real file, then watch it once.
- **Command:** `shelf-video verify --project ~/Videos/practice/sam_acme_v1_EDIT_v1`
- **They should see:** `PASS` and a duration that matches the plan's new length.
- **Check:** they open two stills in `exports/edit_v1/checks/` and play the film. Captions sit above the bottom
  edge and no word is clipped at a join.

## Step 10: Their own settings and recording
- **Do:** set their caption font and colour, then run steps 4 to 9 on one of their own recordings.
- **Command:** `shelf-video settings set caption.colour=#FFD400` and `shelf-video settings set caption.font=<path to a .ttf>`
- **They should see:** the settings printed, with the file path `~/.config/aios/shelf-video.json`.
- **Check:** their own film passes verify, and they approved its plan themselves.

## Recap
Sample, init, transcribe, plan, approve (theirs), render, verify. Every change makes a new `_vN`, and the original
never changes.
