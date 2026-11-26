# B/C Interface Handoff

Use the same ORB commit, Conda environment, YAML, camera intrinsics, and trajectory
window. Do not build a separate ORB fork for comparison.

## Required modes

- B: `rgb` and `rgb_imu`
- C: `rgb_imu` and `rgbd_imu`

## Required inputs

Every run uses the same manifest schema:

```text
timestamp,rgb_path,depth_path,gt_index,frame_id
```

Every run uses the same IMU schema:

```text
timestamp,gx,gy,gz,ax,ay,az
```

B may replace `rgb_path` with blurred, illuminated, or occluded images. C may replace
`depth_path` with corrupted float32-encoded depth images. Frame count, frame IDs,
timestamps, and ordering must remain unchanged.

## Depth contract

C should keep the TartanAir lossless encoding:

- `640x640x4` PNG
- `float32` decoded with `png.view("<f4")`
- units in meters
- invalid depth may be encoded as zero

The runner also accepts a one-channel `CV_32FC1` depth in memory, but the current file
adapter reads the lossless four-channel PNG format.

## Reproducible call

Use `prepare_sequence.py` with `--rgb-subdir` or `--depth-subdir` pointing to the
corrupted data directory. Then pass the resulting manifest and the untouched IMU CSV
to `run_baseline.py`.

## Evaluation contract

- `rgb`: Sim(3)
- `rgb_imu`: SE(3)
- `rgbd_imu`: SE(3)
- Report ATE, RPE, valid-pose coverage, lost events, mean latency, and P95 latency.
- Failed initialization must be preserved as a failed run.

## Minimum handoff smoke test

For both easy and hard:

1. Run clean `rgb`.
2. Run one B-corrupted `rgb`.
3. Run clean `rgb_imu`.
4. Run one C-corrupted `rgbd_imu`.

All four must produce a `metrics.json`. A low metric may be a valid result; silently
deleting failed frames or runs is not allowed.
