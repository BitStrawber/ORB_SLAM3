#!/usr/bin/env python3
"""Evaluate hard runs over one identical, single-map two-second window."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from evo.core import metrics, sync
from evo.core.trajectory import PoseTrajectory3D
from evo.tools import file_interface


MODES = ("rgb", "rgb_imu", "rgbd_imu")
START = 20.0
END = 22.0


def slice_trajectory(traj: PoseTrajectory3D, start: float, end: float) -> PoseTrajectory3D:
    mask = (traj.timestamps >= start - 1e-9) & (traj.timestamps <= end + 1e-9)
    return PoseTrajectory3D(
        traj.positions_xyz[mask],
        traj.orientations_quat_wxyz[mask],
        traj.timestamps[mask],
    )


def tracking_window(path: Path) -> tuple[list[dict[str, str]], dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    window = [row for row in rows if START - 1e-9 <= float(row["timestamp"]) <= END + 1e-9]
    valid = [row for row in window if row["valid"] == "1"]
    maps = sorted({int(row["map_id"]) for row in valid if int(row["map_id"]) >= 0})
    lost = sum(row["valid"] != "1" for row in window)
    return window, {
        "window_frames": len(window),
        "valid_window_frames": len(valid),
        "valid_pose_ratio": len(valid) / len(window) if window else 0.0,
        "lost_window_frames": lost,
        "map_ids": maps,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    run_root = root / "results/A/baseline_final/hard/P000_window_200_299"
    input_root = root / "results/A/inputs_final/OldTownSummer/hard/P000_2p0s_9p9s"
    result_root = root / "results/A"
    (result_root / "figures").mkdir(parents=True, exist_ok=True)

    reference_full = file_interface.read_tum_trajectory_file(
        str(input_root / "trajectory_gt.tum")
    )
    reference_window = slice_trajectory(reference_full, START, END)
    rows = []
    for mode in MODES:
        for seed in (0, 1, 2):
            run_dir = run_root / f"{mode}_seed{seed}"
            _, tracking = tracking_window(run_dir / "tracking.csv")
            if len(tracking["map_ids"]) != 1:
                raise RuntimeError(
                    f"{mode} seed {seed} does not have one map in {START}-{END}: "
                    f"{tracking['map_ids']}"
                )
            estimated = file_interface.read_tum_trajectory_file(
                str(run_dir / "trajectory_frames.tum")
            )
            estimated = slice_trajectory(estimated, START, END)
            reference, estimated = sync.associate_trajectories(
                reference_window, estimated, max_diff=0.02
            )
            estimated.align(
                reference,
                correct_scale=mode == "rgb",
                correct_only_scale=False,
            )
            ape = metrics.APE(metrics.PoseRelation.translation_part)
            ape.process_data((reference, estimated))
            orientation = metrics.APE(metrics.PoseRelation.rotation_angle_deg)
            orientation.process_data((reference, estimated))
            rpe_t = metrics.RPE(
                metrics.PoseRelation.translation_part, 5, metrics.Unit.frames
            )
            rpe_t.process_data((reference, estimated))
            rpe_r = metrics.RPE(
                metrics.PoseRelation.rotation_angle_deg, 5, metrics.Unit.frames
            )
            rpe_r.process_data((reference, estimated))
            result = {
                "dataset": "TartanAirV2",
                "environment": "OldTownSummer",
                "trajectory": "P000",
                "difficulty": "hard",
                "mode": mode,
                "seed": seed,
                "evaluation_type": "common_window_dense_body_trajectory",
                "status": "ok",
                "window_start_s": START,
                "window_end_s": END,
                "map_id": tracking["map_ids"][0],
                "matched_pose_frames": len(reference.timestamps),
                "valid_window_frames": tracking["valid_window_frames"],
                "valid_pose_ratio": tracking["valid_pose_ratio"],
                "lost_window_frames": tracking["lost_window_frames"],
                "ate_rmse_m": float(ape.get_result().stats["rmse"]),
                "orientation_ape_rmse_deg": float(
                    orientation.get_result().stats["rmse"]
                ),
                "rpe_delta_frames": 5,
                "rpe_translation_rmse_m": float(
                    rpe_t.get_result().stats["rmse"]
                ),
                "rpe_rotation_deg_rmse": float(rpe_r.get_result().stats["rmse"]),
            }
            rows.append(result)
            (run_dir / "metrics_common_hard.json").write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            if mode == "rgb":
                label = f"rgb seed {seed}"
            else:
                label = f"{mode} seed {seed}"
            print(label, result["ate_rmse_m"])

    csv_path = result_root / "hard_common_metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (result_root / "hard_common_metrics.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    aggregate = []
    means = []
    stds = []
    for mode in MODES:
        selected = [row for row in rows if row["mode"] == mode]
        item = {"mode": mode, "seed_count": len(selected)}
        for field in [
            "ate_rmse_m",
            "orientation_ape_rmse_deg",
            "rpe_translation_rmse_m",
            "rpe_rotation_deg_rmse",
            "valid_pose_ratio",
            "lost_window_frames",
        ]:
            values = np.asarray([row[field] for row in selected], dtype=float)
            item[f"{field}_mean"] = float(values.mean())
            item[f"{field}_std"] = float(values.std(ddof=1))
        aggregate.append(item)
        means.append(item["ate_rmse_m_mean"])
        stds.append(item["ate_rmse_m_std"])
    aggregate_csv = result_root / "hard_common_aggregate.csv"
    with aggregate_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(aggregate[0]))
        writer.writeheader()
        writer.writerows(aggregate)
    (result_root / "hard_common_aggregate.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    x = np.arange(len(MODES))
    means_array = np.asarray(means)
    stds_array = np.asarray(stds)
    fig, axis = plt.subplots(figsize=(7, 5))
    axis.bar(
        x,
        means_array,
        yerr=np.vstack([np.minimum(means_array, stds_array), stds_array]),
        capsize=4,
        color=["#4C78A8", "#F58518", "#54A24B"],
    )
    axis.set_xticks(x, MODES)
    axis.set_ylabel("ATE RMSE [m]")
    axis.set_title("Hard P000: common 20.0-22.0 s dense window")
    axis.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(result_root / "figures/hard_common_window.png", dpi=170)
    plt.close(fig)
    print(csv_path)
    print(aggregate_csv)


if __name__ == "__main__":
    main()
