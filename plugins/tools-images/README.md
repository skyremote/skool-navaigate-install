# tools-images (AIOS 2.0, module 12: the shelf, tools)

Images and AI video on your own **Higgsfield** account. You install Higgsfield's CLI and Higgsfield's own skills
(product photoshoots, marketplace cards, characters, general generation). This pack gives your agent our method: a
brief first, video prompts written shot by shot, `tools-images check` before any credits are spent, and a manifest
that keeps every output's prompt and model.

- **Your account, your credits.** Higgsfield signs you in through the browser.
- **Plan before you pay.** The check catches gaps between shots, the wrong shot count for the length, and hype words.
- **Your likeness only.** No characters, faces or prompts of ours are included.

## Install

1. Install the start plugin `aios` first (module 1).
2. Higgsfield's CLI: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`,
   then `higgsfield auth login`.
3. Higgsfield's skills: `npx skills add higgsfield-ai/skills` (or in Claude Code: `/plugin marketplace add higgsfield-ai/skills`,
   then `/plugin install higgsfield@higgsfield`).

**Claude Code:** `/aios install tools-images` (or `/plugin install tools-images@navaigate-aios`), then `/reload-plugins`.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-images
./install.sh tools-images --check
```

## Use

```
tools-images doctor
tools-images sample ~/Images-practice
tools-images check ~/Images-practice/northwind-cake_video-prompt_v1.txt --seconds 10
tools-images log ~/Videos/northwind --prompt northwind-cake_video-prompt_v1.txt --model <model> --job <job id>
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-images/SKILL.md](skills/tools-images/SKILL.md).

## Licence

MIT. Higgsfield's CLI and skills are MIT, published by Higgsfield, and installed by you from their repositories.
Higgsfield is a paid service with its own terms.
