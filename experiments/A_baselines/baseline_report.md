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
- ORB-SLAM3 fork commit at run time: `8a3a0af3c2c787f31820d6c1600f176d85ddf4ef`
- Evaluation: RGB with Sim(3), inertial modes with SE(3)
- RPE interval: 10 frames

The run is headless and paced at the camera timestamp rate. Pacing is required because
feeding frames faster than local mapping causes avoidable map resets.

## Results (mean over seeds 0, 1, 2)

| Difficulty | Mode | ATE RMSE [m] | RPE translation [m] | RPE rotation [deg] | Coverage | Lost events |
|---|---|---:|---:|---:|---:|---:|
| easy | rgb | 0.028 ± 0.004 | 1.070 ± 0.003 | 26.515 ± 0.013 | 98.0% ± 0.0% | 0 |
| easy | rgb_imu | 1.421 ± 0.623 | 0.899 ± 0.201 | 29.342 ± 10.003 | 88.3% ± 5.1% | 3.0 ± 1.7 |
| easy | rgbd_imu | 0.639 ± 0.016 | 1.140 ± 0.121 | 48.581 ± 0.068 | 98.0% ± 0.0% | 0 |
| hard | rgb | 0.965 ± 1.346 | 5.373 ± 0.692 | 34.284 ± 9.299 | 38.3% ± 5.5% | 7.0 ± 1.7 |
| hard | rgb_imu | 4.763 ± 0.016 | 7.061 ± 0.000 | 62.594 ± 0.000 | 24.0% ± 0.0% | 20.0 ± 0.0 |
| hard | rgbd_imu | 5.241 ± 0.000 | 4.526 ± 0.000 | 41.006 ± 0.000 | 61.0% ± 0.0% | 19.0 ± 0.0 |

## Interpretation

The easy RGB run provides an excellent short-window baseline with centimetre-level ATE.
RGB-D+IMU is also stable at 98% coverage and sub-metre mean ATE. RGB+IMU has materially
worse translation accuracy and more loss events. Hard runs are substantially less stable
for all modes. RGB-D+IMU has the best hard coverage, while RGB+IMU is the least stable.

The result must not be reported as proof that fusion improves accuracy. It is a valid
baseline reproduction showing that:

1. The data adapter and three ORB modes execute end-to-end.
2. Easy RGB can track accurately.
3. RGB-D+IMU is stable on easy but RGB+IMU scale initialization remains weak.
4. Hard scenarios produce substantial degradation and map resets.

## Limitations

- Only one seed is included in Baseline v0.
- The 10-second window is selected to remain before major map-coordinate discontinuities.
- Map reset and lost frames are retained in coverage and lost-event metrics.
- The fixed optical-to-NED rotation follows the coordinate conventions; translation is
  zero because TartanAir places the IMU frame at the camera center.
- ATE from different map resets is not meaningful unless the maps are aligned; the
  frozen window avoids concatenating incompatible map coordinates.
