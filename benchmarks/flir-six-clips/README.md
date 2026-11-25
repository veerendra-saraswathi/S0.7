# FLIR ADAS v2 recorded infrared benchmark

Six 640 × 512 monochrome recordings, 150 consecutive frames each. The first row reuses the published host run. The other five clips were run sequentially on the same Mac with identical encoder and decoder binaries and arguments. Each linked report includes input and binary hashes, settings, and per-frame results.

| Clip | Frames | Mbps at 30 fps | Max bytes | Median encode ms | Max encode ms | Budget misses | Deadline misses | PSNR dB (14-bit peak) | Max error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [4FRnNp](../flir-4frnnp/run.json) | 150 | 1.998629 | 8331 | 16.84 | 49.51 | 0 | 0 | 71.70 | 28 |
| [5RSrbW](5RSrbW.json) | 150 | 1.998635 | 8331 | 22.31 | 58.85 | 0 | 0 | 73.25 | 23 |
| [6tLtjd](6tLtjd.json) | 150 | 1.998398 | 8329 | 33.71 | 93.99 | 0 | 4 | 72.79 | 40 |
| [SCiKdG](SCiKdG.json) | 150 | 1.998627 | 8331 | 21.57 | 125.21 | 0 | 1 | 70.83 | 47 |
| [ePoikf](ePoikf.json) | 150 | 1.998491 | 8330 | 37.09 | 367.05 | 0 | 17 | 72.66 | 35 |
| [vbrSzr](vbrSzr.json) | 150 | 1.998450 | 8329 | 44.22 | 106.75 | 0 | 10 | 71.86 | 31 |
| **All clips** | 900 | 1.998538 | 8331 | 30.15 | 367.05 | 0 | 32 | 72.11 | 47 |

A miss is an encoded frame larger than 8,333 bytes or an encoder time above 2/30 second. The bitrate covers encoded payload at nominal playback speed. For PSNR, squared differences were summed directly from original and reconstructed samples before conversion to dB, using a peak of 16,383. The aggregate pools samples across all six clips. Per-frame PSNR in the codec JSON uses the uint16 storage peak of 65,535.

Codec revision `921da01`, CMake Release, macOS host, tiled fixed-rate mode, uint16 samples and 16-bit codec setting. Each local input is named `flirv_<clip>_640x512_150.u16`; the [first run report](../flir-4frnnp/README.md) describes frame splitting and the S0.7 CLI. Timing covers in-memory encoding and will vary with host load. These results describe the six recordings at this resolution.
