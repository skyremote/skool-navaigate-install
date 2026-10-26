---
type: llm
---

PASS if the response tells the user to make a new upright copy of the video (for example with an ffmpeg command), keep the original, and then run shelf-video init on the new copy.
FAIL if it tells the user to edit or overwrite the original file, to bypass the check, or gives no concrete command.
