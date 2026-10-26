"""Sandbox steps for tools-research, run by tests/tools-packs/sandbox_proof.py tools-research."""


def run(r, home, work):
    practice = work / 'Research-practice'
    r.run(['tools-research', '--version'])
    r.run(['tools-research', 'doctor'], expect=2, note='Papers and Substack are ready; Reddit waits for the member\'s own app.')
    r.run(['tools-research', 'papers', 'online ordering small restaurants', '--n', '3'], note='Live: OpenAlex, no key.')
    r.run(['tools-research', 'substack', 'archive', 'www.lennysnewsletter.com', '--n', '3'], note='Live: Substack, no key.')
    r.run(['tools-research', 'reddit', 'search', 'ai receptionist'], expect=2, note='Reddit refuses without the member\'s app and says how to make one.')
    r.run(['tools-research', 'sample', practice])
    r.run(['tools-research', 'check', practice / 'bakery-ordering_ledger_practice_v1.md'])
    r.run(['tools-research', 'new', practice / 'question_v1.md', '--question', 'Do AI receptionists work for small clinics?'])
    r.run(['tools-research', 'check', practice / 'question_v1.md'], expect=1, note='An empty ledger fails.')
