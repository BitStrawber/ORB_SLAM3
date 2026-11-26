#!/usr/bin/env python3
"""Summarize dense hard-mode metrics as explicitly diagnostic results."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


MODES = ("rgb", "rgb_imu", "rgbd_imu")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    run_root = root / "results/A/baseline_final/hard/P000_window_200_299"
    result_root = root / "results/A"

    rows = []
    for mode in MODES:
        for seed in (0, 1, 2):
            run = run_root / f"{mode}_seed{seed}"
            metrics = json.loads(
                (run / "metrics_dense_diagnostic.json").read_text(encoding="utf-8")
            )
            rows.append(
                {
                    "dataset": "TartanAirV2",
                    "environment": "OldTownSummer",
                    "trajectory": "P000",
                    "difficulty": "hard",
                    "mode": mode,
                    "seed": seed,
                    "evaluation_type": "dense_per_frame_diagnostic",
                    "status": metrics.get("status"),
                    "ate_rmse_m": metrics.get("ate_rmse"),
                    "orientation_ape_rmse_deg": metrics.get(
                        "orientation_ape_rmse_deg"
                    ),
                    "rpe_translation_rmse_m": metrics.get(
                        "rpe_translation_rmse"
                    ),
                    "rpe_rotation_deg_rmse": metrics.get(
                        "rpe_rotation_deg_rmse"
                    ),
                    "valid_pose_ratio": metrics.get("valid_pose_ratio"),
                    "lost_events": metrics.get("lost_events"),
                    "evaluated_map_id": metrics.get("evaluated_map_id"),
                    "evaluated_window_start_s": metrics.get(
                        "evaluated_window_start"
                    ),
                    "evaluated_window_end_s": metrics.get(
                        "evaluated_window_end"
                    ),
                }
            )

    metrics_csv = result_root / "hard_dense_metrics.csv"
    with metrics_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (result_root / "hard_dense_metrics.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    aggregate = []
    for mode in MODES:
        selected = [row for row in rows if row["mode"] == mode]
        item = {"mode": mode, "seed_count": len(selected)}
        for field in [
            "ate_rmse_m",
            "orientation_ape_rmse_deg",
            "rpe_translation_rmse_m",
            "rpe_rotation_deg_rmse",
            "valid_pose_ratio",
            "lost_events",
        ]:
            values = np.asarray([float(row[field]) for row in selected])
            item[f"{field}_mean"] = float(values.mean())
            item[f"{field}_std"] = float(values.std(ddof=1))
        aggregate.append(item)

    aggregate_csv = result_root / "hard_dense_aggregate.csv"
    with aggregate_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(aggregate[0]))
        writer.writeheader()
        writer.writerows(aggregate)
    (result_root / "hard_dense_aggregate.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    x = np.arange(len(MODES))
    means = [row["ate_rmse_m_mean"] for row in aggregate]
    stds = [row["ate_rmse_m_std"] for row in aggregate]
    fig, axis = plt.subplots(figsize=(7, 5))
    axis.bar(
        x,
        means,
        yerr=np.vstack([np.minimum(means, stds), stds]),
        capsize=4,
        color=["#4C78A8", "#F58518", "#54A24B"],
    )
    axis.set_xticks(x, MODES)
    axis.set_ylabel("ATE RMSE [m]")
    axis.set_title(
        "Hard P000: dense per-frame diagnostic, largest connected map"
    )
    axis.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(result_root / "figures/hard_dense_diagnostic.png", dpi=170)
    plt.close(fig)
    print(metrics_csv)
    print(aggregate_csv)


if __name__ == "__main__":
    main()
