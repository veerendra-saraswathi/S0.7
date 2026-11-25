import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / "tools" / "collection.py"


class CollectionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.frame = self.root / "001.raw"
        self.frame.write_bytes(bytes([0, 255]))
        self.manifest = self.root / "collection.json"

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True)

    def create(self):
        return self.run_cli("create", self.root, "--id", "bench", "--width", "2",
                            "--height", "1", "--storage", "u8")

    def verify(self):
        return self.run_cli("verify", self.manifest, self.root)

    def test_roundtrip_and_changes(self):
        second = self.root / "002.raw"
        second.write_bytes(b"ab")
        result = self.create()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([f["file"] for f in json.loads(result.stdout)["frames"]],
                         ["001.raw", "002.raw"])
        self.manifest.write_text(result.stdout)
        self.assertEqual(self.verify().returncode, 0)
        second.write_bytes(b"ba")
        self.assertNotEqual(self.verify().returncode, 0)
        second.unlink()
        self.assertNotEqual(self.verify().returncode, 0)

    def test_truncated_frame(self):
        self.frame.write_bytes(b"x")
        self.assertIn("expected 2 bytes", self.create().stderr)
