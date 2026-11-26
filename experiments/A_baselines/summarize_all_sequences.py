#!/usr/bin/env python3
"""Summarize all six available TartanAir trajectory directories."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import yaml


MODES = ("rgb", "rgb_imu", "rgbd_imu")
SEEDS = (0, 1, 2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    matrix = yaml.safe_load(
        (root / "experiments/A_baselines/available_sequences.yaml").read_text(
            encoding="utf-8"
        )
    )
    rows = []
    for sequence in matrix["sequences"]:
        result_root = root / sequence["result_root"]
        for mode in MODES:
            for seed in SEEDS:
                run_dir = result_root / f"{mode}_seed{seed}"
                metrics = json.loads(
                    (run_dir / "metrics.json").read_text(encoding="utf-8")
                )
                rows.append(
                    {
                        "sample_id": sequence["id"],
                        "difficulty": sequence["difficulty"],
                        "trajectory": sequence["trajectory"],
                        "start_frame": sequence["start_frame"],
                        "mode": mode,
                        "seed": seed,
                        "status": metrics.get("status"),
                        "ate_rmse_m": metrics.get("ate_rmse"),
                        "rpe_translation_rmse_m": metrics.get(
                            "rpe_translation_rmse"
                        ),
                        "rpe_rotation_deg_rmse": metrics.get(
                            "rpe_rotation_deg_rmse"
                        ),
                        "valid_pose_ratio": metrics.get("valid_pose_ratio"),
                        "valid_pose_frames": metrics.get("valid_pose_frames"),
                        "lost_events": metrics.get("lost_events"),
                        "mean_latency_ms": metrics.get("mean_latency_ms"),
                        "p95_latency_ms": metrics.get("p95_latency_ms"),
                    }
                )

    result_root = root / "results/A"
    fieldnames = []
    for row in rows:
        for field in row:
            if field not in fieldnames:
                fieldnames.append(field)
    with (result_root / "all_sequences_metrics.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    (result_root / "all_sequences_metrics.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    aggregate = []
    for sequence in matrix["sequences"]:
        for mode in MODES:
            selected = [
                row
                for row in rows
                if row["sample_id"] == sequence["id"] and row["mode"] == mode
            ]
            valid = [row for row in selected if row["status"] == "ok"]
            item = {
                "sample_id": sequence["id"],
                "difficulty": sequence["difficulty"],
                "trajectory": sequence["trajectory"],
                "start_frame": sequence["start_frame"],
                "mode": mode,
                "run_count": len(selected),
                "metric_ok_count": len(valid),
            }
            for field in (
                "ate_rmse_m",
                "rpe_translation_rmse_m",
                "rpe_rotation_deg_rmse",
                "valid_pose_ratio",
                "lost_events",
                "mean_latency_ms",
                "p95_latency_ms",
            ):
                source = valid if field in {
                    "ate_rmse_m",
                    "rpe_translation_rmse_m",
                    "rpe_rotation_deg_rmse",
                } else selected
                values = np.asarray(
                    [
                        float(row[field])
                        for row in source
                        if row.get(field) is not None
                    ],
                    dtype=float,
                )
                item[f"{field}_mean"] = (
                    float(values.mean()) if len(values) else None
                )
                item[f"{field}_std"] = (
                    float(values.std(ddof=1)) if len(values) > 1 else 0.0
                )
            aggregate.append(item)

    with (result_root / "all_sequences_aggregate.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(aggregate[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(aggregate)
    (result_root / "all_sequences_aggregate.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result_root / "all_sequences_metrics.csv")
    print(result_root / "all_sequences_aggregate.csv")


if __name__ == "__main__":
    main()
