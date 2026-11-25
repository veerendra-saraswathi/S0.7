# Samanvaya 0.7

**Samanvaya 0.7 is EGurukul Apps’ visible and infrared imaging programme.** We are developing a laboratory software suite that brings six imaging problems into one review workflow. An engineer should be able to open a recorded collection, compare an original frame with a processed result, and trace that result to the sensor, calibration and software build that produced it.

This repository contains the product roadmap and a Python 3 utility for recording and verifying raw-frame collections. The component prototypes described below are developed separately. The integrated suite is in development.

## Try the first collection check

Use Python 3 and a completed collection of single-channel, headerless frames. Store one frame per `.raw` file in a directory and use zero-padded filenames in acquisition order. The manifest lists frames in filename order and records a SHA-256 digest for each. Width, height and storage format are supplied by the caller. The format describes storage (8-bit or little-endian 16-bit), not effective sensor precision.

From the repository root, run this two-frame synthetic example:

```sh
demo_dir=$(mktemp -d)
python3 -c 'from pathlib import Path; import sys; p = Path(sys.argv[1]); (p / "001.raw").write_bytes(bytes(range(4))); (p / "002.raw").write_bytes(bytes(range(4, 8)))' "$demo_dir"
python3 tools/collection.py create "$demo_dir" --id bench-demo --width 2 --height 2 --storage u8 > "$demo_dir/collection.json"
python3 tools/collection.py verify "$demo_dir/collection.json" "$demo_dir"
```

Expected output: `Verified 2 frames for bench-demo`. Verification checks the saved inventory and content digests. This first step establishes input identity for a later codec run.

## Run a lossless Bitrate2 round trip

Build the two C++17 CLI targets from a Bitrate2 checkout (tested with commit `921da01`). Set `codec_src` to that checkout. Run the collection example above in the same terminal first.

```sh
codec_src="$HOME/ombitrate"
cmake -S "$codec_src" -B "$codec_src/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "$codec_src/build" --target ewc_enc ewc_dec
python3 tools/codec_run.py "$demo_dir/collection.json" "$demo_dir" --bin-dir "$codec_src/build" --output "$demo_dir/runs"
```

A successful run prints a new directory containing the input manifest, encoded stream, reconstructed sequence and `run.json`. The report records the exact executable hashes, CLI settings and output hashes. The decoder produces little-endian 16-bit samples; 8-bit input values are zero-extended before encoding. Success requires the decoded sequence to match that canonical input byte for byte. Each invocation gets its own directory. This checks lossless reconstruction; it does not benchmark the fixed-rate profile.

### Measure the fixed-rate profile

Use a collection manifest and its frame directory with the same runner:

```sh
python3 tools/codec_run.py "$demo_dir/collection.json" "$demo_dir" --bin-dir "$codec_src/build" --output "$demo_dir/runs" --profile fixed-2mbps
```

This tiled profile targets 2,000,000 encoded bits/s at a nominal 30 fps (8,333 bytes/frame). In `run.json`, `metrics` records the actual stream bitrate at that playback rate, per-frame byte counts, encoder time, PSNR and maximum absolute sample error. PSNR uses the storage range (8 or 16 bits); JSON null means exact reconstruction. Encoder timing comes from the codec CSV, in milliseconds to three decimal places. Budget and two-frame deadline misses are counted and retained for review. The bitrate excludes network overhead; the tiny README example exercises the workflow only. Use representative full-size frames for performance evaluation.

### Verify a saved lossless run offline

Pass the directory printed by the codec runner to `python3 tools/verify_run.py /path/to/run-directory`.
The verifier checks the manifest and bitstream against the saved report, then checks the decoded samples against each source frame digest in order. It requires only Python and the four saved run files. This is a consistency check against the recorded evidence; authenticating the author or independently decoding the stream requires separate evidence.

## What the project will do

| Article 4 problem | Planned capability | What an engineer will be able to inspect |
| --- | --- | --- |
| 1. Target Segmentation in Infrared Images | Produce a region mask for a recorded IR image. | Original frame, mask overlay and reference annotation. |
| 2. Cross-Spectral Image Matching | Match corresponding visible and infrared views of a scene. | Image pair, alignment overlay and measured discrepancy. |
| 3. Non-Uniformity Correction for Uncooled Infrared Images | Correct non-uniform sensor response and compare the result with the original capture. | Before-and-after frames, calibration version and residual variation. |
| 4. Low-Bitrate, High-Resolution Image/Video Compression with Low Latency | Encode, store or transmit and reconstruct visible and IR imagery with per-frame metadata. | Reconstructed frame, bitrate, image quality and encoder latency. |
| 5. Development of Device Drivers for Custom Imaging Sensors on NVIDIA Jetson Series Hardware for ROS | Acquire and replay a reference sensor stream on Jetson. | Pixel format, timestamps, sequence gaps and capture continuity. |
| 6. Automatic Detection of Objects in Cluttered Visible and Infrared Band Images | Review automated observations on recorded imagery against independent annotations. | Labelled frames, missed objects and false detections. |

## Development status

As of 25 November 2026, EGurukul Apps has submitted proposals for **Problems 1, 2, 4 and 6**. Bitrate compression and object detection have progressed beyond proof of concept and are the first two solutions planned for technical review. Initial proof-of-concept work has begun on **Problems 3 and 5**.

The current compression and detection work can be followed in the component repositories: [Bitrate](https://github.com/veerendra-saraswathi/bitrate), [Bitrate Architecture E](https://github.com/veerendra-saraswathi/bitrate2) and [Object Detection](https://github.com/veerendra-saraswathi/detection).

## Product roadmap

| Phase | Product development | Demonstration milestone |
| --- | --- | --- |
| 1 · Integrated imaging suite | Bring acquisition, processing, compression and replay into a common collection format. Preserve original frames and record the settings used to produce each output. | Reopen a result, find its source frame and reproduce the processing run. Evaluate each module against its own criteria. |
| 2 · Collaborative imaging review | Add a searchable catalogue, shared imagery workspaces, versioned annotations and a semantic layer linking sensors, calibrations, runs and findings. | Two reviewers independently inspect the same evidence and reproduce a published finding. |
| 3 · Multi-laboratory deployment | Package the suite for local installation, controlled collection exchange, offline review and recovery. | A second laboratory imports an approved package, restores its records and reproduces the finding. |

The first integrated demonstration will use a recorded visible/IR collection. Its review package will preserve frame identifiers, timestamps, software versions and evaluation results so another engineer can repeat the demonstration.
