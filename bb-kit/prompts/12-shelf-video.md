# Module 12 · The shelf: video: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 12v.1 · Practise on a sample clip, up to the edit plan

**What it does:** Checks the tools, makes a 30-second practice clip, transcribes it on your computer, and shows the edit plan: which ums and pauses it would cut. It stops there, because you approve the plan.

**How you know it worked:** The report shows the plan table with numbered CUT rows, and nothing is approved yet.

~~~text
Set up the video pack from the shelf and practise on the sample clip. Stop at the plan: I approve it myself.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install shelf-video@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/shelf-video/*/bin | tail -1)/shelf-video"`. Below, `shelf-video` means that full path.

1. Check the tools: `ffmpeg -version | head -1`, `whisper --help | head -1` and `python3 -c "import PIL; print('Pillow', PIL.__version__)"`. If one is missing, install it (`brew install ffmpeg` on a Mac, and `python3 -m pip install --user Pillow openai-whisper`) and check again. Tell me first if a big download is needed.
2. Make the practice clip: `shelf-video sample --out 40_content/video/practice/sam_acme_v1.mp4`.
3. Start a project: `shelf-video init 40_content/video/practice/sam_acme_v1.mp4`. Show the size, frame rate and length.
4. Transcribe on this computer: `shelf-video transcribe --project 40_content/video/practice/sam_acme_v1_EDIT_v1`. The first run downloads the speech model (about 460 MB). Show the word and filler-word counts.
5. Make the plan: `shelf-video plan --project 40_content/video/practice/sam_acme_v1_EDIT_v1 --show`. Show me the numbered table.
6. Stop here. Do not approve the plan. Tell me that I approve it with prompt 12v.2, and that I can keep any row by adding its number to that prompt.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m12-video-plan_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m12-video-plan_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 12v.2 · Approve the plan, render and verify the film

**What it does:** Records your approval of the edit plan, cuts the clip, burns in captions, exports the MP4 with a caption file, and checks the result.

**How you know it worked:** `shelf-video verify` says PASS, `captions.srt` sits beside the MP4, and the report shows two still frames.

~~~text
I have read the edit plan for my practice clip and I approve it.
Rows to keep instead of cutting (edit this line, or leave it empty): 

Approve it, render and verify. The plan must already exist in `40_content/video/practice/sam_acme_v1_EDIT_v1` (if not, stop and tell me to run prompt 12v.1 first).

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install shelf-video@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/shelf-video/*/bin | tail -1)/shelf-video"`. Below, `shelf-video` means that full path.

1. Approve: `shelf-video approve --project 40_content/video/practice/sam_acme_v1_EDIT_v1 --yes`, adding `--drop <number>` for each row I listed above. Show the approval line.
2. Render: `shelf-video render --project 40_content/video/practice/sam_acme_v1_EDIT_v1`. Show the output path, the caption count and `burnt in: yes`.
3. Verify: `shelf-video verify --project 40_content/video/practice/sam_acme_v1_EDIT_v1`. It must say PASS.
4. Check that `captions.srt` sits beside the MP4.
5. In the report, show two still frames from `exports/edit_v1/checks/` by copying them next to the report and using relative image links. Never change or move the original clip.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m12-video-render_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m12-video-render_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
