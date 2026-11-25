"""Run a verified collection through the Bitrate2 CLI."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
from uuid import uuid4

from collection import verify_manifest


def file_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fixed_rate_metrics(work, collection):
    with (work / "encoder.csv").open(newline="") as stream:
        encoded = list(csv.DictReader(stream))
    with (work / "decoder.csv").open(newline="") as stream:
        decoded = list(csv.DictReader(stream))
    frames = collection["frames"]
    if len(encoded) != len(frames) or len(decoded) != len(frames):
        raise ValueError("incomplete codec statistics")
    frame_bytes = collection["width"] * collection["height"] * 2
    if (work / "decoded.u16").stat().st_size != len(frames) * frame_bytes:
        raise ValueError("incomplete reconstructed sequence")
    budget = 2_000_000 // (8 * 30)
    deadline = 2000 / 30
    observations = []
    for i, (source, enc, dec) in enumerate(zip(frames, encoded, decoded)):
        if enc["frame"] != str(i) or dec["frame"] != str(i) or dec["reliable"] != "1":
            raise ValueError(f"unreliable or misordered frame {i}")
        size, elapsed = int(enc["bytes"]), float(enc["encode_ms"])
        error, psnr = int(dec["maxerr"]), float(dec["psnr"])
        if (size <= 0 or size != int(dec["bytes"]) or not math.isfinite(elapsed)
                or elapsed < 0 or error < 0 or not math.isfinite(psnr)):
            raise ValueError(f"invalid codec statistics for frame {i}")
        observations.append({"file": source["file"], "encoded_bytes": size,
                             "encode_ms": elapsed, "max_abs_error": error,
                             "psnr_db": psnr if error else None})
    total = sum(row["encoded_bytes"] for row in observations)
    if total != (work / "encoded.ewc").stat().st_size:
        raise ValueError("frame byte counts differ from bitstream size")
    return {"target_bps": 2_000_000, "nominal_fps": 30, "frame_budget_bytes": budget,
            "encoder_deadline_ms": deadline, "achieved_bps": total * 8 * 30 / len(frames),
            "budget_misses": sum(row["encoded_bytes"] > budget for row in observations),
            "deadline_misses": sum(row["encode_ms"] > deadline for row in observations),
            "frames": observations}


def run(args):
    manifest_bytes = args.manifest.read_bytes()
    collection = verify_manifest(manifest_bytes, args.directory)
    if sys.byteorder != "little":
        raise ValueError("Bitrate2 CLI requires a little-endian host")
    binaries = {name: (args.bin_dir / name).resolve() for name in ("ewc_enc", "ewc_dec")}
    builds = {name: file_digest(path) for name, path in binaries.items()}
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output) as stage:
        work = Path(stage)
        packed = work / "sequence.u16"
        with packed.open("wb") as stream:
            for frame in collection["frames"]:
                data = (args.directory / frame["file"]).read_bytes()
                if hashlib.sha256(data).hexdigest() != frame["sha256"]:
                    raise ValueError(f"{frame['file']} changed after verification")
                if collection["storage"] == "u8":
                    expanded = bytearray(len(data) * 2)
                    expanded[::2] = data
                    stream.write(expanded)
                else:
                    stream.write(data)
        depth = 8 if collection["storage"] == "u8" else 16
        enc_args = ["-i", packed.name, "-o", "encoded.ewc", "-W", str(collection["width"]),
                    "-H", str(collection["height"]), "--bd", str(depth)]
        dec_args = ["-i", "encoded.ewc", "-o", "decoded.u16"]
        if args.profile == "lossless":
            enc_args.append("--lossless")
        else:
            enc_args.extend(["--kbps", "2000", "--fps", "30", "--tile", "128",
                             "--stats", "encoder.csv"])
            dec_args.extend(["--ref", packed.name, "--report", "decoder.csv"])
        for name, options in [("ewc_enc", enc_args), ("ewc_dec", dec_args)]:
            subprocess.run([str(binaries[name]), *options], cwd=work, check=True, stdout=sys.stderr)
        expected = file_digest(packed)
        decoded = file_digest(work / "decoded.u16")
        if args.profile == "lossless" and decoded != expected:
            raise ValueError("lossless verification failed: decoded sequence differs from input")
        report = {"schema": "s07.codec-run.v1", "profile": args.profile,
                  "collection_id": collection["collection_id"],
                  "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                  "frame_count": len(collection["frames"]), "binary_sha256": builds,
                  "encoder_args": enc_args, "decoder_args": dec_args,
                  "packed_input_sha256": expected, "decoded_sha256": decoded,
                  "encoded_sha256": file_digest(work / "encoded.ewc"),
                  "encoded_bytes": (work / "encoded.ewc").stat().st_size}
        if args.profile == "fixed-2mbps":
            report["metrics"] = fixed_rate_metrics(work, collection)
        (work / "collection.json").write_bytes(manifest_bytes)
        (work / "run.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        packed.unlink()
        destination = args.output / f"run-{uuid4().hex}"
        work.rename(destination)
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--profile", choices=("lossless", "fixed-2mbps"), default="lossless")
    parser.add_argument("--bin-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="parent for completed run directories")
    try:
        print(run(parser.parse_args()))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"codec run: {error}\n")
