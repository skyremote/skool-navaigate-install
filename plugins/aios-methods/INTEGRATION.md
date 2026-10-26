# Integration notes for aios-methods (stream D)

These are changes to shared files that stream D does not own. The chief of staff applies them when merging.
The same notes cover `aios-models` and `aios-ship`.

## 1. `.claude-plugin/marketplace.json`

Add the three entries from each pack's `MARKETPLACE_ENTRY.json` to the `plugins` array, in module order:
`aios-methods` (module 9), `aios-models` (module 10), `aios-ship` (module 11).

## 2. `scripts/install_pack.py`: install any pack, link its `bin/` tools

Today the installer accepts only `aios` and `aios-brain`. This patch:

- lists every folder under `plugins/` that has a `.claude-plugin/plugin.json`;
- requires `aios` first for every other pack, not only `aios-brain`;
- links each file in a generic pack's `bin/` into `~/.local/bin`, refusing any existing file that is not ours.

The `aios-brain` path is unchanged. The sandbox proofs for all three stream D packs ran with this patch applied
to a copy of the repository in `/tmp`.

```diff
--- a/scripts/install_pack.py
+++ b/scripts/install_pack.py
@@ -13,6 +13,10 @@
 ROOT = Path(__file__).resolve().parents[1]
 
 
+def available_packs():
+    return sorted(p.name for p in (ROOT/'plugins').iterdir() if (p/'.claude-plugin/plugin.json').is_file())
+
+
 def atomic_write(path,text):
     path.parent.mkdir(parents=True,exist_ok=True)
     fd,name = tempfile.mkstemp(prefix='.'+path.name+'-',dir=str(path.parent))
@@ -68,9 +72,9 @@
     home = Path.home()
     plugin = ROOT/'plugins'/pack
     if not plugin.is_dir():
-        raise ValueError('Unknown pack. Available: aios, aios-brain')
-    if pack=='aios-brain' and not all((home/d/'aios').is_symlink() and (home/d/'aios').resolve()==(ROOT/'plugins/aios/skills/aios').resolve() for d in ('.codex/skills','.cursor/skills','.agents/skills')):
-        raise ValueError('aios-brain depends on aios. First run: ./install.sh aios')
+        raise ValueError('Unknown pack. Available: '+', '.join(available_packs()))
+    if pack!='aios' and not all((home/d/'aios').is_symlink() and (home/d/'aios').resolve()==(ROOT/'plugins/aios/skills/aios').resolve() for d in ('.codex/skills','.cursor/skills','.agents/skills')):
+        raise ValueError(pack+' depends on aios. First run: ./install.sh aios')
     manifest = json.loads((plugin/'.claude-plugin/plugin.json').read_text())
     links = []
     for parent in ('.codex/skills','.cursor/skills','.agents/skills'):
@@ -99,6 +103,13 @@
             raise ValueError('Existing custom Cursor aios-brain server preserved; merge it manually')
         servers['aios-brain'] = dict(existing,command=str(command),args=['mcp'])
         configs.append((cursor,json.dumps(parsed,indent=2)+'\n'))
+    if pack not in ('aios','aios-brain') and (plugin/'bin').is_dir():
+        # Generic packs: link each executable into ~/.local/bin, refusing anything not ours.
+        for tool in sorted((plugin/'bin').iterdir()):
+            command = home/'.local/bin'/tool.name
+            if (command.exists() or command.is_symlink()) and (not command.is_symlink() or ROOT not in command.resolve().parents):
+                raise ValueError('Existing '+tool.name+' executable preserved; move it aside before opting into this pack')
+            links.append((tool,command))
     # All conflicts and both config files have been checked before the first write.
     for path,content in configs:
         path.parent.mkdir(parents=True,exist_ok=True)
@@ -121,12 +132,12 @@
         print('Linked '+str(dest.relative_to(home)))
     receipt = home/'.local/share/aios/packs'/f'{pack}.json'
     atomic_write(receipt,json.dumps({'name':pack,'version':manifest['version'],'root':str(plugin),'harnesses':['codex','cursor','agents']},indent=2)+'\n')
-    print('Installed '+pack+' '+manifest['version']+'. Restart Codex and Cursor. Add ~/.local/bin to PATH for brain.')
+    print('Installed '+pack+' '+manifest['version']+'. Restart Codex and Cursor. Add ~/.local/bin to PATH for its commands.')
 
 
 def main():
     parser = argparse.ArgumentParser(description='Install one AIOS 2.0 pack for Codex and Cursor. No Claude config is changed.')
-    parser.add_argument('pack',choices=['aios','aios-brain'])
+    parser.add_argument('pack',choices=available_packs())
     args = parser.parse_args()
     try:
         install(args.pack)
```

## 3. `plugins/aios/skills/aios/SKILL.md`

- Module 11's pack is `aios-ship`, not `aios-ship-it`. Change line `11. Ship it to others — aios-ship-it.`
  to `11. Ship it to others — aios-ship.`
- Replace "Only `aios` and `aios-brain` ship in phase 1." with the list of packs that have merged.

## 4. Kept out of the repo (Daniel, 26 October 2026)

Course content and build evidence do not go in this repository. Stream D keeps these out:

- `lessons/` (lesson sources and Skool HTML): in the classroom folder `150_Navbot_Classroom/aios-2/lessons_v2/<NN>-<slug>/`.
- `video/` (tutorial scripts, shot lists, SRTs, tapes and clips): in `150_Navbot_Classroom/aios-2/tutorials_v2/<NN>-<slug>/`.
- `plugins/*/proof/` (sandbox and eval evidence): in `150_Navbot_Classroom/aios-2/build-proof/<pack>/`.
  `tests/aios-methods/sandbox_lib_v1.py` and `eval_lib_v1.py` write there when `AIOS_PROOF_DIR` points at it.

Suggested `.gitignore` lines for the shared file: `lessons/`, `video/v2/` and `plugins/*/proof/`.

## 5. Eval runs need a copy without `dependencies`

`claude plugin eval` (2.1.310) does not load a path-target plugin whose `dependencies` lists `aios`: the with-arm then
runs with no plugin, so every skill-fired grader fails and the delta is zero. `tests/aios-methods/eval_lib_v1.py`
evaluates a `/tmp` copy with only that key removed. The same applies to `aios-brain` and every other 2.0 pack.

## 6. `/aios learn <module>`

Each stream D pack ships `TOUR.md` (under 150 lines) for `/aios learn 9`, `10` and `11`, and `plugin.json` carries
`"metadata": {"module": N}`. No pack depends on a bundle.

## 7. `README.md` and `ROADMAP.md`

Add modules 9, 10 and 11 with their pack names and one line each, taken from each pack's `README.md`.
