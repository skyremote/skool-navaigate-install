#!/usr/bin/env python3
"""Prove one library prompt for real: spawn a Claude Code thread in a demo bb, wait, collect evidence.

The demo bb is a separate bb server (its own data folder, ports and HOME), so nothing here
touches the operator's real bb. Point at it with --bb (a wrapper that sets BB_SERVER_URL).

Usage:
  prove_prompt.py --bb <bb wrapper> --project <proj id> --home <member HOME> --prompt 2.1 --out <evidence dir>
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent


def find_prompt(pid):
    data = json.loads((KIT / "plugin" / "prompts.json").read_text())
    for mod in data["modules"]:
        for p in mod["prompts"]:
            if p["id"] == pid:
                return mod, p
    raise SystemExit("No prompt " + pid)


def bb(wrapper, *args, check=True):
    r = subprocess.run([wrapper, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit("bb %s failed: %s %s" % (" ".join(args), r.stdout[-800:], r.stderr[-800:]))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bb", required=True)
    ap.add_argument("--project", required=True)
    ap.add_argument("--home", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", default="45m")
    ap.add_argument("--model", default="")
    a = ap.parse_args()
    mod, p = find_prompt(a.prompt)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "prompt.txt").write_text(p["body"] + "\n")
    folder = Path(a.home) / "AIOS"
    before = sorted(str(x.relative_to(folder)) for x in folder.rglob("*") if ".git/" not in str(x))
    args = ["thread", "spawn", "--project", a.project, "--provider", "claude-code",
            "--title", "aios-demo %s · %s" % (p["id"], p["title"]), "--prompt-file", str(out / "prompt.txt"), "--json"]
    if a.model:
        args += ["--model", a.model]
    started = time.time()
    t = json.loads(bb(a.bb, *args).stdout)
    tid = t["id"]
    (out / "thread_id.txt").write_text(tid + "\n")
    w = bb(a.bb, "thread", "wait", tid, "--timeout", a.timeout, check=False)
    secs = int(time.time() - started)
    show = bb(a.bb, "thread", "show", tid, "--json", check=False).stdout
    (out / "thread_show.json").write_text(show)
    log = bb(a.bb, "thread", "log", tid, "--all", "--format", "verbose", check=False).stdout
    (out / "transcript.md").write_text(log)
    final = bb(a.bb, "thread", "output", tid, check=False).stdout
    (out / "final_output.md").write_text(final)
    after = sorted(str(x.relative_to(folder)) for x in folder.rglob("*") if ".git/" not in str(x))
    new = [x for x in after if x not in before]
    (out / "files_created.txt").write_text("\n".join(new) + "\n")
    reports = sorted(folder.glob("80_aios/reports/*.html"))
    for r in reports:
        (out / r.name).write_bytes(r.read_bytes())
    try:
        status = json.loads(show).get("status")
    except Exception:
        status = "unknown"
    summary = {
        "prompt": p["id"], "title": p["title"], "module": mod["slug"], "thread": tid, "status": status,
        "wait_exit": w.returncode, "seconds": secs, "files_created": len(new),
        "reports": [r.name for r in reports],
        "inline_vis_in_reply": "::inline-vis" in final,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary))
    return 0 if w.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
