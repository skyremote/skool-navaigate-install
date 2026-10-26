"""Sandbox steps for tools-boards, run by tests/tools-packs/sandbox_proof.py tools-boards."""


def run(r, home, work):
    practice = work / 'Boards-practice'
    r.run(['tools-boards', '--version'])
    r.run(['tools-boards', 'sample', practice])
    r.run(['tools-boards', 'validate', practice / 'northwind-workshop_scene_v1.json', '--payload',
           practice / 'northwind-workshop.mcp.json', '--strict'])
    r.run(['head', '-20', practice / 'northwind-workshop.mcp.json'])
    r.run(['tools-boards', 'validate', practice / 'release-workflow_scene_example.json', '--strict'])
    bad = practice / 'too-small_v1.json'
    bad.write_text('{"nodes": [{"id": "a", "label": "A", "x": 0, "y": 0, "width": 200, "height": 50}]}')
    r.run(['tools-boards', 'validate', bad], expect=1, note='A card under the minimum height is refused before anything is written.')
    r.run(['claude', 'mcp', 'list'], note='Claude Code sees the plugin\'s BluPlai server; it signs in on first use.')
