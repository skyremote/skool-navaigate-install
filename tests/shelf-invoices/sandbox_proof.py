#!/usr/bin/env python3
"""Sandbox proof for shelf-invoices: install the pack as a new member and record every step. Not shipped.

  python3 tests/shelf-invoices/sandbox_proof.py prep                 copy this checkout, add the marketplace entry
  python3 tests/shelf-invoices/sandbox_proof.py install              member install steps -> sandbox_<v>.md
  python3 tests/shelf-invoices/sandbox_proof.py prompt N "<title>"   run prompt N from prompts.md headless -> prompts_<v>.md
  python3 tests/shelf-invoices/sandbox_proof.py sh "<title>" -- cmd  run one command as the member -> prompts_<v>.md

Settings (environment): SANDBOX_HOME (default /tmp/aios2-sandbox-shelf-invoices), SANDBOX_CHECKOUT
(default /tmp/shelf-invoices-v2/checkout), PROOF_DIR (where the .md records go, default ./proof-out),
PROOF_VERSION (default v1). The member's model access is inherited from the caller's environment; every
ANTHROPIC_* value and the real home folder are scrubbed from the records.
"""
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOME = Path(os.environ.get("SANDBOX_HOME", "/tmp/aios2-sandbox-shelf-invoices"))
CHECKOUT = Path(os.environ.get("SANDBOX_CHECKOUT", "/tmp/shelf-invoices-v2/checkout"))
PROOF = Path(os.environ.get("PROOF_DIR", "proof-out"))
VERSION = os.environ.get("PROOF_VERSION", "v1")
REAL_HOME = str(Path.home())


def environment():
    env = dict(os.environ, HOME=str(HOME), CLAUDE_CONFIG_DIR=str(HOME / ".claude"), CODEX_HOME=str(HOME / ".codex"),
               XDG_CONFIG_HOME=str(HOME / ".config"), XDG_DATA_HOME=str(HOME / ".local/share"),
               XDG_CACHE_HOME=str(HOME / ".cache"))
    for key in list(env):
        if key.startswith(("CLAUDE_CODE_", "CLAUDE_PLUGIN_", "CLAUDE_AGENT_")) or key in (
                "CLAUDECODE", "AIOS_CONFIG_DIR", "SHELF_INVOICES_BOOKS", "PYTHONUSERBASE", "CLAUDE_PID", "CLAUDE_HOOK",
                "CLAUDE_EFFORT"):
            env.pop(key, None)
    env["PATH"] = ":".join([str(HOME / ".local/bin")] + [p for p in env["PATH"].split(":") if "bb.app" not in p])
    return env


def scrub(text):
    for k, v in os.environ.items():
        if k.startswith("ANTHROPIC_") and k != "ANTHROPIC_BASE_URL" and len(v) >= 8:
            text = text.replace(v, "<KEY>")
    text = text.replace(REAL_HOME, "$REAL_HOME")
    return re.sub(r"(sk-|eyJ)[A-Za-z0-9_\-]{16,}", r"\1<KEY>", text)


def record(kind, text):
    path = PROOF / ("%s_%s.md" % (kind, VERSION))
    PROOF.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with path.open("a", encoding="utf-8") as f:
        if new:
            title = "Sandbox install" if kind == "sandbox" else "Prompt proof"
            f.write("# %s: shelf-invoices 2.0.1 (%s)\n\nA new member in a sandbox: HOME=%s, the pack installed from a "
                    "checkout of this branch, fictional data only (Acme Studio Ltd, Contoso GmbH, Northwind Bakery). "
                    "No key value appears below; paths under the real home are shown as $REAL_HOME.\n\n"
                    % (title, VERSION, HOME))
        f.write(scrub(text))


def run(argv, cwd=None, timeout=900):
    return subprocess.run([str(a) for a in argv], cwd=str(cwd or HOME), env=environment(), text=True,
                          capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL)


def step(kind, title, argv, cwd=None, note=""):
    proc = run(argv, cwd=cwd)
    lines = (proc.stdout + proc.stderr).rstrip().splitlines()
    if len(lines) > 60:
        lines = lines[:35] + ["[... %d lines trimmed ...]" % (len(lines) - 55)] + lines[-20:]
    out = ["## %s" % title, ""] + ([note, ""] if note else []) + [
        "```sh", shlex.join(str(a) for a in argv), "```", "```text"] + lines + ["[exit %d]" % proc.returncode, "```", ""]
    record(kind, "\n".join(out) + "\n")
    print(scrub("\n".join(out)))
    return proc


def prep():
    if CHECKOUT.exists():
        shutil.rmtree(CHECKOUT)
    subprocess.run(["rsync", "-a", "--exclude", ".git", "--exclude", ".claude/worktrees", "--exclude", "__pycache__",
                    str(REPO) + "/", str(CHECKOUT) + "/"], check=True)
    market = CHECKOUT / ".claude-plugin/marketplace.json"
    data = json.loads(market.read_text())
    entry = json.loads((CHECKOUT / "plugins/shelf-invoices/MARKETPLACE_ENTRY.json").read_text())
    data["plugins"] = [p for p in data["plugins"] if p.get("name") != entry["name"]] + [entry]
    market.write_text(json.dumps(data, indent=2) + "\n")
    print("checkout ready: %s" % CHECKOUT)


