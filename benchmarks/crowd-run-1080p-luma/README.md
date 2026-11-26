# Crowd Run visible luma benchmark

The local source file `crowd_run_1080p50.y4m` has SHA-256 `e056e01fc13906dd9a84f5cc686a36888436379476577965a0866821caaf55c8`. Its Y4M header is `YUV4MPEG2 W1920 H1080 F50:1 Ip A1:1`. This records the supplied file dimensions and cadence. Original sensor acquisition metadata was unavailable.

Frames 0–99 were read consecutively. For each FRAME record the first 2,073,600 bytes supplied the 8-bit Y plane and the following 1,036,800 chroma bytes were skipped. The runner imported the luma planes as 1920 × 1080 u8 with zero-padded filenames 000.raw through 099.raw and collection ID `crowd-run-1080p-luma`. No spatial resampling or temporal subsampling was used. The fixed-2mbps profile used its nominal 30 fps budget. Host: x86_64, macOS 26.7.3.

| Host measurement | Result |
| --- | ---: |
| Encoded payload at nominal 30 fps | 1.996284 Mbps |
| Frame budget misses | 0/100 |
| Encoder deadline misses (two nominal frame periods) | 0/100 |
| Median / maximum encode time | 43.74 / 65.98 ms |
| Pooled PSNR, 8-bit peak 255 | 21.53 dB |

[Run report](run.json) records build hashes, arguments and per-frame observations. This measurement covers visible luma on the host. Full-colour, IR, device timing and acceptance near 1920 × 1200 require separate evidence.
