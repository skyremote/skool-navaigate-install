# Prompts: shelf-transcripts

Paste one of these into Claude. Supadata is paid and metered, so these keep to one video or one short search.

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown.
Replace the sample names and figures with your own.

## Prompt 1: Pull the full words of one video

**You need:** Supadata key (SUPADATA_API_KEY) in ~/.claude/.env.

```text
Use the transcripts skill on https://www.youtube.com/watch?v=jNQXAC9IVRw . Pull the full transcript and save it exactly as it is to transcripts/zoo_transcript_v1.txt, with nothing cut off. Then tell me how many words it has and quote the first two sentences word for word.
```

## Prompt 2: Search first, then let me pick

**You need:** Supadata key in ~/.claude/.env.

```text
Use the transcripts skill. Search YouTube for "bakery loyalty card" and list the top 5 results with title, channel, views and length. Do not pull any transcript yet. I will tell you which one I want.
```

## Prompt 3: Pull a talk and extract what matters, with quotes

**You need:** Supadata key in ~/.claude/.env.

```text
Use the transcripts skill on https://www.youtube.com/watch?v=UF8uR6Z6KLc (a public talk). I am preparing a talk for Acme Studio. Pull the whole transcript, save it to transcripts/talk_v1.txt, check the file holds the whole talk and not a shortened version, then list the five main points the speaker makes. Give an exact quote for each point, word for word from the transcript, with no paraphrase in the quote marks.
```
