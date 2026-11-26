# A Baseline Slide Material

## Slide: Baseline setup

- Three ORB-SLAM3 modes: RGB, RGB+IMU, RGB-D+IMU.
- TartanAir V2 OldTownSummer, paired easy/hard P000.
- Frozen 10-second window: 20.0-29.9 seconds.
- Identical camera, ORB extractor, IMU noise, and timestamps for all modes.
- Headless execution paced at the original 10 Hz sensor rate.

## Slide: Important implementation corrections

- Decode TartanAir depth from lossless four-channel PNG to float32 metres.
- Apply the NED/optical camera-to-IMU axis permutation.
- Use ORB-SLAM3 EuRoC-scale IMU noise and random-walk parameters.
- Record ORB tracking state and map ID for every frame.
- Compute trajectory error on the largest continuous map segment while reporting
  full-sequence coverage and all loss events.

## Slide: Main results

Use `results/A/figures/baseline_summary.png` and these values:

- Easy RGB: 0.028 m ATE, 98% coverage.
- Easy RGB+IMU: 1.421 m ATE, 88.3% coverage.
- Easy RGB-D+IMU: 0.639 m ATE, 98% coverage.
- Hard RGB: 0.965 m mean map-segment ATE, 38.3% coverage.
- Hard RGB+IMU: 4.763 m ATE, 24% coverage.
- Hard RGB-D+IMU: 5.241 m ATE, 61% coverage.

All values are mean over three seeds.

## Slide: Interpretation

- The easy fused RGB-D run is stable and accurate.
- RGB+IMU remains the weakest easy mode due to monocular inertial scale initialization.
- Hard scenarios cause substantial loss in all modes.
- RGB-D+IMU provides the best hard coverage.
- Results are reported without deleting failed frames or failed seeds.
