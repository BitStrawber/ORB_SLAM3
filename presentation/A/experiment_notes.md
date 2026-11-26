# A Baseline Presentation Notes

## Core message

We reproduced ORB-SLAM3's RGB, RGB+IMU, and RGB-D+IMU modes on a controlled TartanAir
window. The experiment intentionally keeps failed and map-discontinuous runs visible.

## Controlled variables

- Same images, depth, IMU, GT, timestamp window, seed list, ORB configuration, and
  evaluation alignment policy.
- Same optimized-keyframe trajectory exporter for every mode.
- Coverage and loss events from the complete per-frame tracking log.
- ATE/RPE only when the fixed window remains in one map.

## Main results

- Easy RGB: 1.659 m ATE, 98% coverage.
- Easy RGB+IMU: 0.123 m ATE on two valid seeds, 73.3% mean coverage.
- Easy RGB-D+IMU: 0.224 m ATE, 98% coverage.
- Hard all modes: ATE N/A; coverage RGB 27.0%, RGB+IMU 20.0%, RGB-D+IMU 58.0%.

## Interpretation

RGB+IMU does not universally outperform RGB. On easy/P000 it is less accurate and has
more loss events. The P002 holdout gives the opposite easy ordering, showing strong scene
dependence. Hard failures are map-continuity failures, not missing data.
