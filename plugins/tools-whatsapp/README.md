# tools-whatsapp (AIOS 2.0, module 12: the shelf, tools)

Your WhatsApp chats, searchable on your own Mac. You install the public **whatscribe** (MIT). It reads the WhatsApp
desktop app's local database (no QR code, no cloud API) and transcribes voice notes on your Mac. This pack gives your
agent our way of using the archive: find the messages, pull out every date, time and price, and quote the message
behind each one.

- **Local.** Chats and voice notes stay on your Mac.
- **Quoted.** `extract` lists each date, time and amount with the message, date and sender it came from.
- **Nothing sent.** Sending stays with whatscribe, which asks you to confirm every message.

## Install (macOS)

1. Install the start plugin `aios` first (module 1).
2. WhatsApp desktop, signed in.
3. `git clone https://github.com/GoodLadTom/whatscribe ~/whatscribe && cd ~/whatscribe && ./install.sh`, then
   `whatscribe setup` and `whatscribe permissions` (Full Disk Access).

**Claude Code:** `/aios install tools-whatsapp` (or `/plugin install tools-whatsapp@navaigate-aios`), then `/reload-plugins`.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-whatsapp
./install.sh tools-whatsapp --check
```

Needs Python 3.9 or later. On Windows, see `GoodLadTom/whatscribe-windows`; `find` and `extract` read the same file.

## Use

```
tools-whatsapp doctor
tools-whatsapp sample ~/WhatsApp-practice
tools-whatsapp extract ~/WhatsApp-practice/transcript.jsonl
whatscribe sync
tools-whatsapp find ~/Documents/whatscribe/<chat>/transcript.jsonl --since 2026-10-20 --type voice
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-whatsapp/SKILL.md](skills/tools-whatsapp/SKILL.md).

## Licence

MIT. whatscribe is MIT and installed by you from its own repository. WhatsApp is a Meta product with its own terms.
