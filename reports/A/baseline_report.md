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
- ORB-SLAM3 fork commit at run time: `4861c078f11e3afafc38eb1d26b4444c6deb7d54`
- Evaluation: RGB with Sim(3), inertial modes with SE(3)
- RPE interval: 10 frames

The run is headless and paced at the camera timestamp rate. Pacing is required because
feeding frames faster than local mapping causes avoidable map resets.

## Results (mean over seeds 0, 1, 2)

| Difficulty | Mode | ATE RMSE [m] | RPE translation [m] | RPE rotation [deg] | Coverage | Lost events |
|---|---|---:|---:|---:|---:|---:|
| easy | rgb | 0.020 ± 0.004 | 1.069 ± 0.003 | 26.515 ± 0.010 | 98.0% ± 0.0% | 0 |
| easy | rgb_imu | 1.684 ± 0.162 | 0.842 ± 0.088 | 39.659 ± 18.821 | 87.7% ± 3.1% | 4.0 ± 1.0 |
| easy | rgbd_imu | 0.652 ± 0.011 | 1.240 ± 0.014 | 48.606 ± 0.059 | 98.0% ± 0.0% | 0 |
| hard | rgb | 1.151 ± 1.387 | 4.778 ± 1.286 | 37.065 ± 6.971 | 41.0% ± 6.1% | 5.7 ± 2.1 |
| hard | rgb_imu | 5.013 ± 0.392 | 7.110 ± 0.086 | 66.917 ± 7.487 | 24.3% ± 0.6% | 20.0 ± 1.0 |
| hard | rgbd_imu | 5.249 ± 0.003 | 4.329 ± 0.171 | 40.071 ± 0.809 | 59.7% ± 1.2% | 19.7 ± 0.6 |

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
