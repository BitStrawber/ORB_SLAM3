# A Baseline Slide Material

## Slide: Controlled setup

- Three ORB-SLAM3 modes: RGB, RGB+IMU, RGB-D+IMU.
- TartanAir V2 OldTownSummer, paired easy/hard P000.
- Fixed window: frames 200-299, 20.0-29.9 seconds.
- Same camera, ORB parameters, IMU noise, timestamps, and seeds.
- Same optimized-keyframe body trajectory exporter for every mode.
- Fixed single-thread math libraries; viewer disabled.

## Slide: Experimental controls

- BGR input is declared correctly.
- TartanAir NED/optical `Tbc` is applied consistently.
- Seed is injected after ORB-SLAM3 construction.
- Coverage and loss events use all frames.
- ATE/RPE are N/A when a fixed window crosses map coordinate systems.
- Optimized, per-frame, and raw trajectories are stored separately.

## Slide: Main results

Use `results/A/figures/baseline_summary.png`.

- Easy RGB: 1.659 m ATE, 98% coverage.
- Easy RGB+IMU: 0.123 m ATE on 2/3 valid seeds, 73.3% coverage.
- Easy RGB-D+IMU: 0.224 m ATE, 98% coverage.
- Hard RGB: ATE N/A, 27.0% coverage.
- Hard RGB+IMU: ATE N/A, 20.0% coverage.
- Hard RGB-D+IMU: ATE N/A, 58.0% coverage.

## Slide: Interpretation

- RGB+IMU is not universally better than RGB on a short easy sequence.
- P002 easy changes the ordering: RGB+IMU 0.328 m and RGB-D+IMU 0.281 m outperform
  RGB at 1.140 m.
- Hard sequences produce map changes severe enough that fixed-window ATE is undefined.
- Coverage and loss events are reported rather than hiding this failure.
- No validation sequence was used for further parameter tuning.
