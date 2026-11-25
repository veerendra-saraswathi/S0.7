# Recorded infrared compression benchmark

One FLIR ADAS v2 sequence, video `video-4FRnNpmSmwktFJKjg`, original frames 745–894 inclusive. Source file: `flirv_4FRnNp_640x512_150.u16`, SHA-256 `2d9d5774a340b75c71737407dae95e9c412a148f6a50a845221e8605780caf02`. The test used 150 consecutive 640 × 512 monochrome frames in little-endian uint16 storage. No raw images are included here.

| Host measurement | Result |
| --- | ---: |
| Stream bitrate at nominal 30 fps | 1.998629 Mbps |
| Largest frame / budget | 8,331 / 8,333 bytes |
| Median / maximum encoder latency | 16.84 / 49.51 ms |
| Budget misses / two-frame deadline misses | 0 / 0 |
| Frames reported reliable by decoder | 150 / 150 |
| Sequence PSNR using a 14-bit reference peak of 16,383 | 71.70 dB |
| Worst absolute sample error | 28 counts |

S0.7 runner `7c2e3d7`, Bitrate2 `921da01`, CMake Release, AppleClang 21.0.0 on macOS. The runner used `fixed-2mbps` with its default uint16 coding depth of 16. The 14-bit PSNR above was independently calculated from the original and reconstructed samples using mean squared error across the entire clip. The per-frame PSNR in [run.json](run.json) uses a peak of 65,535; compare results only on the same peak convention.

To reproduce, split the identified file into consecutive 655,360-byte frames named `000.raw` through `149.raw`, create a collection manifest with width 640, height 512 and storage `u16le`, then run the fixed-rate profile as documented in the repository README. Encoder timings cover encoding of an in-memory frame. This host recording does not qualify Jetson latency, live transport or high-resolution IR performance.
