# GOES-19 weather raster compression experiment

Two CONUS band 13 Level 1b radiance rasters, in scan-start order, from the [verified input inventory](../../docs/infrared-input-coverage.md). The delivered grid is 2500 × 1500. Scan starts are five minutes apart.

The host run exported each entire Rad array in row-major order as unsigned little-endian 16-bit packed samples without scaling, interpolation or replacement of fill values. Inputs were named 000.raw and 001.raw. The S0.7 fixed-2mbps profile used a nominal 30 fps accounting rate, an 8,333-byte frame budget and a 66.67 ms encoder deadline. This rate describes the benchmark configuration. The original NetCDF files retain data quality flags and radiometric calibration. The codec stream contains only the sample grid.

| Scan | Encoded bytes | Encode ms | Good pixels scored | RMSE (packed counts) | Max absolute error (packed counts) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 8315 | 91.25 | 3702837 | 132.82 | 2870 |
| 2 | 8315 | 74.29 | 3702837 | 132.92 | 3494 |

Errors above compare the decoded samples to the original packed values where DQF equals 0 and Rad lies within 0–4094. Fill and flagged pixels are excluded from this score but included in the encoded input. The [machine report](run.json) also records whole-grid codec metrics. Timings cover a single host run. This two-scan experiment is separate from camera-video coverage and from the v4 snapshot.

### Reproduce the recorded output

From S0.7, run the following with a Python interpreter containing h5py and the recorded Bitrate2 binaries:

```sh
python benchmarks/goes19-c13-two-scans/reproduce.py --bin-dir "$HOME/bitrate2/ombitrate/build"
```

The replay downloads the two source NetCDF files to a temporary directory. To reuse local files, add `--scans FIRST.nc SECOND.nc`. It compares SHA-256 digests for the original scans, binaries, packed input, encoded stream and reconstructed samples. Encoder times are printed as new observations. They vary with host conditions.

### Replay timing records

The [two reported Mac replays](replays/reported-mac-times.csv) transcribe the per-scan encoder times from the operator’s terminal. Each invocation reported successful byte verification and one encoder deadline miss. Their exact start times were unrecorded.

Add `--record` to the replay command to save the full measured run under `replays/replay-<id>.json`. Each successful check produces a separate file with per-scan timings, observed misses, verification time in UTC, source digests and the digest of the baseline report.
