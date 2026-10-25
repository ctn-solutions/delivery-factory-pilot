"""Package the bounded synthetic site and an exact source receipt; run no build hooks."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

REPOSITORY = 'ctn-solutions/delivery-factory-pilot'
FILES = ('index.html',)
MAX_BYTES = 65536


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL)


def build(root, *, repository, sha, ref):
    root = Path(root).resolve(strict=True)
    if repository != REPOSITORY or ref != 'refs/heads/main' or not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Unqualified repository, source revision or branch')
    if git(root, 'rev-parse', 'HEAD').decode().strip() != sha:
        raise ValueError('Checkout does not match requested source revision')
    for directory in (root / 'docs', root / 'docs/site'):
        if not stat.S_ISDIR(directory.lstat().st_mode):
            raise ValueError('Site directories must be real directories')
    site = root / 'docs/site'
    if sorted(p.name for p in site.iterdir()) != list(FILES):
        raise ValueError('Unexpected or missing static files')
    payload = {}
    for name in FILES:
        path = site / name
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > MAX_BYTES:
            raise ValueError('Static file must be bounded, regular and singly linked')
        relative = f'docs/site/{name}'
        tree = git(root, 'ls-tree', sha, '--', relative).decode().split()
        if len(tree) != 4 or tree[0] != '100644' or tree[1] != 'blob' or tree[3] != relative:
            raise ValueError('Static source must be a non-executable committed blob')
        # Publish committed bytes only; verify checkout equality without following symlinks.
        if int(git(root, 'cat-file', '-s', tree[2])) > MAX_BYTES:
            raise ValueError('Committed static blob exceeds size bound')
        data = git(root, 'cat-file', 'blob', tree[2])
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            current = os.fstat(fd)
            if (current.st_dev, current.st_ino) != (info.st_dev, info.st_ino):
                raise ValueError('Static source changed during validation')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                observed = stream.read(MAX_BYTES + 1)
        finally:
            os.close(fd)
        if len(data) > MAX_BYTES or observed != data:
            raise ValueError('Static checkout differs from committed source')
        payload[name] = data
    receipt = {'schema': 1, 'repository': repository, 'commit': sha,
               'files': {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()}}
    output = root / '_site'
    output.mkdir(mode=0o755)  # Refuse any existing output, including a symlink.
    for name, data in payload.items():
        (output / name).write_bytes(data)
    (output / 'deployment-receipt.json').write_text(json.dumps(receipt, sort_keys=True) + '\n')
    return receipt


if __name__ == '__main__':
    build(Path.cwd(), repository=os.environ['GITHUB_REPOSITORY'],
          sha=os.environ['GITHUB_SHA'], ref=os.environ['GITHUB_REF'])
