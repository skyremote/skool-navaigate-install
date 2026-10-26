"""Sandbox steps for tools-social, run by tests/tools-packs/sandbox_proof.py tools-social."""
import json
from datetime import datetime, timedelta


def run(r, home, work):
    practice = work / 'Social-practice'
    post = json.dumps({'tool_name': 'mcp__blotato__blotato_create_post', 'tool_input': {'text': 'x'}})
    r.run(['tools-social', '--version'])
    r.run(['tools-social', 'doctor'])
    r.run(['tools-social', 'sample', practice])
    r.run(['tools-social', 'check', practice / 'northwind_posts_v1.json'])
    r.run(['tools-social', 'gate'], stdin=post, note='No release on record: the gate denies the post.')
    r.run(['tools-social', 'release', 'now', '--words', 'I love it, go ahead'], expect=1, note='Approval is not a time.')
    day = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%dT09:00')
    r.run(['tools-social', 'release', 'schedule', '--words', 'Thursday at 9am London time', '--at', day, '--tz', 'Europe/London'])
    r.run(['tools-social', 'gate'], stdin=post, note='A time is on record, but this call would publish now: denied.')
    r.run(['tools-social', 'release', 'clear'])
    r.run(['claude', 'mcp', 'list'], note='Claude Code sees the plugin\'s Blotato server; with no key set it cannot connect yet.')
