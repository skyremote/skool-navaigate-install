"""Sandbox steps for tools-voice, run by tests/tools-packs/sandbox_proof.py tools-voice."""


def run(r, home, work):
    practice = work / 'Voice-practice'
    r.run(['tools-voice', '--version'])
    r.run(['tools-voice', 'doctor'], expect=2, note='A new member has not installed voice-skill-builder yet.')
    r.run(['git', 'clone', '--depth', '1', 'https://github.com/skyremote/voice-skill-builder',
           home / '.claude/skills/voice-skill-builder'], note='The public tool, installed the way the README says.')
    r.run(['tools-voice', 'doctor'])
    r.run(['tools-voice', 'sample', practice])
    r.run(['tools-voice', 'check', practice / 'draft-bad_v1.md'], expect=1)
    r.run(['tools-voice', 'check', practice / 'draft-good_v1.md'])
    r.run(['tools-voice', 'new', 'Sam'])
    r.run(['ls', home / '.claude/skills/sam-voice'])
    r.run(['tools-voice', 'evidence', practice / 'sam-call_transcript_v1.txt', '--speaker', 'Sam', '--out', work / 'Private/VOICE_EVIDENCE.md'])
    r.run(['head', '-30', work / 'Private/VOICE_EVIDENCE.md'])
    r.run(['tools-voice', 'calibrate', '--profile', home / '.claude/skills/sam-voice/PROFILE.md', '--before', 'Not a big job.',
           '--after', "there's nothing like a big job", '--lesson', 'Soften the negation and chain it.'])
    r.run(['tail', '-6', home / '.claude/skills/sam-voice/PROFILE.md'])
