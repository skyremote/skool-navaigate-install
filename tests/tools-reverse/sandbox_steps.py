"""Sandbox steps for tools-reverse, run by tests/tools-packs/sandbox_proof.py tools-reverse."""


def run(r, home, work):
    practice = work / 'Reverse-practice'
    r.run(['tools-reverse', '--version'])
    r.run(['tools-reverse', 'doctor'], expect=2, note='A new member has not run REA\'s setup yet.')
    r.run(['tools-reverse', 'sample', practice])
    r.run(['tools-reverse', 'check', practice / 'acme-calculator_investigation_v1.md'])
    r.run(['tools-reverse', 'new', practice / 'pricing_v1.md', '--target', "my site's price calculator",
           '--question', 'How is the price worked out?'])
    r.run(['tools-reverse', 'check', practice / 'pricing_v1.md'], expect=1, note='No analysis until the scope is filled in.')
    r.run(['npx', '-y', 'rea-agents@6.8.0', '--version'], timeout=300, note='REA itself, the public tool, fetched by npx (not set up for any agent here).')
