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
   ├─ validation_summary.png
   ├─ hard_robustness.png
   ├─ hard_common_summary.png
   ├─ hard_map_segments.png
   ├─ easy_rgb_overlay.png
   ├─ easy_rgb_imu_overlay.png
   ├─ easy_rgbd_imu_overlay.png
   ├─ validation_rgb_overlay.png
   ├─ validation_rgb_imu_overlay.png
   ├─ validation_rgbd_imu_overlay.png
   ├─ hard_rgb_overlay.png
   ├─ hard_rgb_imu_overlay.png
   └─ hard_rgbd_imu_overlay.png
```

## Suggested slide allocation

- Slide 3: ORB-SLAM3 baseline and research gap.
- Slide 5: shared TartanAir setup and evaluation protocol.
- Slide 6: baseline accuracy and coverage results.
- Slide 6 follow-up: hard robustness and conditional accuracy.

## Required caveat

Do not state that fusion always improves accuracy. P000 and P002 produce different
orderings. Hard full-window ATE is unavailable because map frames are discontinuous;
the separate common-window result must always be shown with valid-frame coverage.
