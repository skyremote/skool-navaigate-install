"""Sandbox steps for tools-memory, run by tests/tools-packs/sandbox_proof.py tools-memory."""


def run(r, home, work):
    practice = work / 'Memory-practice'
    r.run(['tools-memory', '--version'])
    r.run(['tools-memory', 'doctor'], expect=2, note='A new member has not cloned db-sync yet; the Turso CLI and Paste are tools on this Mac.')
    r.run(['git', 'clone', '--depth', '1', 'https://github.com/skyremote/db-sync', home / '.claude/skills/db-sync'],
          note='The public db-sync skill, installed the way the README says.')
    r.run(['tools-memory', 'sample', practice])
    r.run(['tools-memory', 'check', practice / 'acme-orders_v1.db'], expect=1)
    r.run(['tools-memory', 'check', practice / 'acme-orders_v2.db'])
    r.run(['tools-memory', 'doctor'], note='db-sync is found now.')
