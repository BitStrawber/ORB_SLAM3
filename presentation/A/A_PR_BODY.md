## Research question

How do official ORB-SLAM3 RGB, RGB+IMU and RGB-D+IMU modes differ in trajectory
accuracy, tracking coverage, loss events, map continuity and processing latency on
TartanAir V2?

## Input data and experiment configuration

- TartanAir V2 `OldTownSummer`
- Easy P000 primary: frames 200-299, 20.0-29.9 s
- Easy P002 holdout: frames 200-299, 20.0-29.9 s
- Hard P001 robustness: frames 100-199, 10.0-19.9 s
- Seeds 0, 1 and 2 for every sequence and mode
- Camera: 640x640 pinhole, `fx=fy=320`, `cx=cy=320`, no distortion
- IMU: 100 Hz, fixed optical-to-NED axis permutation
- ORB: 1250 features, scale 1.2, 8 levels
- Single-thread OpenMP/OpenBLAS/MKL
- RGB Sim(3); inertial modes SE(3); RPE interval 1 m

## Run command

```bash
export A_ROOT=/path/to/ORB_SLAM3_A
export REPO_ROOT=/path/to/ORB_SLAM3
source "${REPO_ROOT}/scripts/A/activate_a_orb.sh"
bash "${REPO_ROOT}/scripts/A/build_pangolin.sh"
bash "${REPO_ROOT}/experiments/A_baselines/build_a.sh"
bash "${REPO_ROOT}/experiments/A_baselines/reproduce_baseline_v2.sh"
```

## Outputs

```text
results/A/baseline_metrics.csv
results/A/baseline_aggregate.csv
results/A/validation_metrics.csv
results/A/validation_aggregate.csv
results/A/hard_metrics.csv
results/A/hard_aggregate.csv
results/A/hard_common_metrics.csv
results/A/hard_common_aggregate.csv
results/A/figures/
```

## Main findings

- Easy/P000: RGB+IMU has the lowest conditional ATE but lower coverage.
- Easy/P002: both fusion modes outperform RGB.
- Hard/P001 coverage is 50.3% for RGB, 28.0% for RGB+IMU and 60.0% for RGB-D+IMU.
- Hard full-window ATE/RPE is N/A because valid poses span discontinuous maps.
- Per-map segment evaluation finds 4 evaluable RGB segments, no RGB+IMU segment and
  3 RGB-D+IMU segments.
- Hard conditional accuracy uses one preselected common map-0 interval, 12.9-14.9 s.
- RGB has zero coverage in one hard seed and that failure remains in the outputs.

## Interface changes

- Adds a headless TartanAir runner with explicit map IDs and tracking validity.
- Adds a shared manifest/IMU/tracking/trajectory result interface.
- Adds full easy, holdout and hard experiment matrices with three seeds.
- Adds map-aware evaluation that refuses to concatenate incompatible maps.
- Adds hard conditional-window validation and per-mode trajectory figures.
- Adds aggregation for ATE, RPE, coverage, loss, map switches and latency.
