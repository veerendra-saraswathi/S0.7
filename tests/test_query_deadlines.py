import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
QUERY = ROOT / "tools/query_deadlines.py"
FIRST = ROOT / "benchmarks/flir-4frnnp/run.json"


class DeadlineQueryTests(unittest.TestCase):
    def query(self, *paths):
        return subprocess.run([sys.executable, QUERY, "--json", *paths], capture_output=True, text=True)

    def test_six_clip_evidence(self):
        result = self.query(FIRST, *sorted((ROOT / "benchmarks/flir-six-clips").glob("*.json")))
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence = json.loads(result.stdout)
        self.assertEqual((evidence["deadline_misses"], evidence["total_frames"]), (32, 900))
        for run in evidence["runs"]:
            original = json.loads(Path(run["source_report"]).read_text())
            self.assertEqual(run["codec_build"], original["binary_sha256"])
            for miss in run["missed_frames"]:
                row = original["metrics"]["frames"][miss["frame_index"]]
                self.assertEqual((miss["file"], miss["encode_ms"]), (row["file"], row["encode_ms"]))
                self.assertGreater(miss["encode_ms"], run["deadline_ms"])

    def test_boundary_and_invalid_summary(self):
        record = json.loads(FIRST.read_text())
        metrics = record["metrics"]
        metrics["frames"][0]["encode_ms"] = metrics["encoder_deadline_ms"]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "run.json"
            path.write_text(json.dumps(record))
            self.assertEqual(self.query(path).returncode, 0)
            self.assertIn("duplicate report", self.query(path, path).stderr)
            metrics["deadline_misses"] += 1
            path.write_text(json.dumps(record))
            self.assertIn("differs from observations", self.query(path).stderr)
