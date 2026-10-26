"""Sandbox steps for tools-images, run by tests/tools-packs/sandbox_proof.py tools-images. No credits are spent."""


def run(r, home, work):
    practice = work / 'Images-practice'
    r.run(['tools-images', '--version'])
    r.run(['tools-images', 'doctor'], expect=2, note='The Higgsfield CLI is on this Mac, but the new member is not signed in and has not installed Higgsfield\'s skills.')
    r.run(['tools-images', 'sample', practice])
    r.run(['tools-images', 'check', practice / 'northwind-cake_video-prompt_v1.txt', '--seconds', '10'])
    bad = practice / 'northwind-cake_video-prompt_v2.txt'
    bad.write_text((practice / 'northwind-cake_video-prompt_v1.txt').read_text().replace('SHOT 3 (0:05', 'SHOT 3 (0:06')
                   .replace('morning light', 'stunning morning light'))
    r.run(['tools-images', 'check', bad, '--seconds', '10'], expect=1, note='A gap between shots and a hype word, caught before credits are spent.')
    r.run(['tools-images', 'log', work / 'Videos/northwind', '--prompt', practice / 'northwind-cake_video-prompt_v1.txt',
           '--model', 'example-model', '--note', 'sandbox: no generation was made'])
    r.run(['cat', work / 'Videos/northwind/manifest_v1.jsonl'])
