#!/usr/bin/env python3
"""Evaluate one A baseline run with evo and write JSON plus a trajectory plot."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from evo.core import metrics, sync
from evo.core.trajectory import PoseTrajectory3D
from evo.tools import file_interface


def read_tracking(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def tracking_summary(path: Path) -> dict[str, float | int]:
    rows = read_tracking(path)
    valid = [row["valid"] == "1" for row in rows]
    latency = [
        float(row["latency_ms"])
        for row in rows
        if row.get("latency_ms") not in (None, "", "NA")
    ]
    lost_events = 0
    seen_valid = False
    in_loss = False
    for is_valid in valid:
        if is_valid:
            seen_valid = True
            in_loss = False
        elif seen_valid and not in_loss:
            lost_events += 1
            in_loss = True
    return {
        "input_frames": len(rows),
        "valid_pose_frames": sum(valid),
        "valid_pose_ratio": sum(valid) / len(rows) if rows else 0.0,
        "lost_events": lost_events,
        "mean_latency_ms": float(np.mean(latency)) if latency else math.nan,
        "p95_latency_ms": float(np.percentile(latency, 95)) if latency else math.nan,
    }


def largest_map_window(path: Path) -> dict[str, float | int] | None:
    rows = read_tracking(path)
    if not rows or "map_id" not in rows[0]:
        return None
    valid_rows = [
        row
        for row in rows
        if row.get("valid") == "1" and int(row.get("map_id", "-1")) >= 0
    ]
    if not valid_rows:
        return None
    counts = Counter(int(row["map_id"]) for row in valid_rows)
    map_id, count = counts.most_common(1)[0]
    map_rows = [row for row in valid_rows if int(row["map_id"]) == map_id]
    return {
        "map_id": map_id,
        "map_ids": sorted(counts),
        "valid_rows": count,
        "start": float(map_rows[0]["timestamp"]),
        "end": float(map_rows[-1]["timestamp"]),
    }


def slice_trajectory(traj: PoseTrajectory3D, start: float, end: float) -> PoseTrajectory3D:
    mask = (traj.timestamps >= start - 1e-9) & (traj.timestamps <= end + 1e-9)
    return PoseTrajectory3D(
        traj.positions_xyz[mask],
        traj.orientations_quat_wxyz[mask],
        traj.timestamps[mask],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--estimated", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--tracking", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--alignment", required=True, choices=["sim3", "se3"]
    )
    parser.add_argument("--max-time-diff", default=0.02, type=float)
    parser.add_argument("--rpe-delta", default=1.0, type=float)
    parser.add_argument(
        "--rpe-unit", choices=["frames", "meters"], default="meters"
    )
    parser.add_argument("--plot", type=Path)
    parser.add_argument(
        "--map-segment", choices=["fixed", "largest", "all"], default="fixed"
    )
    args = parser.parse_args()

    result: dict[str, object] = {
        "alignment": args.alignment,
        "rpe_delta": args.rpe_delta,
        "rpe_delta_unit": args.rpe_unit,
    }
    try:
        result.update(tracking_summary(args.tracking))
        reference = file_interface.read_tum_trajectory_file(str(args.reference))
        estimated = file_interface.read_tum_trajectory_file(str(args.estimated))
        map_window = largest_map_window(args.tracking)
        result["map_ids_in_valid_tracking"] = (
            map_window["map_ids"] if map_window else []
        )
        if (
            map_window
            and args.map_segment == "fixed"
            and len(map_window["map_ids"]) > 1
        ):
            result.update(
                {
                    "status": "invalid_map_discontinuity",
                    "error": (
                        "Multiple maps are active in the fixed evaluation window; "
                        "ATE/RPE would mix incompatible coordinate frames."
                    ),
                }
            )
        else:
            if map_window and args.map_segment == "largest":
                reference = slice_trajectory(
                    reference, float(map_window["start"]), float(map_window["end"])
                )
                estimated = slice_trajectory(
                    estimated, float(map_window["start"]), float(map_window["end"])
                )
                result["evaluated_map_id"] = map_window["map_id"]
                result["evaluated_map_valid_rows"] = map_window["valid_rows"]
                result["evaluated_window_start"] = map_window["start"]
                result["evaluated_window_end"] = map_window["end"]
            else:
                result["evaluated_window_start"] = float(reference.timestamps[0])
                result["evaluated_window_end"] = float(reference.timestamps[-1])

            reference = slice_trajectory(
                reference,
                float(result["evaluated_window_start"]),
                float(result["evaluated_window_end"]),
            )
            estimated = slice_trajectory(
                estimated,
                float(result["evaluated_window_start"]),
                float(result["evaluated_window_end"]),
            )
            reference, estimated = sync.associate_trajectories(
                reference, estimated, max_diff=args.max_time_diff
            )
            estimated.align(
                reference,
                correct_scale=args.alignment == "sim3",
                correct_only_scale=False,
            )

            ape = metrics.APE(metrics.PoseRelation.translation_part)
            ape.process_data((reference, estimated))
            ape_result = ape.get_result()

            orientation_ape = metrics.APE(metrics.PoseRelation.rotation_angle_deg)
            orientation_ape.process_data((reference, estimated))
            orientation_ape_result = orientation_ape.get_result()

            rpe_translation = metrics.RPE(
                metrics.PoseRelation.translation_part,
                args.rpe_delta,
                metrics.Unit.meters
                if args.rpe_unit == "meters"
                else metrics.Unit.frames,
            )
            rpe_translation.process_data((reference, estimated))
            translation_result = rpe_translation.get_result()

            rpe_rotation = metrics.RPE(
                metrics.PoseRelation.rotation_angle_deg,
                args.rpe_delta,
                metrics.Unit.meters
                if args.rpe_unit == "meters"
                else metrics.Unit.frames,
            )
            rpe_rotation.process_data((reference, estimated))
            rotation_result = rpe_rotation.get_result()

            result.update(
                {
                    "status": "ok",
                    "matched_pose_frames": len(reference.timestamps),
                    "ate_rmse": float(ape_result.stats["rmse"]),
                    "ate_mean": float(ape_result.stats["mean"]),
                    "ate_median": float(ape_result.stats["median"]),
                    "ate_std": float(ape_result.stats["std"]),
                    "orientation_ape_rmse_deg": float(
                        orientation_ape_result.stats["rmse"]
                    ),
                    "rpe_translation_rmse": float(
                        translation_result.stats["rmse"]
                    ),
                    "rpe_rotation_deg_rmse": float(rotation_result.stats["rmse"]),
                }
            )

        if args.plot and result.get("status") == "ok":
            positions_ref = reference.positions_xyz
            positions_est = estimated.positions_xyz
            fig = plt.figure(figsize=(7, 6))
            axis = fig.add_subplot(111)
            axis.plot(positions_ref[:, 0], positions_ref[:, 1], label="Ground truth")
            axis.plot(positions_est[:, 0], positions_est[:, 1], label="Estimated")
            axis.set_aspect("equal", adjustable="datalim")
            axis.set_xlabel("x [m]")
            axis.set_ylabel("y [m]")
            axis.set_title(f"TartanAir trajectory ({args.alignment} alignment)")
            axis.legend()
            axis.grid(True, alpha=0.3)
            fig.tight_layout()
            args.plot.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(args.plot, dpi=160)
            plt.close(fig)
    except Exception as error:
        result.update({"status": "failed", "error": f"{type(error).__name__}: {error}"})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return (
        0
        if result.get("status") in {"ok", "invalid_map_discontinuity"}
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
