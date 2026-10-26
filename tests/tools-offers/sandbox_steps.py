"""Sandbox steps for tools-offers, run by tests/tools-packs/sandbox_proof.py tools-offers."""


def run(r, home, work):
    corpus = work / 'Hormozi-corpus'
    r.run(['tools-offers', '--version'])
    r.run(['tools-offers', 'doctor'], expect=2, note='A new member has not installed the public engine yet.')
    r.run(['git', 'clone', '--depth', '1', 'https://github.com/skyremote/hormozi-growth-engine', home / 'hormozi-growth-engine'],
          note='The public engine, installed the way the README says.')
    r.run(['bash', home / 'hormozi-growth-engine/install.sh', 'claude'])
    r.run(['tools-offers', 'doctor'])
    r.run(['tools-offers', 'corpus', 'init', corpus])
    (corpus / 'offers/corpus/ch01-practice.md').write_text('# Practice chapter (the member writes their own)\n'
                                                         'My own notes on the value equation [p.000].\n')
    r.run(['tools-offers', 'corpus', 'check', corpus], note='One practice chapter with a page marker.')
    r.run(['tools-offers', 'corpus', 'point', corpus], expect=1, note='A dry run first: it lists the files.')
    r.run(['tools-offers', 'corpus', 'point', corpus, '--yes'])
    r.run(['tools-offers', 'doctor'])
