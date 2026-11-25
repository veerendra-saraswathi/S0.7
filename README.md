# Samanvaya 0.7

**Samanvaya 0.7 is EGurukul Apps’ visible and infrared imaging programme.** We are developing a laboratory software suite that brings six imaging problems into one review workflow. An engineer should be able to open a recorded collection, compare an original frame with a processed result, and trace that result to the sensor, calibration and software build that produced it.

This repository starts with the product scope and roadmap. The component prototypes described below are developed separately. The integrated suite is in development.

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
