# tools-meetings (AIOS 2.0, module 12: the shelf, tools)

Your meetings, turned into decisions and owners the same day. You record calls in **Granola** on your own account.
This pack reads the transcripts with your own key and gives your agent our method: a decision record where every
owner, number and quote is checked against what was actually said.

- **Your account, your key.** Granola is a public app (granola.ai). The API needs a Business or Enterprise plan.
- **Read-only.** The pack never edits or deletes a note.
- **Checked.** `tools-meetings check` fails a record that invents an owner, a number or a quote.
- **Practice first.** A fictional call (Northwind Bakery and Acme Studio) works with no account at all.

## Install

1. Install the start plugin `aios` first (module 1).
2. Install Granola from granola.ai and sign in. Record one real call.
3. Create your API key in the Granola app: Settings, Connectors, API keys. It starts `grn_`.

**Claude Code:** type `/aios install tools-meetings` (it runs `aios-guide --harness claude install tools-meetings`),
then `/reload-plugins`. Or install it directly:
```
/plugin install tools-meetings@navaigate-aios
```
Then open `/plugin`, choose tools-meetings, Configure, and paste the key as "Granola API key". It is kept in your
system keychain.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-meetings
./install.sh tools-meetings --check
```
Then put the key in your shell profile (`export GRANOLA_API_KEY=grn_...`) or as one line,
`GRANOLA_API_KEY=grn_...`, in `~/.config/aios-tools/env`, then `chmod 600 ~/.config/aios-tools/env`.
The installer also adds the `tools-meetings` MCP server to Codex and Cursor.

Needs Python 3.9 or later. No other installs.

## Use

```
tools-meetings doctor
tools-meetings sample ~/Meetings-practice
tools-meetings search "Northwind"
tools-meetings transcript <id> --me "Sam" --out ~/Meetings/northwind_transcript_v1.txt
tools-meetings new ~/Meetings/northwind_record_v1.md --title "Northwind kick-off" --source northwind_transcript_v1.txt
tools-meetings check ~/Meetings/northwind_record_v1.md --source ~/Meetings/northwind_transcript_v1.txt
```

Three starter prompts: [prompts.md](prompts.md). The full method: [skills/tools-meetings/SKILL.md](skills/tools-meetings/SKILL.md).

## Licence

MIT. Granola is a third-party product with its own terms; this pack only calls its public API with your key.
