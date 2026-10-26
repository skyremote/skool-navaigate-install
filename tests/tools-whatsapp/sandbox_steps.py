"""Sandbox steps for tools-whatsapp, run by tests/tools-packs/sandbox_proof.py tools-whatsapp. No real chat is read."""


def run(r, home, work):
    practice = work / 'WhatsApp-practice'
    r.run(['tools-whatsapp', '--version'])
    r.run(['tools-whatsapp', 'doctor'], expect=None, note='whatscribe and WhatsApp are tools on this Mac; the result depends on what is installed here.')
    r.run(['tools-whatsapp', 'sample', practice])
    r.run(['tools-whatsapp', 'extract', practice / 'transcript.jsonl'])
    r.run(['tools-whatsapp', 'find', practice / 'transcript.jsonl', '--type', 'voice'])
    r.run(['tools-whatsapp', 'find', practice / 'transcript.jsonl', '--since', '2026-10-21', '--contains', 'invoice'])
