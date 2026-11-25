# Repeat timing for FLIR ePoikf

Two sequential macOS replays of the same 150 frames, in the original order. The encoder and decoder commands and SHA-256 hashes were taken from the [baseline report](../flir-six-clips/ePoikf.json). The input sequence, both binaries, encoded stream, decoded samples and per-frame encoded sizes matched the baseline. All frames decoded reliably.

| Run | Start UTC | Median ms | Maximum ms | Deadline misses | Original misses repeated | Host load (1 min), start / end of encode |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Baseline | unrecorded | 37.09 | 367.05 | 17 | — | unrecorded / unrecorded |
| Repeat 1 | 2026-11-25T18:51:21+00:00 | 17.81 | 22.08 | 0 | 0 | 4.92 / 4.85 |
| Repeat 2 | 2026-11-25T18:51:27+00:00 | 18.79 | 27.87 | 0 | 0 | 4.85 / 4.94 |

Deadline: two frame periods at nominal 30 fps (66.67 ms). Indices in [frame-times.csv](frame-times.csv) are zero-based within this clip.

| Comparison | Frame indices |
| --- | --- |
| Original misses | 91, 92, 93, 94, 100, 101, 102, 103, 104, 105, 109, 123, 124, 125, 127, 128, 133 |
| Original misses repeated at least once | None |
| Missed in all three runs | None |
| Missed in both repeats only | None |

Host load is a system-wide one-minute average, sampled immediately before and after encoding. The original run has no load sample. These observations measure repeatability on this host; they cannot isolate CPU scheduling, thermal conditions or frame content as the cause of a missed deadline.
