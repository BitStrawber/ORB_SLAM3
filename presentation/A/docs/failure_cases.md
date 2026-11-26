# A Baseline Failure Cases

## Long-window map reset

On easy `P000`, a 60-second window produced many map resets. The estimated trajectory
was split across maps whose local coordinate frames were not connected. Concatenating
all returned poses produced ATE above 10 m even though early tracking was visually
correct.

The same issue appeared after roughly 10-30 seconds on other exploratory windows.

## Fast feed without timestamp pacing

The first runner fed images as quickly as possible. Local mapping could not keep up,
which increased tracking loss. The final runner waits according to the 10 Hz camera
timestamps.

## Inertial initialization

Inertial runs repeatedly logged:

```text
IMU is not or recently initialized
Reseting active map
```

The controlled easy/P000 window has 73.3% RGB+IMU coverage and 8.0 loss events. Two of
three seeds produce a connected optimized trajectory with ATE 0.120 and 0.126 m; one
seed has no usable keyframe trajectory. RGB-D+IMU reaches 98% coverage and 0.224 m ATE.
Monocular inertial scale initialization remains the weakest easy-case component.

## Hard trajectory

Hard P000 had substantially lower coverage than easy P000 in every mode. Mean coverage
was 27.0% for RGB, 20.0% for RGB+IMU, and 58.0% for RGB-D+IMU. The fixed window crosses
multiple map coordinate systems, so ATE is reported as N/A rather than concatenating
incompatible trajectories. No failed run was removed.

## Same-seed non-determinism

A repeated easy/RGB+IMU run with the same seed still differed because ORB-SLAM3 uses
internal worker threads. Math-library thread pools are fixed, but the full SLAM execution
is not bitwise deterministic. Results must therefore use repeated seeds and report
variability rather than a single selected run.
