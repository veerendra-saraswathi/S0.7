"""Create and verify manifests for single-channel raw frame collections."""
import argparse
import hashlib
import json
from pathlib import Path


def build_manifest(directory, collection_id, width, height, storage):
    if not collection_id.strip() or width < 1 or height < 1:
        raise ValueError("provide a collection ID and positive frame dimensions")
    if storage not in ("u8", "u16le"):
        raise ValueError("unsupported storage format")
    expected = width * height * (1 if storage == "u8" else 2)
    frames = []
    for path in sorted(directory.glob("*.raw")):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"{path.name}: expected a regular frame file")
        digest = hashlib.sha256()
        length = 0
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1 << 20), b""):
                length += len(block)
                digest.update(block)
        if length != expected:
            raise ValueError(f"{path.name}: expected {expected} bytes, found {length}")
        frames.append({"file": path.name, "sha256": digest.hexdigest()})
    if not frames:
        raise ValueError("no .raw frames found")
    return {"schema": "s07.raw-collection.v1", "collection_id": collection_id,
            "width": width, "height": height, "storage": storage, "frames": frames}


def verify_manifest(manifest_bytes, directory):
    saved = json.loads(manifest_bytes)
    if not isinstance(saved, dict) or saved.get("schema") != "s07.raw-collection.v1":
        raise ValueError("unsupported manifest schema")
    if (type(saved.get("width")) is not int or type(saved.get("height")) is not int
            or not isinstance(saved.get("collection_id"), str)):
        raise ValueError("invalid collection metadata")
    current = build_manifest(directory, saved["collection_id"], saved["width"],
                             saved["height"], saved["storage"])
    if current != saved:
        raise ValueError("frame inventory, order or content differs from the manifest")
    return current


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create", help="write manifest JSON to stdout")
    create.add_argument("directory", type=Path)
    create.add_argument("--id", required=True)
    create.add_argument("--width", required=True, type=int)
    create.add_argument("--height", required=True, type=int)
    create.add_argument("--storage", required=True, choices=["u8", "u16le"])
    verify = commands.add_parser("verify", help="check collection against saved manifest")
    verify.add_argument("manifest", type=Path)
    verify.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "create":
            manifest = build_manifest(args.directory, args.id, args.width, args.height, args.storage)
            print(json.dumps(manifest, indent=2))
        else:
            current = verify_manifest(args.manifest.read_bytes(), args.directory)
            print(f"Verified {len(current['frames'])} frames for {current['collection_id']}")
    except (KeyError, OSError, ValueError) as error:
        parser.exit(1, f"collection: {error}\n")


if __name__ == "__main__":
    main()
