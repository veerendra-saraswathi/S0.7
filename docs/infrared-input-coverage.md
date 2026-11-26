# Infrared input coverage

The compression review calls for evidence near 1920 × 1200. The local dataset check below examined file headers, dataset export metadata, and existing benchmark records. It did not establish native infrared acquisition near that resolution.

| Input | Evidence examined | Finding |
| --- | --- | --- |
| Six FLIR ADAS v2 clips | [Six-clip benchmark](../benchmarks/flir-six-clips/README.md) | Recorded infrared encoder input is 640 × 512. |
| Crowd Run | [Y4M header and host run](../benchmarks/crowd-run-1080p-luma/README.md) | Recorded 1920 × 1080 visible luma. |
| Thermal Dogs and People export | Embedded export README and all three COCO annotation files in thermal.zip | All 203 JPEGs have annotation dimensions of 416 × 416. The export README documents stretch resizing. |
| Bracken, Frio and Marathon archives | First PNG image header encountered in each archive | Sampled dimensions are 1024 × 1024, 1024 × 1024 and 1024 × 640 respectively. Each header declares 16-bit grayscale storage. The sampled headers establish neither sensor modality nor native acquisition dimensions. |

For the next measurement, retain the source's acquisition metadata alongside the input identity: infrared camera or band, recorded dimensions, any crop or resize, sample storage and effective precision if documented, and acquisition order. Only the measured dimensions belong in the benchmark record. Acceptance of an approximate resolution remains a separate review decision.
