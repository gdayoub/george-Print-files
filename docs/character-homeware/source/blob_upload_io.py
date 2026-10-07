"""Local side of GitHub connector blob uploads; never reads credentials.

The orchestration caller keeps base64 tool results out of model-visible output.
"""
import argparse
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RECEIPTS = ROOT / 'review' / 'blob_uploads.json'


def entry(path, repo_path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return dict(local_path=str(path), path=repo_path, size=len(data),
                sha=hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(),
                sha256=hashlib.sha256(data).hexdigest())


parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest='command', required=True)
p = sub.add_parser('chunk')
p.add_argument('path')
p.add_argument('start', type=int)
p.add_argument('length', type=int, default=600000)
p = sub.add_parser('bowl-plan')
p = sub.add_parser('scan')
p.add_argument('folder')
p.add_argument('--prefix', default='')
p = sub.add_parser('record')
p.add_argument('base64_json')
p = sub.add_parser('record-json')
p.add_argument('json')
args = parser.parse_args()

if args.command == 'chunk':
    with Path(args.path).open('rb') as f:
        f.seek(args.start)
        print(base64.b64encode(f.read(args.length)).decode())
elif args.command == 'bowl-plan':
    bowl = ROOT / 'bowl'
    prefix = 'prints/king-shark-catchall-bowl/'
    files = []
    for src in sorted((bowl / 'packages').glob('*.3mf')):
        files.append(entry(src, prefix + 'files/3mf/' + src.name))
    for src in sorted((bowl / 'packages' / 'STL_parts').glob('*.stl')):
        files.append(entry(src, prefix + 'files/stl/' + src.name))
    files.append(entry(bowl / 'King_Shark_Catchall_Bowl.blend', prefix + 'source/King_Shark_Catchall_Bowl.blend'))
    for src in sorted(bowl.glob('*.png')):
        files.append(entry(src, prefix + 'images/' + src.name))
    files.append(entry(bowl / 'engineering_validation.json', prefix + 'validation/engineering_validation.json'))
    for src in sorted((bowl / 'packages').glob('*.json')):
        files.append(entry(src, prefix + 'validation/' + src.name))
    print(json.dumps(files))
elif args.command == 'scan':
    folder = Path(args.folder).resolve()
    files = [entry(p, args.prefix + p.relative_to(folder).as_posix()) for p in sorted(folder.rglob('*')) if p.is_file()]
    print(json.dumps(files))
elif args.command in ('record', 'record-json'):
    new = json.loads(base64.b64decode(args.base64_json)) if args.command == 'record' else json.loads(args.json)
    data = json.loads(RECEIPTS.read_text()) if RECEIPTS.exists() else dict(repository='gdayoub/george-Print-files', files=[])
    keyed = {f['path']: f for f in data['files']}
    for f in new:
        keyed[f['path']] = f
    data['files'] = sorted(keyed.values(), key=lambda f: f['path'])
    data['updated_utc'] = datetime.now(timezone.utc).isoformat()
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    RECEIPTS.write_text(json.dumps(data, indent=2))
    print(json.dumps(dict(recorded=len(new), total=len(data['files']), receipt=str(RECEIPTS))))
