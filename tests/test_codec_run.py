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

    def test_fixed_rate_metrics(self):
        import random
        import struct
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw = random.Random(25).randbytes(128 * 128)
            (root / "001.raw").write_bytes(raw)
            manifest = root / "collection.json"
            manifest.write_bytes(subprocess.check_output([
                sys.executable, TOOLS / "collection.py", "create", root, "--id", "noise",
                "--width", "128", "--height", "128", "--storage", "u8"]))
            run = subprocess.check_output([
                sys.executable, TOOLS / "codec_run.py", manifest, root, "--profile", "fixed-2mbps",
                "--bin-dir", os.environ["BITRATE2_BIN_DIR"], "--output", root / "runs"], text=True)
            directory = Path(run.strip())
            metrics = json.loads((directory / "run.json").read_text())["metrics"]
            frame = metrics["frames"][0]
            reconstructed = struct.unpack("<16384H", (directory / "decoded.u16").read_bytes())
            max_error = max(abs(a - b) for a, b in zip(raw, reconstructed))
            self.assertGreater(max_error, 0)
            self.assertEqual(frame["max_abs_error"], max_error)
            self.assertEqual(metrics["budget_misses"], 0)
            self.assertEqual(metrics["achieved_bps"], (directory / "encoded.ewc").stat().st_size * 240)
            self.assertEqual(metrics["deadline_misses"], int(frame["encode_ms"] > 2000 / 30))
