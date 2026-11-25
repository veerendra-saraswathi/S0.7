"""Trace encoder deadline misses to their collection, codec build and run report."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re


def sha256_field(value):
    if not isinstance(value, str) or not re.fullmatch("[0-9a-f]{64}", value):
        raise ValueError("invalid SHA-256 identifier")
    return value


def duration(value):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("invalid duration in milliseconds")
    return value


def query_report(path):
    raw = path.read_bytes()
    record = json.loads(raw)
    if record["schema"] != "s07.codec-run.v1" or record["profile"] != "fixed-2mbps":
        raise ValueError("expected a fixed-2mbps codec-run.v1 report")
    metrics = record["metrics"]
    deadline = duration(metrics["encoder_deadline_ms"])
    frames = metrics["frames"]
    if not deadline or not isinstance(frames, list) or not frames:
        raise ValueError("missing deadline or frame observations")
    if type(record["frame_count"]) is not int or len(frames) != record["frame_count"]:
        raise ValueError("frame count differs from observations")
    misses = []
    for index, frame in enumerate(frames):
        elapsed = duration(frame["encode_ms"])
        if elapsed > deadline:
            misses.append({"frame_index": index, "file": frame["file"], "encode_ms": elapsed})
    if type(metrics["deadline_misses"]) is not int or len(misses) != metrics["deadline_misses"]:
        raise ValueError("stored deadline-miss count differs from observations")
    return {
        "source_report": str(path), "report_sha256": hashlib.sha256(raw).hexdigest(),
        "collection_id": record["collection_id"],
        "manifest_sha256": sha256_field(record["manifest_sha256"]),
        "codec_build": {name: sha256_field(record["binary_sha256"][name])
                        for name in ("ewc_enc", "ewc_dec")},
        "deadline_ms": deadline, "frame_count": len(frames), "missed_frames": misses,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", type=Path, nargs="+", help="saved fixed-rate run reports")
    parser.add_argument("--json", action="store_true", help="include frame evidence and full hashes")
    args = parser.parse_args()
    runs = []
    seen = set()
    for path in args.reports:
        try:
            run = query_report(path)
            if run["report_sha256"] in seen:
                raise ValueError("duplicate report supplied")
            seen.add(run["report_sha256"])
            runs.append(run)
        except (ValueError, KeyError, TypeError, OSError) as error:
            parser.exit(1, f"{path}: {error}\n")
    total = sum(run["frame_count"] for run in runs)
    misses = sum(len(run["missed_frames"]) for run in runs)
    if args.json:
        print(json.dumps({"total_frames": total, "deadline_misses": misses, "runs": runs}, indent=2))
        return
    print("Collection | Misses/frames | Encoder/decoder SHA-256 prefixes | Source report")
    for run in runs:
        build = run["codec_build"]
        print(f"{run['collection_id']} | {len(run['missed_frames'])}/{run['frame_count']} | "
              f"{build['ewc_enc'][:12]}/{build['ewc_dec'][:12]} | {run['source_report']}")
    print(f"Total: {misses} deadline misses in {total} frame observations across {len(runs)} reports")


if __name__ == "__main__":
    main()
