# Infrared input coverage

The compression review calls for evidence near 1920 × 1200. The local dataset check below examined file headers, dataset export metadata, and existing benchmark records. It did not establish native infrared acquisition near that resolution.

| Input | Evidence examined | Finding |
| --- | --- | --- |
| Six FLIR ADAS v2 clips | [Six-clip benchmark](../benchmarks/flir-six-clips/README.md) | Recorded infrared encoder input is 640 × 512. |
| Crowd Run | [Y4M header and host run](../benchmarks/crowd-run-1080p-luma/README.md) | Recorded 1920 × 1080 visible luma. |
| Thermal Dogs and People export | Embedded export README and all three COCO annotation files in thermal.zip | All 203 JPEGs have annotation dimensions of 416 × 416. The export README documents stretch resizing. |
| Bracken, Frio and Marathon archives | First PNG image header encountered in each archive | Sampled dimensions are 1024 × 1024, 1024 × 1024 and 1024 × 640 respectively. Each header declares 16-bit grayscale storage. The sampled headers establish neither sensor modality nor native acquisition dimensions. |

For the next measurement, retain the source's acquisition metadata alongside the input identity: infrared camera or band, recorded dimensions, any crop or resize, sample storage and effective precision if documented, and acquisition order. Only the measured dimensions belong in the benchmark record. Acceptance of an approximate resolution remains a separate review decision.

## Weather-satellite input candidate

Two original NOAA GOES-19 ABI Level 1b CONUS NetCDF files were inspected for a weather-imagery compression experiment. Both contain a 2500 × 1500 radiance product grid (x × y) for band 13. The first file reports a band wavelength of 10.33 µm. Its Rad variable uses int16 storage with unsigned interpretation, a packed valid range of 0–4094, and scale and offset attributes. Preserve the data quality flags and fill semantics if extracting samples.

| Scan start (UTC, 2025-07-19) | Original NOAA file | SHA-256 |
| --- | --- | --- |
| 12:01:18.1 | [First scan](https://noaa-goes19.s3.amazonaws.com/ABI-L1b-RadC/2025/200/12/OR_ABI-L1b-RadC-M6C13_G19_s20252001201181_e20252001203566_c20252001204051.nc) | `28699d68ae9713b9d230ae1f5f09cad600f44a5aace160fdbfca19100602c0fe` |
| 12:06:18.1 | [Second scan](https://noaa-goes19.s3.amazonaws.com/ABI-L1b-RadC/2025/200/12/OR_ABI-L1b-RadC-M6C13_G19_s20252001206181_e20252001208566_c20252001209001.nc) | `d17c68dc7bfef01d638057e02b660669dc2ae87700c199b25c2d9d16c856eaf5` |

These are Earth-observation scans five minutes apart. Product grid dimensions describe the delivered raster. This metadata check supplies no codec timings or native camera-video resolution evidence. Keep this candidate separate from the seven measured compression collections.
