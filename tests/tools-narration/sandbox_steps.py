"""Sandbox steps for tools-narration, run by tests/tools-packs/sandbox_proof.py tools-narration."""


def run(r, home, work):
    practice = work / 'Narration-practice'
    r.run(['tools-narration', '--version'])
    r.run(['tools-narration', 'doctor'], expect=2, note='ffmpeg is found; a new member has no key or voice yet.')
    r.run(['tools-narration', 'voices'], expect=2, note='Reading voices refuses without the member\'s own key, and says how to add it.')
    r.run(['tools-narration', 'sample', practice])
    r.run(['tools-narration', 'plan', practice / 'slides.json', '--out', practice / 'script_v1.txt'])
    r.run(['cat', practice / 'script_v1.txt'])
    r.run(['tools-narration', 'narrate', practice / 'slides.json', '--out', practice / 'narration_v1'], expect=1,
          note='A paid take waits for the member\'s --yes.')
    r.run(['tools-narration', 'split', '--slides', practice / 'slides.json', '--take', practice / 'take.mp3',
           '--alignment', practice / 'alignment.json', '--out', practice / 'clips_v1'])
    r.run(['cat', practice / 'clips_v1/manifest_v1.json'])
    r.run(['tools-narration', 'clone', 'My voice', practice / 'take.mp3'], expect=1, note='Cloning needs --consent.')
