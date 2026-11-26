"""Compare the two weather scans using saved records; no imagery or codec needed."""
import csv
import hashlib
import json
import math
from pathlib import Path


def compare(folder):
    raw = (folder / 'run.json').read_bytes()
    baseline = json.loads(raw)
    digest = hashlib.sha256(raw).hexdigest()
    deadline = baseline['metrics']['encoder_deadline_ms']
    frames = baseline['metrics']['frames']
    files = [row['file'] for row in frames]
    if len(files) != 2 or len(set(files)) != 2 or not math.isfinite(deadline) or deadline <= 0:
        raise ValueError('invalid two-scan baseline')

    rows = []
    def add(label, times):
        if not all(math.isfinite(t) and t >= 0 for t in times):
            raise ValueError(f'invalid timing in {label}')
        rows.append((label, times, sum(t > deadline for t in times)))

    add('Baseline JSON', [row['encode_ms'] for row in frames])
    for path in sorted((folder / 'replays').glob('replay-*.json')):
        record = json.loads(path.read_bytes())
        if record['replay']['baseline_sha256'] != digest or any(
                record[key] != baseline[key] for key in ('binary_sha256', 'encoder_args', 'decoder_args',
                'manifest_sha256', 'packed_input_sha256', 'encoded_sha256', 'decoded_sha256')):
            raise ValueError(f'{path.name}: recorded evidence differs from baseline')
        metrics = record['metrics']
        if metrics['encoder_deadline_ms'] != deadline or [r['file'] for r in metrics['frames']] != files:
            raise ValueError(f'{path.name}: timing observations are not comparable')
        add(path.stem, [row['encode_ms'] for row in metrics['frames']])
        if rows[-1][2] != metrics['deadline_misses']:
            raise ValueError(f'{path.name}: inconsistent deadline count')
    with (folder / 'replays' / 'reported-mac-times.csv').open(newline='') as stream:
        for row in csv.DictReader(stream):
            add('Terminal transcript ' + row['replay'], [float(row['scan_1_encode_ms']), float(row['scan_2_encode_ms'])])
    return deadline, rows


if __name__ == '__main__':
    deadline, rows = compare(Path(__file__).resolve().parent)
    print(f'Encoder deadline: {deadline:.3f} ms')
    print(f'{"Source":42} {"Scan 1 ms":>10} {"Scan 2 ms":>10} {"Misses":>8}')
    for label, (first, second), misses in rows:
        print(f'{label:42} {first:10.3f} {second:10.3f} {misses:8}')
