# Prompts: tools-images

Paste one into Claude Code, Codex or Cursor.

## 1. Learn the video prompt shape (free)

```text
Use tools-images. Make the practice video prompt in ~/Images-practice, check it for 10 seconds, then explain the four sections to me in plain English.
```

**What it does:** writes a fictional 10-second bakery video prompt and checks it, without spending credits.
**How you know it worked:** the check prints `PASS`, and you can say what each of the four sections is for.

## 2. Product photos from your own photo

```text
Use tools-images. Make four product photos of this mug on a kitchen counter in morning light, using my photo as the reference, and save the best two. Tell me the cost before you start: <attach photo>
```

**What it does:** uses Higgsfield's product photoshoot skill on your photo, after telling you the cost.
**How you know it worked:** four images in a new `_v1` folder, two picked, and a `manifest_v1.jsonl` with the prompt
and model for each.

## 3. A short product video, planned first

```text
Use tools-images. Write a 15-second shot-by-shot prompt for a calm reveal of my booking app on a phone, check it, show me, and only generate after I say go.
```

**What it does:** writes the four-section prompt, checks it, waits for you, then generates and logs it.
**How you know it worked:** the check says `PASS` before anything is generated, and the video's folder has a manifest
entry with the same prompt file.
