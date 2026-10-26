"""Sandbox steps for tools-tasks, run by tests/tools-packs/sandbox_proof.py tools-tasks."""


def run(r, home, work):
    practice = work / 'Tasks-practice'
    r.run(['tools-tasks', '--version'])
    r.run(['tools-tasks', 'sample', practice])
    r.run(['tools-tasks', 'check', practice / 'northwind_tasks_v1.md'])
    bad = practice / 'loose_tasks_v1.md'
    bad.write_text('## Tasks\n- Look into pricing | Owner: Sam\n')
    r.run(['tools-tasks', 'check', bad], expect=1, note='A vague task with no date and no "done when" is refused.')
    r.run(['tools-tasks', 'today', practice / 'open-tasks_v1.json', '--on', '2026-10-26'])
    r.run(['claude', 'mcp', 'list'], note='Claude Code sees ClickUp\'s official server from the plugin; it signs in with /mcp on first use.')
