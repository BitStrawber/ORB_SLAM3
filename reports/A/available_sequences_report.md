# A Baseline: All Available Trajectory Sequences

## Scope

The local `OldTownSummer` TartanAir V2 package contains three Easy and three Hard
trajectory directories. This expanded matrix uses all six directories:

| Difficulty | Trajectory | Window |
|---|---|---:|
| Easy | P000 | frames 200-299 |
| Easy | P001 | frames 100-199 |
| Easy | P002 | frames 200-299 |
| Hard | P000 | frames 100-199 |
| Hard | P001 | frames 100-199 |
| Hard | P002 | frames 100-199 |

Each trajectory is evaluated with RGB, RGB+IMU and RGB-D+IMU and seeds 0, 1 and 2.
This produces 6 trajectories x 3 modes x 3 seeds = 54 runs.

## Evaluation rules

- Use the primary optimized-keyframe body trajectory when it is available.
- RGB uses Sim(3); inertial modes use SE(3).
- Report ATE/RPE only when the full window remains on one map.
- Keep failed initialization and empty keyframe trajectories as failed runs.
- Report valid-seed count together with every mean.
- Coverage, loss events and latency always use the complete 100-frame tracking log.

For a failed primary trajectory, the stored trajectory image is explicitly marked as a
per-frame by-map diagnostic. It is not treated as a continuous ATE trajectory.

## Easy results

Values are mean over valid metric seeds. Coverage uses all three runs.

| Trajectory | Mode | Valid seeds | ATE [m] | RPE trans. [m] | RPE rot. [deg] | Coverage | Loss events |
|---|---|---:|---:|---:|---:|---:|---:|
| P000 | RGB | 3/3 | 1.659 ± 0.021 | 1.270 ± 0.284 | 21.776 ± 5.539 | 98.0% | 0.0 |
| P000 | RGB+IMU | 2/3 | 0.123 ± 0.004 | 0.608 ± 0.023 | 19.907 ± 3.616 | 73.3% | 8.0 |
| P000 | RGB-D+IMU | 3/3 | 0.224 ± 0.012 | 0.634 ± 0.003 | 25.027 ± 0.440 | 98.0% | 0.0 |
| P001 | RGB | 3/3 | 2.635 ± 0.088 | 2.013 ± 0.068 | 9.476 ± 0.112 | 95.0% | 0.0 |
| P001 | RGB+IMU | 0/3 | N/A | N/A | N/A | 58.7% | 14.3 |
| P001 | RGB-D+IMU | 3/3 | 0.235 ± 0.022 | 1.296 ± 0.005 | 11.603 ± 0.969 | 98.0% | 0.0 |
| P002 | RGB | 3/3 | 1.103 ± 0.032 | 1.767 ± 0.042 | 15.104 ± 0.843 | 99.0% | 0.0 |
| P002 | RGB+IMU | 3/3 | 0.326 ± 0.002 | 0.766 ± 0.028 | 12.806 ± 0.282 | 99.0% | 0.0 |
| P002 | RGB-D+IMU | 3/3 | 0.281 ± 0.004 | 0.791 ± 0.023 | 10.325 ± 0.121 | 98.0% | 0.0 |

Easy P001 exposes a real initialization limitation: all three RGB+IMU runs had
tracking poses but no usable optimized keyframe trajectory. Its ATE is therefore
reported as `N/A`, not recovered from a successful-only segment.

## Hard results

| Trajectory | Mode | Valid seeds | ATE [m] | Coverage | Loss events | RPE |
|---|---|---:|---:|---:|---:|---|
| P000 | RGB | 3/3 | 0.588 ± 0.024 | 91.0% | 0.0 | available |
| P000 | RGB+IMU | 0/3 | N/A | 24.7% | 19.7 | N/A |
| P000 | RGB-D+IMU | 0/3 | N/A | 58.0% | 20.0 | N/A |
| P001 | RGB | 0/3 | N/A | 50.3% | 4.7 | N/A |
| P001 | RGB+IMU | 0/3 | N/A | 28.0% | 21.7 | N/A |
| P001 | RGB-D+IMU | 0/3 | N/A | 60.0% | 19.0 | N/A |
| P002 | RGB | 1/3 | 4.877 | 76.3% | 1.3 | available for 1 seed |
| P002 | RGB+IMU | 0/3 | N/A | 35.0% | 21.3 | N/A |
| P002 | RGB-D+IMU | 0/3 | N/A | 68.7% | 14.7 | N/A |

Hard results primarily measure robustness. Map discontinuities make a single
continuous ATE undefined for most runs.

## Output files

```text
results/A/all_sequences_metrics.csv
results/A/all_sequences_metrics.json
results/A/all_sequences_aggregate.csv
results/A/all_sequences_aggregate.json
results/A/available_sequence_trajectory_manifest.csv
results/A/available_sequences/trajectories/
results/A/figures/easy_available_trajectories.png
results/A/figures/hard_available_trajectories.png
```

## Limitations

- The package contains three physical trajectories per difficulty, not five.
- Windows are fixed 100-frame samples and do not represent complete sequence lengths.
- Hard results contain frequent map resets and low coverage.
- The same simulated environment is used for all six trajectories.
