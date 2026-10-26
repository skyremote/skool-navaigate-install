#!/usr/bin/env python3
"""Write fictional sessions only. No reads from the host's real harness folders."""
import json
from pathlib import Path


def write(home):
    home = Path(home)
    stamp = '2026-10-26T10:00:00Z'
    sessions = {
      '.claude/projects/fictional/fictional-claude.jsonl':[
        {'type':'user','sessionId':'fictional-claude','timestamp':stamp,'message':{'role':'user','content':'<system-reminder>harness-only-needle</system-reminder> Plan the Lighthouse launch.'}},
        {'type':'assistant','sessionId':'fictional-claude','timestamp':stamp,'message':{'role':'assistant','content':[{'type':'text','text':'The fictional Lighthouse launch budget is 2400 pounds. Use the blue invitation.'},{'type':'tool_use','name':'ignored','input':{'text':'tool-only-needle'}}]}}],
      '.codex/sessions/2026/10/26/fictional-codex.jsonl':[
        {'type':'session_meta','payload':{'id':'fictional-codex'}},
        {'type':'response_item','timestamp':stamp,'payload':{'type':'message','role':'user','content':[{'type':'input_text','text':'For the fictional Orchard order, use recyclable boxes.'}]}},
        {'type':'response_item','timestamp':stamp,'payload':{'type':'message','role':'assistant','content':[{'type':'output_text','text':'Orchard packaging is recyclable cardboard. Delivery is Friday.'}]}}],
      '.cursor/projects/fictional/agent-transcripts/fictional-cursor.jsonl':[
        {'role':'user','timestamp':stamp,'message':{'content':'<timestamp>Monday</timestamp><user_query>Which colour for the fictional Juniper page?</user_query>'}},
        {'role':'assistant','timestamp':stamp,'message':{'content':'Juniper uses a navy heading and a cream background.'}}]
    }
    for relative,events in sessions.items():
        path = home/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(''.join(json.dumps(e)+'\n' for e in events))
    return len(sessions)


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--home',required=True)
    args = parser.parse_args()
    target = Path(args.home).resolve()
    if not str(target).startswith(('/tmp/','/private/tmp/')):
        parser.error('Fixtures require a /tmp sandbox HOME')
    print('Wrote '+str(write(target))+' fictional session files.')
