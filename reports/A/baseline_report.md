# A Baseline v0 Report

## Scope

This report reproduces three ORB-SLAM3 modes on TartanAir V2 without modifying the
optimizer or fusion backend:

- `rgb`: `MONOCULAR`
- `rgb_imu`: `IMU_MONOCULAR`
- `rgbd_imu`: `IMU_RGBD`

## Frozen setup

- Environment: `OldTownSummer`
- Trajectories: easy `P000`, hard `P000`
- Evaluation window: frames 200-299, 20.0-29.9 seconds
- Camera: 640x640, pinhole, `fx=fy=320`, `cx=cy=320`, no distortion
- IMU: TartanAir synthetic IMU at 100 Hz, aligned with `lcam_front`
- IMU-camera extrinsic: NED/optical axis permutation, with zero translation
- ORB features: 2000
- ORB-SLAM3 fork commit at run time: `7eeb5c42c874693923ac3f655bfe342d740d45f7`
- Evaluation: RGB with Sim(3), inertial modes with SE(3)
- RPE interval: 10 frames

The run is headless and paced at the camera timestamp rate. Pacing is required because
feeding frames faster than local mapping causes avoidable map resets.

## Results (mean over seeds 0, 1, 2)

| Difficulty | Mode | ATE RMSE [m] | RPE translation [m] | RPE rotation [deg] | Coverage | Lost events |
|---|---|---:|---:|---:|---:|---:|
| easy | rgb | 0.020 ± 0.002 | 0.040 ± 0.006 | 0.151 ± 0.022 | 98.0% ± 0.0% | 0 |
| easy | rgb_imu | 0.789 ± 0.785 | 0.299 ± 0.437 | 6.675 ± 11.347 | 87.3% ± 10.8% | 3.0 ± 2.6 |
| easy | rgbd_imu | 0.067 ± 0.006 | 0.072 ± 0.011 | 0.245 ± 0.054 | 98.0% ± 0.0% | 0 |
| hard | rgb | 1.257 ± 1.799 | 1.727 ± 2.465 | 8.923 ± 12.113 | 35.0% ± 5.2% | 5.7 ± 3.1 |
| hard | rgb_imu | 4.718 ± 0.047 | 6.836 ± 0.215 | 56.044 ± 11.078 | 25.7% ± 2.1% | 19.0 ± 1.0 |
| hard | rgbd_imu | 5.259 ± 0.000 | 4.284 ± 0.000 | 33.135 ± 0.000 | 61.0% ± 0.0% | 19.0 ± 0.0 |

## Interpretation

The easy RGB run provides an excellent short-window baseline with centimetre-level ATE.
RGB-D+IMU is also stable at 98% coverage and sub-decimetre mean ATE. RGB+IMU has a good
median (0.575 m ATE, 92% coverage) but one outlier seed drives the mean and variance.
Hard runs are substantially less stable for all modes. RGB-D+IMU has the best hard
coverage, while RGB+IMU is the least stable.

The result must not be reported as proof that fusion improves accuracy. It is a valid
baseline reproduction showing that:

1. The data adapter and three ORB modes execute end-to-end.
2. Easy RGB can track accurately.
3. RGB-D+IMU is stable on easy; RGB+IMU scale initialization remains seed-sensitive.
4. Hard scenarios produce substantial degradation and map resets.

## Limitations

- Three fixed seeds are included for every sequence/mode combination.
- The 10-second window is selected to remain before major map-coordinate discontinuities.
- Map reset and lost frames are retained in coverage and lost-event metrics.
- The fixed optical-to-NED rotation follows the coordinate conventions; translation is
  zero because TartanAir places the IMU frame at the camera center.
- ATE from different map resets is not meaningful unless the maps are aligned; the
  frozen window avoids concatenating incompatible map coordinates.

## Holdout validation

The same code, configuration, frame range, and seed were applied without further tuning
to P002:

| Difficulty | Mode | ATE [m] | Orientation APE [deg] | Coverage | Lost events |
|---|---|---:|---:|---:|---:|
| easy | rgb | 0.293 | 20.869 | 99% | 0 |
| easy | rgb_imu | 0.060 | 0.387 | 99% | 0 |
| easy | rgbd_imu | 0.024 | 0.322 | 98% | 0 |
| hard | rgb | 8.633 | 95.563 | 24% | 5 |
| hard | rgb_imu | 9.273 | 45.557 | 47% | 22 |
| hard | rgbd_imu | 9.358 | 45.137 | 64% | 17 |

The holdout confirms that easy fusion tracking generalizes beyond the window used to
define the matrix, while hard scenarios remain genuinely challenging.
