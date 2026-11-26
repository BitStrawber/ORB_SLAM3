# A Presentation Package

This directory contains the presentation-ready materials for workstream A:

```text
presentation/A/
├─ README.md
├─ A_baseline_slides.md
├─ A_PR_BODY.md
├─ experiment_notes.md
└─ figures/
   ├─ baseline_summary.png
   ├─ easy_rgb_overlay.png
   ├─ easy_rgb_imu_overlay.png
   └─ easy_rgbd_imu_overlay.png
```

## Suggested slide allocation

- Slide 3: ORB-SLAM3 baseline and research gap.
- Slide 5: shared TartanAir setup and evaluation protocol.
- Slide 6: baseline accuracy and coverage results.

## Required caveat

Do not state that fusion always improves accuracy. On easy/P000 the ordering is
scene-dependent, and P002 produced a different ordering from P000.
