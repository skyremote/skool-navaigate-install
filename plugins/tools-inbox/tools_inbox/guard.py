"""PreToolUse hook: block every MCP tool that would send, forward or reply to email. Drafts stay allowed."""
import json
import re
import sys

SENDING = re.compile(r'(SEND|FORWARD|REPLY_TO|REPLY|SCHEDULE_SEND|DISPATCH)', re.I)
DRAFTS = re.compile(r'DRAFT', re.I)
MAIL = re.compile(r'(GMAIL|OUTLOOK|MAIL|EMAIL)', re.I)


def decide(tool_name):
    """Return a deny reason for a sending tool, or None to let the call through."""
    if not tool_name.startswith('mcp__'):
        return None
    action = tool_name.split('__', 2)[-1]
    if not MAIL.search(tool_name):
        return None
    if SENDING.search(action) and not (DRAFTS.search(action) and not re.search(r'SEND_DRAFT|SEND', action, re.I)):
        return ('tools-inbox never sends email. Make a draft instead (a CREATE_EMAIL_DRAFT tool), show it, and let the '
                'member send it from their own inbox. To send from agents on purpose, disable the tools-inbox plugin.')
    return None


def main(stdin=sys.stdin, stdout=sys.stdout):
    try:
        event = json.load(stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    reason = decide(str(event.get('tool_name', '')))
    if reason:
        stdout.write(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny',
                                                        'permissionDecisionReason': reason}}) + '\n')
    return 0
