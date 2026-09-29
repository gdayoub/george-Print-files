"""Package the curated prototype without environments or recursive ZIPs. Standard library only."""
from pathlib import Path
import hashlib, json, zipfile

PROJECT=Path(__file__).resolve().parent.parent
REPO_URL='https://github.com/gdayoub/george-Print-files'
manifest=PROJECT/'validation/file_manifest.json'
archive=PROJECT/'downloads/dragon-pixel-shelves-prototype.zip'
files=sorted(p for p in PROJECT.rglob('*') if p.is_file()
    and not any(x in p.relative_to(PROJECT).parts for x in ['downloads','.venv','__pycache__','python_libs'])
    and p!=manifest)
# Use LF text so manifest hashes agree with Git and the ZIP on every platform.
for p in files:
    if p.suffix in ['.md','.json','.py','.scad','.txt']:
        data=p.read_bytes()
        if b'\r\n' in data: p.write_bytes(data.replace(b'\r\n',b'\n'))
records=[{'path':p.relative_to(PROJECT).as_posix(),'bytes':p.stat().st_size,
          'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
manifest.write_text(json.dumps({'version':'0.1.0-prototype','algorithm':'SHA-256','files':records},indent=2)+'\n',encoding='utf-8',newline='\n')
archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files+[manifest]:
        z.write(p,'prints/dragon-pixel-shelves/'+p.relative_to(PROJECT).as_posix())
    # Retain the repository layout so internal navigation works in the extracted kit.
    for name in ['SUPPORT.md','GETTING_STARTED.md']:
        z.write(PROJECT.parent.parent/'docs'/name,'docs/'+name)
    z.writestr('README.md','# Dragon + Pixel prototype kit\n\nOpen [the project guide](prints/dragon-pixel-shelves/README.md).\n\nFull gallery: '+REPO_URL+'\n\nThis is an untested prototype with no assigned load rating. The ZIP preserves the project layout and includes instructions, geometry, references, editable source and validation.\n')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(f'Packaged {len(files)+4} files: {archive}')
