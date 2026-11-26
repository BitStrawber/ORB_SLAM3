# A Baseline Report

## Scope

This report evaluates three ORB-SLAM3 modes on TartanAir V2 without modifying the
optimizer or fusion backend:

- `rgb`: `MONOCULAR`
- `rgb_imu`: `IMU_MONOCULAR`
- `rgbd_imu`: `IMU_RGBD`

## Controlled protocol

- Dataset: TartanAir V2, `OldTownSummer`
- Primary trajectories: easy `P000` and hard `P000`
- Fixed evaluation window: frames 200-299, 20.0-29.9 seconds
- Seeds: `0`, `1`, `2`
- Camera: pinhole 640x640, `fx=fy=320`, `cx=cy=320`, zero distortion
- Image input: OpenCV BGR (`Camera.RGB: 0`)
- IMU: 100 Hz, fixed optical-to-NED `Tbc`, zero translation
- ORB features: 1250
- Math-library threads: OpenMP/OpenBLAS/MKL fixed to one
- Seed is applied again after ORB-SLAM3 construction to override the internal
  TwoViewReconstruction seed
- Primary trajectory: ORB-SLAM3 optimized keyframe trajectory converted to body/NED
- Secondary trajectory: per-frame body trajectory and ORB largest-map diagnostic
- Coverage and loss events always use all frames in the fixed window
- RGB alignment: Sim(3); inertial alignment: SE(3)
- ATE/RPE are `N/A` if a fixed window contains multiple map frames

The same protocol was applied to P002 without further tuning.

## Results

Values are mean and standard deviation over valid seeds. For easy RGB+IMU, one of the
three keyframe trajectories was unusable, so aggregate error uses the two valid seeds.

| Difficulty | Mode | Valid seeds | ATE RMSE [m] | RPE translation [m] | RPE rotation [deg] | Coverage | Lost events |
|---|---|---:|---:|---:|---:|---:|---:|
| easy | rgb | 3/3 | 1.659 ± 0.021 | 1.270 ± 0.284 | 21.776 ± 5.539 | 98.0% | 0 |
| easy | rgb_imu | 2/3 | 0.123 | 0.608 | 19.907 | 73.3% ± 4.6% | 8.0 ± 1.7 |
| easy | rgbd_imu | 3/3 | 0.224 ± 0.012 | 0.634 ± 0.003 | 25.027 ± 0.440 | 98.0% | 0 |
| hard | rgb | 0/3 | N/A | N/A | N/A | 27.0% ± 5.3% | 6.3 ± 4.5 |
| hard | rgb_imu | 0/3 | N/A | N/A | N/A | 20.0% ± 1.7% | 18.3 ± 1.2 |
| hard | rgbd_imu | 0/3 | N/A | N/A | N/A | 58.0% | 20.0 |

## Interpretation

The controlled experiment does not show RGB+IMU outperforming RGB on easy/P000.
RGB+IMU has lower coverage, more loss events, and one seed without a usable optimized
keyframe trajectory. RGB-D+IMU is more stable than RGB+IMU but still does not outperform
RGB in ATE on this short easy window.

Hard scenarios cause repeated map changes. Under the fixed-window rule, ATE cannot be
defined because different maps do not share a consistent coordinate frame. Coverage and
loss events are reported instead of manufacturing a trajectory from incompatible maps.

These are valid findings, not grounds for retuning on the validation sequence.

## P002 holdout

| Difficulty | Mode | ATE [m] | Coverage | Lost events |
|---|---|---:|---:|---:|
| easy | rgb | 1.140 | 99% | 0 |
| easy | rgb_imu | 0.328 | 99% | 0 |
| easy | rgbd_imu | 0.281 | 98% | 0 |
| hard | rgb | N/A | 57% | 6 |
| hard | rgb_imu | N/A | 32% | 26 |
| hard | rgbd_imu | N/A | 64% | 17 |

P002 changes the sign of the easy accuracy ordering: both fusion modes outperform RGB
there. This scene dependence prevents a universal claim that one mode is always better.

## Hard dense diagnostic

The primary hard ATE/RPE table remains `N/A` because the fixed window crosses map
frames. For failure analysis and presentation only, the per-frame body trajectories
were separately evaluated on the largest connected map segment:

| Mode | ATE [m] | RPE translation [m] | RPE rotation [deg] | Coverage | Lost events |
|---|---:|---:|---:|---:|---:|
| rgb | 0.208 ± 0.052 | 0.484 ± 0.243 | 3.599 ± 1.388 | 27.0% | 6.3 |
| rgb_imu | 5.871 ± 0.431 | 4.887 ± 0.132 | 73.648 ± 17.840 | 20.0% | 18.3 |
| rgbd_imu | 5.467 ± 0.000 | 2.051 ± 0.000 | 24.740 ± 0.000 | 58.0% | 20.0 |

This table must always be labeled **dense per-frame diagnostic, largest connected map**.
It is not the primary fixed-window result and must not be mixed with the easy table.

## Repeatability

A repeated easy/RGB+IMU run with the same seed still differed because ORB-SLAM3 uses
internal worker threads. The run is reproducible in protocol, but not bitwise
deterministic. Seed variation must be interpreted together with scheduling variation.

## Limitations

- One simulation environment and one paired scene are not enough for broad generalization.
- The fixed short window avoids long trajectories where additional map resets dominate.
- TartanAir IMU is synthetic and ORB noise parameters use an EuRoC-scale setting.
- Hard ATE is unavailable because map continuity fails; this is a real experiment result.
- A separate dense diagnostic exists for presentations, but it is not the primary metric.
