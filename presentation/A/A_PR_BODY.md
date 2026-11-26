## Research question

How do RGB, RGB+IMU, and RGB-D+IMU modes of ORB-SLAM3 differ in trajectory accuracy,
tracking coverage, loss events, and processing latency on TartanAir V2?

## Input data and experiment configuration

- TartanAir V2, `OldTownSummer`
- Paired easy/hard `P000`
- Fixed frames 200-299, 20.0-29.9 seconds
- Seeds 0, 1, 2
- Camera: 640x640 pinhole, `fx=fy=320`, `cx=cy=320`, no distortion
- IMU Tbc: fixed optical-to-NED axis permutation
- ORB: 1250 features, scale 1.2, 8 levels
- Single-thread OpenMP/OpenBLAS/MKL
- RGB Sim(3), inertial modes SE(3), RPE interval 1 m

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
results/A/baseline_final/
results/A/validation/P002/
results/A/figures/
```

## Main findings

- Easy/RGB has 98% coverage but mean ATE of 1.659 m on the controlled keyframe metric.
- Easy/RGB+IMU has 73.3% coverage and two usable seeds with mean ATE 0.123 m.
- Easy/RGB-D+IMU has 98% coverage and mean ATE 0.224 m.
- Hard runs cross map frames; ATE/RPE are reported as N/A and coverage/loss events remain.
- On the identical 20.0-22.0 second hard window, ATE is 0.203/0.911/0.877 m for RGB,
  RGB+IMU, and RGB-D+IMU; all modes remain on map 0.
- A P002 holdout changes the easy ordering, so no universal fusion advantage is claimed.

## Interface changes

- Adds a headless TartanAir runner and deterministic input/seed handling.
- Adds `map_id`, `trajectory_source`, and fixed-window validity metadata.
- Adds `trajectory_est.tum`, `trajectory_frames.tum`, and raw optimized trajectory output.
- Adds reusable aggregation and evo evaluation scripts.
- Adds a separately evaluated hard common-window comparison with identical duration
  and trajectory source.