def plugin_bin():
    hits = sorted((HOME / ".claude/plugins/cache").glob("*/shelf-invoices/*/bin/shelf-invoices"))
    return hits[-1] if hits else None


def install():
    (HOME / ".claude").mkdir(parents=True, exist_ok=True)
    (HOME / "Work").mkdir(exist_ok=True)
    step("sandbox", "1. The tools: lxml for this Python (README step)",
         ["python3", "-m", "pip", "install", "--user", "--quiet", "--disable-pip-version-check", "lxml"])
    step("sandbox", "2. LibreOffice is found", ["sh", "-c", "command -v soffice || ls /Applications/LibreOffice.app"])
    step("sandbox", "3. Add the marketplace (a checkout of this branch)",
         ["claude", "plugin", "marketplace", "add", CHECKOUT])
    step("sandbox", "4. Install the start plugin", ["claude", "plugin", "install", "aios@navaigate-aios"])
    step("sandbox", "5. Install the pack", ["claude", "plugin", "install", "shelf-invoices@navaigate-aios"])
    b = plugin_bin()
    step("sandbox", "6. The command runs", [b, "--version"], note="The installed copy: `%s`" % b)
    step("sandbox", "7. No books yet: the command says what to do", [b, "next-number"])
    step("sandbox", "8. Practice books", [b, "sample", HOME / "Invoices-practice"])
    step("sandbox", "9. Next number", [b, "next-number", "--books", HOME / "Invoices-practice"])
    step("sandbox", "10. Make the Contoso invoice",
         [b, "make", HOME / "Invoices-practice/examples/contoso-workshop.json", "--books", HOME / "Invoices-practice"])
    step("sandbox", "11. Make it again: a new number, nothing overwritten",
         [b, "make", HOME / "Invoices-practice/examples/northwind-website.json", "--books", HOME / "Invoices-practice"])
    step("sandbox", "12. File ACME-002 (after looking at the PDF)",
         [b, "file", "ACME-002", "--books", HOME / "Invoices-practice"])
    step("sandbox", "13. Filing twice is refused", [b, "file", "ACME-002", "--books", HOME / "Invoices-practice"])
    step("sandbox", "14. The member's own books", [b, "init", HOME / "Documents/Invoices"])
    step("sandbox", "15. Empty settings are refused before any invoice", [b, "company", "check"])
    step("sandbox", "16. What is in the practice books",
         ["find", ".", "-type", "f"], cwd=HOME / "Invoices-practice")


def prompt(n, title):
    text = (REPO / "plugins/shelf-invoices/prompts.md").read_text()
    blocks = re.findall(r"```text\n(.*?)\n```", text, re.S)
    body = blocks[int(n) - 1].strip()
    extra = os.environ.get("PROMPT_SUFFIX", "").strip()
    if extra:
        body = body + " " + extra
    cwd = HOME / "Work" / ("invoices-%s" % n)
    cwd.mkdir(parents=True, exist_ok=True)
    args = ["claude", "-p", body, "--model", os.environ.get("PROOF_MODEL", "sonnet"), "--permission-mode",
            "bypassPermissions", "--output-format", "stream-json", "--verbose"]
    proc = run(args, cwd=cwd, timeout=1500)
    skills, calls, final = [], [], ""
    for line in proc.stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for block in ev.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    name, inp = block.get("name"), block.get("input", {})
                    if name == "Skill":
                        skills.append(inp.get("skill", ""))
                    elif name == "Bash":
                        calls.append("Bash: " + inp.get("command", "").strip())
                    elif name in ("Write", "Edit", "Read"):
                        calls.append("%s: %s" % (name, inp.get("file_path")))
                    else:
                        calls.append("%s: %s" % (name, json.dumps(inp)[:200]))
        if ev.get("type") == "result":
            final = ev.get("result", "")
    raw = PROOF / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / ("prompt%s_%s.jsonl" % (n, VERSION))).write_text(scrub(proc.stdout))
    out = ["## Prompt %s: %s" % (n, title), "", "Prompt:", "", "```text", body, "```", "",
           "Command: `claude -p \"<prompt>\" --model %s --permission-mode bypassPermissions` in `~/Work/invoices-%s`"
           % (os.environ.get("PROOF_MODEL", "sonnet"), n), "",
           "Skills the session invoked: %s" % (", ".join(s for s in skills if s) or "none"), "",
           "Tool calls (%d):" % len(calls), "", "```text"] + [c[:500] for c in calls[:40]] + [
           "```", "", "Claude's final answer:", "", "```text", final.strip()[:6000], "```", "",
           "Exit code: %d" % proc.returncode, ""]
    record("prompts", "\n".join(out) + "\n")
    print(scrub("\n".join(out))[:4000])


if __name__ == "__main__":
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "prep":
        prep()
    elif cmd == "install":
        install()
    elif cmd == "prompt":
        prompt(rest[0], rest[1])
    elif cmd == "sh":
        i = rest.index("--")
        step("prompts", rest[0], rest[i + 1:], cwd=HOME / "Work")
