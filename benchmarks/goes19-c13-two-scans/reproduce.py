"""Replay the two published GOES-19 weather rasters against the recorded report."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
from urllib.request import urlopen
from uuid import uuid4

import h5py

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from codec_run import file_digest, run
from collection import build_manifest

BASE = 'https://noaa-goes19.s3.amazonaws.com/ABI-L1b-RadC/2025/200/12/'
SCANS = [
    ('OR_ABI-L1b-RadC-M6C13_G19_s20252001201181_e20252001203566_c20252001204051.nc',
     '28699d68ae9713b9d230ae1f5f09cad600f44a5aace160fdbfca19100602c0fe'),
    ('OR_ABI-L1b-RadC-M6C13_G19_s20252001206181_e20252001208566_c20252001209001.nc',
     'd17c68dc7bfef01d638057e02b660669dc2ae87700c199b25c2d9d16c856eaf5'),
]


def replay(args, work):
    baseline = Path(__file__).with_name('run.json')
    baseline_bytes = baseline.read_bytes()
    expected = json.loads(baseline_bytes)
    for name, sha in expected['binary_sha256'].items():
        if file_digest(args.bin_dir / name) != sha:
            raise ValueError(f'codec build differs: {name}')
    frames = work / 'frames'
    frames.mkdir()
    for i, (name, sha) in enumerate(SCANS):
        if args.scans:
            source = args.scans[i]
        else:
            source = work / name
            with urlopen(BASE + name, timeout=60) as response, source.open('wb') as out:
                shutil.copyfileobj(response, out)
        if file_digest(source) != sha:
            raise ValueError(f'source digest differs for scan {i+1}')
        with h5py.File(source) as data:
            packed = data['Rad'][:].astype('<u2')
            packed.tofile(frames / f'{i:03}.raw')
    manifest = work / 'collection.json'
    collection = build_manifest(frames, expected['collection_id'], 2500, 1500, 'u16le')
    manifest.write_text(json.dumps(collection, indent=2) + '\n')
    directory = run(argparse.Namespace(manifest=manifest, directory=frames, bin_dir=args.bin_dir,
                                       output=work / 'runs', profile=expected['profile']))
    actual = json.loads((directory / 'run.json').read_text())
    for key in ('manifest_sha256', 'binary_sha256', 'encoder_args', 'decoder_args', 'packed_input_sha256',
                'encoded_sha256', 'decoded_sha256'):
        if actual[key] != expected[key]:
            raise ValueError(f'replay differs from recorded report: {key}')
    if args.record:
        folder = baseline.parent / 'replays'
        folder.mkdir(exist_ok=True)
        actual['replay'] = {
            'verified_at_utc': datetime.now(timezone.utc).isoformat(),
            'baseline_sha256': hashlib.sha256(baseline_bytes).hexdigest(),
            'sources': [{'file': name, 'sha256': sha} for name, sha in SCANS],
        }
        destination = folder / f'replay-{uuid4().hex}.json'
        with tempfile.TemporaryDirectory(dir=folder) as stage:
            staged = Path(stage) / 'record.json'
            staged.write_text(json.dumps(actual, indent=2) + '\n', encoding='utf-8')
            staged.rename(destination)
        print('Saved verified replay:', destination)
    print('Verified both source scans, codec build, settings, packed input, bitstream and decoded samples.')
    print('Replay encoder times (ms):', [r['encode_ms'] for r in actual['metrics']['frames']])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bin-dir', type=Path, required=True)
    parser.add_argument('--scans', nargs=2, type=Path, help='local originals in acquisition order; default downloads both')
    parser.add_argument('--record', action='store_true', help='save a new verified run under the benchmark replays directory')
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix='goes19-replay-') as tmp:
            replay(args, Path(tmp))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f'weather replay: {exc}\n')
