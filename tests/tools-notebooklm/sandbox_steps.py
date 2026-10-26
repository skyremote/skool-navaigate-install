"""Sandbox steps for tools-notebooklm, run by tests/tools-packs/sandbox_proof.py tools-notebooklm. Nothing is uploaded."""


def run(r, home, work):
    practice = work / 'NotebookLM-practice'
    r.run(['tools-notebooklm', '--version'])
    r.run(['tools-notebooklm', 'doctor'], expect=2, note='The new member has not signed in to NotebookLM (the CLI may be on this Mac; the sign-in is per account).')
    r.run(['tools-notebooklm', 'sample', practice])
    r.run(['tools-notebooklm', 'plan', practice])
