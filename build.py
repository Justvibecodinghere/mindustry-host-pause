#!/usr/bin/env python3
import json, pathlib, zipfile
root = pathlib.Path(__file__).resolve().parent
meta = json.loads((root/'mod.json').read_text())
assert meta['hidden'] is True
assert meta['iosCompatible'] is True
assert meta['minGameVersion'] == '160.7'
assert not meta.get('hideBrowser', False)
out = root/'dist'/f"host-pause-{meta['version']}.zip"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for name in ['mod.json', 'README.md', 'TESTING.md', 'LICENSE', 'scripts/main.js', 'scripts/controller.js']:
        z.write(root/name, name)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert json.loads(z.read('mod.json')) == meta
print(out)

source = root/'dist'/f"host-pause-source-{meta['version']}.zip"
with zipfile.ZipFile(source, 'w', zipfile.ZIP_DEFLATED) as z:
    for name in ['mod.json', 'README.md', 'TESTING.md', 'LICENSE', '.gitignore', 'build.py', 'scripts/main.js', 'scripts/controller.js', 'tests/controller.test.js', 'tests/integration.py', 'tests/IosPathLauncher.java']:
        z.write(root/name, name)
print(source)
