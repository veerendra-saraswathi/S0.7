# GOES-19 weather raster compression experiment

Two CONUS band 13 Level 1b radiance rasters, in scan-start order, from the [verified input inventory](../../docs/infrared-input-coverage.md). The delivered grid is 2500 × 1500. Scan starts are five minutes apart.

The host run exported each entire Rad array in row-major order as unsigned little-endian 16-bit packed samples without scaling, interpolation or replacement of fill values. Inputs were named 000.raw and 001.raw. The S0.7 fixed-2mbps profile used a nominal 30 fps accounting rate, an 8,333-byte frame budget and a 66.67 ms encoder deadline. This rate describes the benchmark configuration. The original NetCDF files retain data quality flags and radiometric calibration. The codec stream contains only the sample grid.

| Scan | Encoded bytes | Encode ms | Good pixels scored | RMSE (packed counts) | Max absolute error (packed counts) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 8315 | 91.25 | 3702837 | 132.82 | 2870 |
| 2 | 8315 | 74.29 | 3702837 | 132.92 | 3494 |

Errors above compare the decoded samples to the original packed values where DQF equals 0 and Rad lies within 0–4094. Fill and flagged pixels are excluded from this score but included in the encoded input. The [machine report](run.json) also records whole-grid codec metrics. Timings cover a single host run. This two-scan experiment is separate from camera-video coverage and from the v4 snapshot.
