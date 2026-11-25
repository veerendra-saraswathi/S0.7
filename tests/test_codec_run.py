"""Run against real Bitrate2 executables when BITRATE2_BIN_DIR is set."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"


@unittest.skipUnless(os.environ.get("BITRATE2_BIN_DIR"), "set BITRATE2_BIN_DIR for codec integration")
class CodecRunTests(unittest.TestCase):
    def test_both_storage_formats_and_modified_input(self):
        for storage, raw in [("u8", bytes(range(4))), ("u16le", bytes(range(8)))]:
            with self.subTest(storage=storage), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                frame = root / "000.raw"
                frame.write_bytes(raw)
                create = [sys.executable, str(TOOLS / "collection.py"), "create", temp,
                          "--id", "test", "--width", "2", "--height", "2", "--storage", storage]
                manifest = root / "collection.json"
                manifest.write_bytes(subprocess.check_output(create))
                output = root / "runs"
                command = [sys.executable, str(TOOLS / "codec_run.py"), manifest, temp,
                           "--bin-dir", os.environ["BITRATE2_BIN_DIR"], "--output", output]
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                directory = Path(result.stdout.strip())
                report = json.loads((directory / "run.json").read_text())
                expected = bytes([0, 0, 1, 0, 2, 0, 3, 0]) if storage == "u8" else raw
                self.assertEqual((directory / "decoded.u16").read_bytes(), expected)
                self.assertEqual(report["decoded_sha256"], hashlib.sha256(expected).hexdigest())
                verify = [sys.executable, str(TOOLS / "verify_run.py"), directory]
                subprocess.run(verify, capture_output=True, check=True)
                for name in ("decoded.u16", "encoded.ewc", "collection.json"):
                    path = directory / name
                    original = path.read_bytes()
                    path.write_bytes(bytes([original[0] ^ 1]) + original[1:])
                    self.assertNotEqual(subprocess.run(verify, capture_output=True).returncode, 0, name)
                    path.write_bytes(original)
                frame.write_bytes(raw[::-1])
                self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
                self.assertEqual(list(output.iterdir()), [directory])
