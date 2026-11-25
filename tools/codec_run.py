"""Run a verified collection through the Bitrate2 lossless CLI."""
import argparse
import hashlib
import json
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
                    "-H", str(collection["height"]), "--bd", str(depth), "--lossless"]
        dec_args = ["-i", "encoded.ewc", "-o", "decoded.u16"]
        for name, options in [("ewc_enc", enc_args), ("ewc_dec", dec_args)]:
            subprocess.run([str(binaries[name]), *options], cwd=work, check=True, stdout=sys.stderr)
        expected = file_digest(packed)
        decoded = file_digest(work / "decoded.u16")
        if decoded != expected:
            raise ValueError("lossless verification failed: decoded sequence differs from input")
        report = {"schema": "s07.codec-run.v1", "profile": "lossless",
                  "collection_id": collection["collection_id"],
                  "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                  "frame_count": len(collection["frames"]), "binary_sha256": builds,
                  "encoder_args": enc_args, "decoder_args": dec_args,
                  "packed_input_sha256": expected, "decoded_sha256": decoded,
                  "encoded_sha256": file_digest(work / "encoded.ewc"),
                  "encoded_bytes": (work / "encoded.ewc").stat().st_size}
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
    parser.add_argument("--bin-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="parent for completed run directories")
    try:
        print(run(parser.parse_args()))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"codec run: {error}\n")
