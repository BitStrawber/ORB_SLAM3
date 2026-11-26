#!/usr/bin/env python3
"""Summarize Baseline v2 runs and create comparison figures."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


MODES = ["rgb", "rgb_imu", "rgbd_imu"]
DIFFICULTIES = ["easy", "hard"]
SEEDS = [0, 1, 2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    root = Path("/media/SSD0/XCX/ORB_SLAM3_A")
    run_root = root / "results/A/baseline_final"
    result_root = root / "results/A"
    figure_root = result_root / "figures"
    figure_root.mkdir(parents=True, exist_ok=True)

    rows = []
    for difficulty in DIFFICULTIES:
        for mode in MODES:
            for seed in SEEDS:
                run_dir = (
                    run_root
                    / difficulty
                    / "P000_window_200_299"
                    / f"{mode}_seed{seed}"
                )
                metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
                meta_path = run_dir / "run_meta.json"
                meta = (
                    json.loads(meta_path.read_text(encoding="utf-8"))
                    if meta_path.exists()
                    else {}
                )
                rows.append(
                    {
                        "dataset": "TartanAirV2",
                        "environment": "OldTownSummer",
                        "trajectory": "P000",
                        "window": "20.0-29.9s",
                        "difficulty": difficulty,
                        "mode": mode,
                        "seed": seed,
                        "run_status": metrics.get("status"),
                        "ate_rmse_m": metrics.get("ate_rmse"),
                        "rpe_translation_rmse_m": metrics.get("rpe_translation_rmse"),
                        "rpe_rotation_rmse_deg": metrics.get("rpe_rotation_deg_rmse"),
                        "orientation_ape_rmse_deg": metrics.get(
                            "orientation_ape_rmse_deg"
                        ),
                        "valid_pose_ratio": metrics.get("valid_pose_ratio"),
                        "lost_events": metrics.get("lost_events"),
                        "mean_latency_ms": metrics.get("mean_latency_ms"),
                        "p95_latency_ms": metrics.get("p95_latency_ms"),
                        "alignment": metrics.get("alignment"),
                        "evaluated_map_id": metrics.get("evaluated_map_id"),
                        "evaluated_map_valid_rows": metrics.get(
                            "evaluated_map_valid_rows"
                        ),
                        "evaluated_window_start_s": metrics.get(
                            "evaluated_window_start"
                        ),
                        "evaluated_window_end_s": metrics.get(
                            "evaluated_window_end"
                        ),
                        "git_commit": meta.get("git_commit", "unknown"),
                        "config_sha256": sha256(run_dir / "settings_snapshot.yaml"),
                    }
                )

    csv_path = result_root / "baseline_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (result_root / "baseline_metrics.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    aggregate = []
    for difficulty in DIFFICULTIES:
        for mode in MODES:
            selected = [
                row
                for row in rows
                if row["difficulty"] == difficulty and row["mode"] == mode
            ]
            summary = {"difficulty": difficulty, "mode": mode, "seed_count": len(selected)}
            for field in [
                "ate_rmse_m",
                "rpe_translation_rmse_m",
                "rpe_rotation_rmse_deg",
                "orientation_ape_rmse_deg",
                "valid_pose_ratio",
                "lost_events",
                "mean_latency_ms",
                "p95_latency_ms",
            ]:
                values = np.array(
                    [
                        float(row[field])
                        for row in selected
                        if row.get(field) is not None
                    ],
                    dtype=float,
                )
                summary[f"{field}_mean"] = float(values.mean()) if len(values) else None
                summary[f"{field}_std"] = (
                    float(values.std(ddof=1)) if len(values) > 1 else 0.0
                )
                summary[f"{field}_median"] = (
                    float(np.median(values)) if len(values) else None
                )
                summary[f"{field}_min"] = (
                    float(values.min()) if len(values) else None
                )
                summary[f"{field}_max"] = (
                    float(values.max()) if len(values) else None
                )
            aggregate.append(summary)
    aggregate_json = result_root / "baseline_aggregate.json"
    aggregate_json.write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    aggregate_csv = result_root / "baseline_aggregate.csv"
    with aggregate_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(aggregate[0]))
        writer.writeheader()
        writer.writerows(aggregate)

    validation_rows = []
    validation_root = result_root / "validation/P002"
    if validation_root.exists():
        for difficulty in DIFFICULTIES:
            for mode in MODES:
                metrics_path = validation_root / difficulty / mode / "metrics.json"
                if not metrics_path.exists():
                    continue
                metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
                validation_rows.append(
                    {
                        "dataset": "TartanAirV2",
                        "environment": "OldTownSummer",
                        "trajectory": "P002",
                        "window": "20.0-29.9s",
                        "difficulty": difficulty,
                        "mode": mode,
                        "seed": 0,
                        "status": metrics.get("status"),
                        "ate_rmse_m": metrics.get("ate_rmse"),
                        "orientation_ape_rmse_deg": metrics.get(
                            "orientation_ape_rmse_deg"
                        ),
                        "valid_pose_ratio": metrics.get("valid_pose_ratio"),
                        "lost_events": metrics.get("lost_events"),
                    }
                )
    validation_csv = result_root / "validation_metrics.csv"
    with validation_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(validation_rows[0]))
        writer.writeheader()
        writer.writerows(validation_rows)
    (result_root / "validation_metrics.json").write_text(
        json.dumps(validation_rows, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    colors = ["#4C78A8", "#F58518", "#54A24B"]
    for row_index, difficulty in enumerate(DIFFICULTIES):
        selected = [
            row for row in aggregate if row["difficulty"] == difficulty
        ]
        x = np.arange(len(MODES))
        ate_means = np.array([row["ate_rmse_m_mean"] for row in selected])
        ate_stds = np.array([row["ate_rmse_m_std"] for row in selected])
        ate_errors = np.vstack([np.minimum(ate_means, ate_stds), ate_stds])
        axes[row_index, 0].bar(
            x,
            ate_means,
            yerr=ate_errors,
            capsize=4,
            color=colors,
        )
        axes[row_index, 0].set_xticks(x, MODES)
        axes[row_index, 0].set_ylabel("ATE RMSE [m]")
        axes[row_index, 0].set_title(f"{difficulty}: trajectory error")
        axes[row_index, 0].grid(True, axis="y", alpha=0.3)

        coverage_means = 100.0 * np.array(
            [row["valid_pose_ratio_mean"] for row in selected]
        )
        coverage_stds = 100.0 * np.array(
            [row["valid_pose_ratio_std"] for row in selected]
        )
        coverage_errors = np.vstack(
            [np.minimum(coverage_means, coverage_stds), coverage_stds]
        )
        axes[row_index, 1].bar(
            x,
            coverage_means,
            yerr=coverage_errors,
            capsize=4,
            color=colors,
        )
        axes[row_index, 1].set_xticks(x, MODES)
        axes[row_index, 1].set_ylim(0, 105)
        axes[row_index, 1].set_ylabel("Valid pose coverage [%]")
        axes[row_index, 1].set_title(f"{difficulty}: coverage")
        axes[row_index, 1].grid(True, axis="y", alpha=0.3)
    fig.suptitle("A Baseline: TartanAir P000, 3 seeds, 20.0-29.9 seconds")
    fig.tight_layout()
    fig.savefig(figure_root / "baseline_summary.png", dpi=170)
    plt.close(fig)
    print(f"Wrote {csv_path}")
    print(f"Wrote {result_root / 'baseline_metrics.json'}")
    print(f"Wrote {aggregate_csv}")
    print(f"Wrote {aggregate_json}")
    print(f"Wrote {validation_csv}")
    print(f"Wrote {figure_root / 'baseline_summary.png'}")


if __name__ == "__main__":
    main()
