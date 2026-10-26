# 12 · The shelf: video
pack: shelf-video
cmd: shelf-video

## 12v.1 · Practise on a sample clip, up to the edit plan
what: Checks the tools, makes a 30-second practice clip, transcribes it on your computer, and shows the edit plan: which ums and pauses it would cut. It stops there, because you approve the plan.
check: The report shows the plan table with numbered CUT rows, and nothing is approved yet.
~~~
Set up the video pack from the shelf and practise on the sample clip. Stop at the plan: I approve it myself.

<<INSTALL>>

1. Check the tools: `ffmpeg -version | head -1`, `whisper --help | head -1` and `python3 -c "import PIL; print('Pillow', PIL.__version__)"`. If one is missing, install it (`brew install ffmpeg` on a Mac, and `python3 -m pip install --user Pillow openai-whisper`) and check again. Tell me first if a big download is needed.
2. Make the practice clip: `shelf-video sample --out 40_content/video/practice/sam_acme_v1.mp4`.
3. Start a project: `shelf-video init 40_content/video/practice/sam_acme_v1.mp4`. Show the size, frame rate and length.
4. Transcribe on this computer: `shelf-video transcribe --project 40_content/video/practice/sam_acme_v1_EDIT_v1`. The first run downloads the speech model (about 460 MB). Show the word and filler-word counts.
5. Make the plan: `shelf-video plan --project 40_content/video/practice/sam_acme_v1_EDIT_v1 --show`. Show me the numbered table.
6. Stop here. Do not approve the plan. Tell me that I approve it with prompt 12v.2, and that I can keep any row by adding its number to that prompt.

<<RULES>>

<<FINISH m12-video-plan>>
~~~

## 12v.2 · Approve the plan, render and verify the film
what: Records your approval of the edit plan, cuts the clip, burns in captions, exports the MP4 with a caption file, and checks the result.
check: `shelf-video verify` says PASS, `captions.srt` sits beside the MP4, and the report shows two still frames.
~~~
I have read the edit plan for my practice clip and I approve it.
Rows to keep instead of cutting (edit this line, or leave it empty): 

Approve it, render and verify. The plan must already exist in `40_content/video/practice/sam_acme_v1_EDIT_v1` (if not, stop and tell me to run prompt 12v.1 first).

<<INSTALL>>

1. Approve: `shelf-video approve --project 40_content/video/practice/sam_acme_v1_EDIT_v1 --yes`, adding `--drop <number>` for each row I listed above. Show the approval line.
2. Render: `shelf-video render --project 40_content/video/practice/sam_acme_v1_EDIT_v1`. Show the output path, the caption count and `burnt in: yes`.
3. Verify: `shelf-video verify --project 40_content/video/practice/sam_acme_v1_EDIT_v1`. It must say PASS.
4. Check that `captions.srt` sits beside the MP4.
5. In the report, show two still frames from `exports/edit_v1/checks/` by copying them next to the report and using relative image links. Never change or move the original clip.

<<RULES>>

<<FINISH m12-video-render>>
~~~
