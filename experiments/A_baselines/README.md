# A Baseline v0

## Frozen experiment

- Dataset: TartanAir V2
- Environment: `OldTownSummer`
- Easy trajectory: `Data_easy/P000`
- Hard trajectory: `Data_hard/P000`
- Evaluation window: frames 200-299, 20.0-29.9 seconds at 10 Hz
- Modes: `rgb`, `rgb_imu`, `rgbd_imu`
- Seeds: `0`, `1`, `2`
- Camera: pinhole, 640x640, `fx=fy=320`, `cx=cy=320`, zero distortion
- IMU: 100 Hz, aligned with `lcam_front`

The window is intentionally short because longer windows cross ORB-SLAM3 map resets,
which creates discontinuous coordinate frames. The window and the resulting failure
rate are part of the frozen experiment definition.

The camera-to-IMU transform is the fixed optical-to-NED axis permutation:

```text
[0 0 1 0]
[1 0 0 0]
[0 1 0 0]
[0 0 0 1]
```

IMU noise and random-walk values use the ORB-SLAM3 EuRoC magnitudes, not a near-zero
placeholder covariance.

The comparison protocol uses the same optimized-keyframe body-frame trajectory as the
primary metric source for every mode. Per-frame and largest-map trajectories are retained
as diagnostic artifacts. ATE/RPE are computed over the full frozen window only when all
valid tracking frames belong to one map; otherwise they are marked unavailable. OpenMP,
OpenBLAS, and MKL are fixed to one thread. RPE uses a 1 m interval. The seed is reapplied
after ORB-SLAM3 construction because the TwoViewReconstruction constructor seeds its own
RNG.

## Environment

```bash
export A_ROOT=/path/to/ORB_SLAM3_A
export REPO_ROOT=/path/to/ORB_SLAM3
source "${REPO_ROOT}/scripts/A/activate_a_orb.sh"
```

Paths:

```text
A_ROOT=<workspace containing data, conda_envs, install, build>
REPO_ROOT=<this Git checkout>
runner=A_ROOT/build/A_baselines/run_tartanair
config=REPO_ROOT/configs/A/tartanair.yaml
vocabulary=REPO_ROOT/Vocabulary/ORBvoc.txt
```

Create the environment and build:

```bash
conda env create -f "${REPO_ROOT}/configs/A/environment.yml"
export A_CONDA_ENV="$(conda run -n a_orb python -c 'import sys; print(sys.prefix)')"
bash "${REPO_ROOT}/scripts/A/build_pangolin.sh"
bash "${REPO_ROOT}/experiments/A_baselines/build_a.sh"
```

The build requires Pangolin v0.6 at `A_PANGOLIN_PREFIX`, defaulting to
`A_ROOT/install/pangolin`.

Download and extract the public TartanAir assets:

```bash
python "${REPO_ROOT}/experiments/A_baselines/download_tartanair_a.py" \
  --data-root "${A_ROOT}/data/TartanAirV2"
```

## Prepare a sequence

```bash
python "${REPO_ROOT}/experiments/A_baselines/prepare_sequence.py" \
  --sequence-root "${A_ROOT}/data/TartanAirV2/OldTownSummer/Data_easy/P000" \
  --start-frame 200 \
  --num-frames 100 \
  --output "${REPO_ROOT}/results/A/inputs_final/OldTownSummer/easy/P000_2p0s_9p9s"
```

## Run one configuration

```bash
python "${REPO_ROOT}/experiments/A_baselines/run_baseline.py" \
  --binary "${A_ROOT}/build/A_baselines/run_tartanair" \
  --vocab "${REPO_ROOT}/Vocabulary/ORBvoc.txt" \
  --settings "${REPO_ROOT}/configs/A/tartanair.yaml" \
  --mode rgb \
  --manifest "${REPO_ROOT}/results/A/inputs_final/OldTownSummer/easy/P000_2p0s_9p9s/manifest.csv" \
  --imu "${REPO_ROOT}/results/A/inputs_final/OldTownSummer/easy/P000_2p0s_9p9s/imu.csv" \
  --output "${REPO_ROOT}/results/A/runs/new_run" \
  --seed 0 \
  --orb-root "${REPO_ROOT}"
```

The runner is headless, uses `bUseViewer=false`, paces input at the timestamp rate,
and writes `trajectory_est.tum`, `trajectory_frames.tum`, `trajectory_orb_raw.tum`,
`tracking.csv`, `run.log`, and `run_meta.json`. `trajectory_est.tum` is the optimized
keyframe trajectory in TartanAir body/NED coordinates and is the only primary comparison
trajectory.

## Evaluate

RGB uses Sim(3). RGB+IMU and RGB-D+IMU use SE(3). RPE uses a 1 m interval.

```bash
python "${REPO_ROOT}/experiments/A_baselines/evaluate_run.py" \
  --estimated RUN/trajectory_est.tum \
  --reference "${REPO_ROOT}/results/A/inputs_final/OldTownSummer/easy/P000_2p0s_9p9s/trajectory_gt.tum" \
  --tracking RUN/tracking.csv \
  --output RUN/metrics.json \
  --alignment sim3 \
  --plot RUN/trajectory_overlay.png
```

## Known results

The frozen handoff results are in:

```text
results/A/baseline_metrics.csv
results/A/baseline_metrics.json
results/A/figures/baseline_summary.png
results/A/baseline_final/
results/A/baseline_aggregate.csv
results/A/baseline_aggregate.json
```

Some easy/hard fusion runs still lose tracking. This is reported as an actual baseline
result and must not be replaced by successful-only segments.
