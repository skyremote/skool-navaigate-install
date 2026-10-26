#!/usr/bin/env python3
"""Scrub eval JSON of local paths and write proof/eval_v1.md. Usage: eval_report.py <pack> <full.json> [<rerun.json> <case>] [--note FILE]"""
import json
import os
import re
import sys
from pathlib import Path



def scrub(obj):
    text = json.dumps(obj)
    text = re.sub(r'/Users/[A-Za-z0-9_.-]+[^"\s\\]*', '<local-path>', text)
    text = re.sub(r'/private/tmp/e-[A-Za-z0-9]+', '<eval-sandbox>', text)
    return json.loads(text)


def main(argv):
    pack, full_path = argv[0], argv[1]
    rerun_path, rerun_case = (argv[2], argv[3]) if len(argv) > 3 and not argv[2].startswith('--') else (None, None)
    note = ''
    if '--note' in argv:
        note = Path(argv[argv.index('--note') + 1]).read_text()
    proof = Path(os.environ.get('AIOS2_PROOF_DIR') or Path.home() / 'NAS_Local/150_Navbot_Classroom/aios-2/build-proof') / pack
    proof.mkdir(parents=True, exist_ok=True)
    full = json.load(open(full_path))
    (proof / 'eval_v1.json').write_text(json.dumps(scrub(full), indent=1) + '\n')
    scores = {c['name']: c['aggregates'] for c in full['cases']}
    first = {}
    if rerun_path:
        rerun = json.load(open(rerun_path))
        (proof / ('eval_v1_' + rerun_case + '-rerun.json')).write_text(json.dumps(scrub(rerun), indent=1) + '\n')
        first[rerun_case] = scores[rerun_case]['score']
        scores[rerun_case] = rerun['cases'][0]['aggregates']
    rows = []
    for name, a in scores.items():
        extra = ' (first run: %s)' % first[name] if name in first else ''
        rows.append('| %s | %s%s | %s | %s |' % (name, a['score'], extra, a['scoreWithout'], a['delta']))
    mean_with = sum(a['score'] for a in scores.values()) / len(scores)
    mean_without = sum(a['scoreWithout'] for a in scores.values()) / len(scores)
    md = ['# %s eval results (v1, 26 October 2026)' % pack, '',
          'Command, from the repo root so the `aios` dependency resolves:',
          '`claude plugin eval plugins --eval-dir %s/evals --runs 1 --no-publish --trust-plugin`' % pack, '',
          'One run per case, with a no-plugin baseline arm. Score is the share of scored graders that pass. The',
          '`skill-fired` grader is an indicator and is not part of the score.', '',
          '| Case | With the pack | Without | Change |', '|---|---|---|---|'] + rows + [
          '', 'Mean with the pack: %.2f. Mean without: %.2f.' % (mean_with, mean_without), '']
    if note:
        md += ['## Notes', '', note.strip(), '']
    (proof / 'eval_v1.md').write_text('\n'.join(md))
    print('\n'.join(md))


if __name__ == '__main__':
    main(sys.argv[1:])
