"""Sandbox steps for tools-meetings, run by tests/tools-packs/sandbox_proof.py tools-meetings."""
import json


def run(r, home, work):
    practice = work / 'Meetings-practice'
    r.run(['tools-meetings', '--version'])
    r.run(['tools-meetings', 'doctor'], expect=2, note='A new member has no Granola key yet, so doctor says how to add one.')
    r.run(['tools-meetings', 'list', '5'], expect=2, note='Reading Granola refuses without a key, and says why.')
    r.run(['tools-meetings', 'sample', practice])
    transcript = practice / 'northwind-kickoff_transcript_v1.txt'
    blank = practice / 'northwind-kickoff_record_v1.md'
    r.run(['tools-meetings', 'check', blank, '--source', transcript], expect=1, note='The empty record fails on purpose.')
    filled = practice / 'northwind-kickoff_record_v2.md'
    filled.write_text("""# Decision record: Northwind Bakery kick-off (practice)

Meeting: Northwind Bakery: booking page kick-off (practice), 2026-10-20 10:00. Source: northwind-kickoff_transcript_v1.txt.

## Decisions
- The first version takes online orders for celebration cakes only. (quote: "cakes only for now")
- Prices stay the same as the shop this year. (quote: "the price list stays the same as the shop")

## Actions
- Send the page layout | Owner: Me | Due: Friday 31 October | Quote: "I will send the page layout by Friday 31 October"
- Send photos of the six best-selling cakes | Owner: Tom | Due: not stated | Quote: "Tom will send you the photos of the six cakes we sell most"
- Build the page after sign-off | Owner: Sam | Due: not stated | Quote: "Sam from my team builds it once you have signed the layout off"

## Open questions
- Whether a 20 percent deposit is fine for VAT: Northwind asks their accountant.

## Source
northwind-kickoff_transcript_v1.txt
""")
    r.run(['cat', filled], note='The record an agent writes from the transcript, following the skill.')
    r.run(['tools-meetings', 'check', filled, '--source', transcript])
    wrong = practice / 'northwind-kickoff_record_v3.md'
    wrong.write_text(filled.read_text().replace('Owner: Tom', 'Owner: Jordan').replace('20 percent', '25 percent'))
    r.run(['tools-meetings', 'check', wrong, '--source', transcript], expect=1,
          note='An invented owner and an invented number both fail.')
    requests = '\n'.join(json.dumps(x) for x in [
        {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18'}},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
        {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'meetings_list', 'arguments': {}}}]) + '\n'
    r.run(['tools-meetings', 'mcp'], stdin=requests, note='The MCP server Claude Code starts: it lists two tools and, with no key, says what is missing.')
    r.run(['grep', '-A3', 'tools-meetings', home / '.codex/config.toml'], note='The installer added the MCP server to Codex.')
    r.run(['cat', home / '.cursor/mcp.json'])
