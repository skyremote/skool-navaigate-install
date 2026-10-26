# aios-rules: changes needed in shared files

This stream does not edit shared files. The chief of staff applies these when merging.
Each change was tested on a copy of the branch (`tests/test_brain.py`: 37 tests pass with the
installer patch applied; the aios-rules sandbox install in `proof/sandbox_v1.md` used it).

## 1. `.claude-plugin/marketplace.json`
Add the object in `MARKETPLACE_ENTRY.json` to `plugins`, after `aios`.

## 2. `scripts/install_pack.py` (generic packs, bin links, dependency check)
Today the installer accepts only `aios` and `aios-brain`, and links only `bin/brain`. This patch:
- lists every folder under `plugins/` that has `.claude-plugin/plugin.json` as a valid pack;
- checks the `aios` dependency from each pack's own `plugin.json`, not by pack name;
- links every executable in a pack's `bin/` into `~/.local/bin`, refusing any foreign file there.

Apply with `patch -p1 < plugins/aios-rules/INTEGRATION.diff` from the repository root, or by hand:

```diff
--- a/scripts/install_pack.py	2026-10-26 10:04:38
+++ b/scripts/install_pack.py	2026-10-26 10:22:37
@@ -64,14 +64,18 @@
     return result
 
 
+def available_packs():
+    return sorted(p.name for p in (ROOT/'plugins').iterdir() if (p/'.claude-plugin/plugin.json').is_file())
+
+
 def install(pack):
     home = Path.home()
     plugin = ROOT/'plugins'/pack
     if not plugin.is_dir():
-        raise ValueError('Unknown pack. Available: aios, aios-brain')
-    if pack=='aios-brain' and not all((home/d/'aios').is_symlink() and (home/d/'aios').resolve()==(ROOT/'plugins/aios/skills/aios').resolve() for d in ('.codex/skills','.cursor/skills','.agents/skills')):
-        raise ValueError('aios-brain depends on aios. First run: ./install.sh aios')
+        raise ValueError('Unknown pack. Available: '+', '.join(available_packs()))
     manifest = json.loads((plugin/'.claude-plugin/plugin.json').read_text())
+    if 'aios' in manifest.get('dependencies',[]) and not all((home/d/'aios').is_symlink() and (home/d/'aios').resolve()==(ROOT/'plugins/aios/skills/aios').resolve() for d in ('.codex/skills','.cursor/skills','.agents/skills')):
+        raise ValueError(pack+' depends on aios. First run: ./install.sh aios')
     links = []
     for parent in ('.codex/skills','.cursor/skills','.agents/skills'):
         for source in sorted((plugin/'skills').iterdir()):
@@ -80,12 +84,16 @@
                 if not dest.is_symlink() or ROOT not in dest.resolve().parents:
                     raise ValueError('Existing skill preserved: '+str(dest)+'. Move it aside yourself before opting into 2.0.')
             links.append((source,dest))
+    # Every executable in the pack's bin/ is linked into ~/.local/bin, never over a foreign file.
+    if (plugin/'bin').is_dir():
+        for source in sorted(p for p in (plugin/'bin').iterdir() if p.is_file() and os.access(p,os.X_OK)):
+            command = home/'.local/bin'/source.name
+            if (command.exists() or command.is_symlink()) and (not command.is_symlink() or ROOT not in command.resolve().parents):
+                raise ValueError('Existing '+source.name+' executable preserved; move it aside before opting into this pack')
+            links.append((source,command))
     configs = []
     if pack=='aios-brain':
         command = home/'.local/bin/brain'
-        if (command.exists() or command.is_symlink()) and (not command.is_symlink() or ROOT not in command.resolve().parents):
-            raise ValueError('Existing brain executable preserved; move it aside before opting into this pack')
-        links.append((plugin/'bin/brain',command))
         codex = home/'.codex/config.toml'
         old = codex.read_text() if codex.exists() else ''
         configs.append((codex,codex_config(old,command)))
@@ -121,12 +129,12 @@
         print('Linked '+str(dest.relative_to(home)))
     receipt = home/'.local/share/aios/packs'/f'{pack}.json'
     atomic_write(receipt,json.dumps({'name':pack,'version':manifest['version'],'root':str(plugin),'harnesses':['codex','cursor','agents']},indent=2)+'\n')
-    print('Installed '+pack+' '+manifest['version']+'. Restart Codex and Cursor. Add ~/.local/bin to PATH for brain.')
+    print('Installed '+pack+' '+manifest['version']+'. Restart Codex and Cursor. Add ~/.local/bin to PATH for the pack commands.')
 
 
 def main():
     parser = argparse.ArgumentParser(description='Install one AIOS 2.0 pack for Codex and Cursor. No Claude config is changed.')
-    parser.add_argument('pack',choices=['aios','aios-brain'])
+    parser.add_argument('pack',choices=available_packs())
     args = parser.parse_args()
     try:
         install(args.pack)
```

## 3. `plugins/aios/scripts/status.py`
Line 67: `'available_packs':['aios','aios-brain']` becomes `['aios','aios-rules','aios-brain']`.

## 4. `plugins/aios/skills/aios/SKILL.md`
"Only `aios` and `aios-brain` ship in phase 1." becomes
"`aios`, `aios-rules` and `aios-brain` ship now." Leave the rest unchanged.

## 5. `README.md`
In the opening paragraph, "Phase 1 includes **aios** and **aios-brain**." becomes
"Ready now: **aios**, **aios-rules** and **aios-brain**." Add `./install.sh aios-rules` to the
Codex and Cursor block, between `aios` and `aios-brain`.

## 6. `ROADMAP.md`
Module 2 row, last column: "Planned: AGENTS.md, short rules, CLAUDE.md bridge" becomes
"Shipped for local review: folder map, AGENTS.md starter, CLAUDE.md bridge, path-scoped rules, budget check, monthly audit".

## 7. Lesson 1 (module 1) needs nothing from `plugins/aios/`
See `lessons/v2/01-start-here/INTEGRATION.md` for the one wording change it suggests.
