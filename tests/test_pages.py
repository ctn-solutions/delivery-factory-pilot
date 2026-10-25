import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.build_pages import build, REPOSITORY


class PagesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.site = self.root / 'docs/site'
        self.site.mkdir(parents=True)
        self.source = b'<!doctype html><title>Synthetic</title>\n'
        (self.site / 'index.html').write_bytes(self.source)
        self.git('init', '-q', '-b', 'main')
        self.git('add', 'docs')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Synthetic fixture')
        self.sha = self.git('rev-parse', 'HEAD').decode().strip()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.DEVNULL)

    def package(self, **changes):
        return build(self.root, **dict(repository=REPOSITORY, sha=self.sha,
                                      ref='refs/heads/main', **changes))

    def test_receipt_binds_exact_committed_bytes(self):
        receipt = self.package()
        self.assertEqual(receipt, {'schema': 1, 'repository': REPOSITORY, 'commit': self.sha,
                         'files': {'index.html': hashlib.sha256(self.source).hexdigest()}})
        self.assertEqual((self.root / '_site/index.html').read_bytes(), self.source)
        self.assertEqual(json.loads((self.root / '_site/deployment-receipt.json').read_text()), receipt)
        with self.assertRaises(FileExistsError):
            self.package()

    def test_source_binding_refuses_wrong_identity_and_dirty_bytes(self):
        for kwargs in ({'repository': 'other/repository'}, {'sha': '0' * 40},
                       {'sha': '../main'}, {'ref': 'refs/heads/feature'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                build(self.root, **({'repository': REPOSITORY, 'sha': self.sha,
                                    'ref': 'refs/heads/main'} | kwargs))
        (self.site / 'index.html').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.package()
        self.assertFalse((self.root / '_site').exists())

    def test_unsafe_files_are_refused_before_output(self):
        target = self.site / 'index.html'
        for kind in ('symlink', 'hardlink', 'fifo', 'directory', 'oversize', 'extra'):
            with self.subTest(kind=kind):
                target.unlink()
                if kind == 'symlink':
                    target.symlink_to(self.root / '.git/config')
                elif kind == 'hardlink':
                    os.link(self.root / '.git/config', target)
                elif kind == 'fifo':
                    os.mkfifo(target)
                elif kind == 'directory':
                    target.mkdir()
                elif kind == 'oversize':
                    target.write_bytes(b'x' * 65537)
                else:
                    target.write_bytes(self.source)
                    (self.site / 'extra.js').write_text('throw new Error()')
                with self.assertRaises(ValueError):
                    self.package()
                self.assertFalse((self.root / '_site').exists())
                if target.is_dir():
                    target.rmdir()
                else:
                    target.unlink()
                target.write_bytes(self.source)
                if kind == 'extra':
                    (self.site / 'extra.js').unlink()
        self.site.rename(self.root / 'real-site')
        self.site.symlink_to(self.root / 'real-site', target_is_directory=True)
        with self.assertRaises(ValueError):
            self.package()
