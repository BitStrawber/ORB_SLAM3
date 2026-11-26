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

The frozen easy/P000 window has 87.7% RGB+IMU coverage and a mean ATE of 1.684 m over
three seeds. RGB-D+IMU reaches 98% coverage and 0.652 m ATE. Monocular inertial scale
initialization remains the weakest easy-case component.

## Hard trajectory

Hard P000 had substantially lower coverage than easy P000 in every mode. RGB+IMU had
the lowest coverage and the most loss transitions. No failed run was removed.
