"""Check a saved lossless run against its recorded hashes, without a codec."""
import argparse
import hashlib
import json
from pathlib import Path

from codec_run import file_digest


def verify_run(directory):
    report = json.loads((directory / "run.json").read_bytes())
    if not isinstance(report, dict) or report.get("schema") != "s07.codec-run.v1":
        raise ValueError("unsupported run schema")
    if report.get("profile") != "lossless":
        raise ValueError("expected a lossless run")
    manifest_bytes = (directory / "collection.json").read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != report["manifest_sha256"]:
        raise ValueError("collection.json checksum mismatch")
    manifest = json.loads(manifest_bytes)
    if not isinstance(manifest, dict) or manifest.get("schema") != "s07.raw-collection.v1":
        raise ValueError("unsupported collection schema")
    if not isinstance(manifest["collection_id"], str) or manifest["collection_id"] != report["collection_id"]:
        raise ValueError("collection identity mismatch")
    width, height = manifest["width"], manifest["height"]
    if any(type(n) is not int or n <= 0 for n in (width, height)):
        raise ValueError("invalid frame dimensions")
    frames = manifest["frames"]
    if (not isinstance(frames, list) or not frames or type(report["frame_count"]) is not int
            or len(frames) != report["frame_count"]):
        raise ValueError("frame count mismatch")
    storage = manifest["storage"]
    if storage not in ("u8", "u16le"):
        raise ValueError("unknown sample format")

    encoded = directory / "encoded.ewc"
    if encoded.stat().st_size != report["encoded_bytes"] or file_digest(encoded) != report["encoded_sha256"]:
        raise ValueError("encoded.ewc size or checksum mismatch")

    sequence = hashlib.sha256()
    with (directory / "decoded.u16").open("rb") as stream:
        for frame in frames:
            source = hashlib.sha256()
            remaining = width * height * 2
            while remaining:
                size = min(remaining, 1 << 20)
                data = stream.read(size)
                if len(data) != size:
                    raise ValueError("truncated decoded.u16")
                sequence.update(data)
                if storage == "u8":
                    if any(data[1::2]):
                        raise ValueError("decoded sample exceeds u8 range")
                    data = data[::2]
                source.update(data)
                remaining -= size
            if not isinstance(frame, dict) or source.hexdigest() != frame.get("sha256"):
                raise ValueError("decoded frame differs from source frame checksum")
        if stream.read(1):
            raise ValueError("unexpected extra decoded data")
    if sequence.hexdigest() != report["decoded_sha256"] or sequence.hexdigest() != report["packed_input_sha256"]:
        raise ValueError("lossless sequence checksum mismatch")
    return f"Verified saved run for {manifest['collection_id']} ({len(frames)} frames)"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        print(verify_run(args.directory))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"verify run: {error}\n")
