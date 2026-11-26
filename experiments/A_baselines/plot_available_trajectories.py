#!/usr/bin/env python3
"""Create representative trajectory plots for all available sequences."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import yaml

from evo.core import sync
from evo.core.trajectory import PoseTrajectory3D
from evo.tools import file_interface


MODES = ("rgb", "rgb_imu", "rgbd_imu")
SEEDS = (0, 1, 2)


def read_tracking(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def segments(rows: list[dict[str, str]]) -> list[list[dict[str, str]]]:
    groups = []
    current = []
    map_id = None
    for row in rows:
        valid = row["valid"] == "1" and int(row["map_id"]) >= 0
        candidate_map = int(row["map_id"]) if valid else None
        if valid and (map_id is None or candidate_map == map_id):
            current.append(row)
            map_id = candidate_map
        else:
            if current:
                groups.append(current)
            current = [row] if valid else []
            map_id = candidate_map
    if current:
        groups.append(current)
    return groups


def slice_traj(
    trajectory: PoseTrajectory3D, start: float, end: float
) -> PoseTrajectory3D:
    mask = (
        (trajectory.timestamps >= start - 1e-6)
        & (trajectory.timestamps <= end + 1e-6)
    )
    return PoseTrajectory3D(
        trajectory.positions_xyz[mask],
        trajectory.orientations_quat_wxyz[mask],
        trajectory.timestamps[mask],
    )


def representative(
    rows: list[dict[str, object]], run_root: Path, mode: str
) -> tuple[int, dict[str, object], Path]:
    selected = [row for row in rows if row["mode"] == mode]
    valid = [row for row in selected if row["status"] == "ok"]
    pool = valid or selected
    best = max(pool, key=lambda row: float(row["valid_pose_ratio"] or 0.0))
    return (
        int(best["seed"]),
        best,
        run_root / f"{mode}_seed{int(best['seed'])}",
    )


def plot_map_diagnostic(
    run_dir: Path, reference_path: Path, output: Path, title: str
) -> None:
    reference_full = file_interface.read_tum_trajectory_file(str(reference_path))
    estimated_full = file_interface.read_tum_trajectory_file(
        str(run_dir / "trajectory_frames.tum")
    )
    groups = segments(read_tracking(run_dir / "tracking.csv"))
    groups = [group for group in groups if len(group) >= 2]
    if not groups:
        raise ValueError(f"No plottable tracking segments in {run_dir}")

    columns = min(3, len(groups))
    rows = int(np.ceil(len(groups) / columns))
    figure, axes = plt.subplots(
        rows,
        columns,
        figsize=(5.6 * columns, 4.8 * rows),
        squeeze=False,
    )
    for axis, group in zip(axes.flat, groups, strict=False):
        start = float(group[0]["timestamp"])
        end = float(group[-1]["timestamp"])
        map_id = int(group[0]["map_id"])
        reference = slice_traj(reference_full, start, end)
        estimated = slice_traj(estimated_full, start, end)
        if len(reference.timestamps) and len(estimated.timestamps):
            try:
                reference, estimated = sync.associate_trajectories(
                    reference, estimated, max_diff=0.02
                )
            except Exception:
                pass
        axis.plot(
            reference.positions_xyz[:, 0],
            reference.positions_xyz[:, 1],
            color="#1f77b4",
            label="Ground truth",
        )
        axis.plot(
            estimated.positions_xyz[:, 0],
            estimated.positions_xyz[:, 1],
            color="#ff7f0e",
            label="Estimated",
        )
        axis.set_aspect("equal", adjustable="datalim")
        axis.set_title(f"Map {map_id}: {len(group)} tracked frames")
        axis.set_xlabel("x [m]")
        axis.set_ylabel("y [m]")
        axis.grid(True, alpha=0.3)
        axis.legend(loc="best")
    for axis in axes.flat[len(groups) :]:
        axis.axis("off")
    figure.suptitle(title + " (per-frame diagnostic by map)")
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=150)
    plt.close(figure)


def contact_sheet(
    entries: list[dict[str, object]], title: str, output: Path
) -> None:
    sequences = []
    for entry in entries:
        if entry["sample_id"] not in sequences:
            sequences.append(entry["sample_id"])
    figure, axes = plt.subplots(
        len(sequences), len(MODES), figsize=(18, 6 * len(sequences))
    )
    for row, sample_id in enumerate(sequences):
        for column, mode in enumerate(MODES):
            axis = axes[row, column]
            entry = next(
                item
                for item in entries
                if item["sample_id"] == sample_id and item["mode"] == mode
            )
            axis.imshow(mpimg.imread(entry["figure_path"]))
            axis.axis("off")
            axis.set_title(
                f"{sample_id} | {mode} | seed {entry['seed']} | "
                f"coverage {100 * float(entry['valid_pose_ratio']):.1f}%"
            )
    figure.suptitle(title)
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=145)
    plt.close(figure)


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
    metrics = json.loads(
        (root / "results/A/all_sequences_metrics.json").read_text(
            encoding="utf-8"
        )
    )
    output_root = root / "results/A/available_sequences/trajectories"
    output_root.mkdir(parents=True, exist_ok=True)
    entries = []

    for sequence in matrix["sequences"]:
        run_root = root / sequence["result_root"]
        reference = (
            root
            / "results/A/full_sequences/inputs"
            / sequence["id"]
            / "trajectory_gt.tum"
        )
        if not reference.exists():
            candidate = (
                root
                / "results/A/inputs_final/OldTownSummer"
                / sequence["difficulty"]
                / (
                    f"{sequence['trajectory']}_2p0s_9p9s"
                    if sequence["start_frame"] == 200
                    else f"{sequence['trajectory']}_start{sequence['start_frame']}"
                )
                / "trajectory_gt.tum"
            )
            if candidate.exists():
                reference = candidate
            elif sequence["id"] == "hard_P001":
                reference = (
                    root
                    / "results/A/inputs_final/OldTownSummer/hard/P001_start100"
                    / "trajectory_gt.tum"
                )
            elif sequence["id"] == "easy_P002":
                reference = (
                    root
                    / "results/A/validation/P002/easy/window_200_299"
                    / "trajectory_gt.tum"
                )
        sequence_rows = [
            row for row in metrics if row["sample_id"] == sequence["id"]
        ]
        for mode in MODES:
            seed, selected, run_dir = representative(
                sequence_rows, run_root, mode
            )
            output = output_root / f"{sequence['id']}_{mode}.png"
            overlay = run_dir / "trajectory_overlay.png"
            if selected["status"] == "ok" and overlay.exists():
                shutil.copy2(overlay, output)
                plot_type = "primary_optimized_keyframe"
            else:
                plot_map_diagnostic(
                    run_dir,
                    reference,
                    output,
                    f"{sequence['id']} {mode} seed {seed}",
                )
                plot_type = "per_frame_by_map_diagnostic"
            entries.append(
                {
                    "sample_id": sequence["id"],
                    "difficulty": sequence["difficulty"],
                    "trajectory": sequence["trajectory"],
                    "mode": mode,
                    "seed": seed,
                    "status": selected["status"],
                    "valid_pose_ratio": selected["valid_pose_ratio"],
                    "plot_type": plot_type,
                    "figure_path": str(output),
                }
            )

    manifest = root / "results/A/available_sequence_trajectory_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(entries[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(entries)

    for difficulty in ("easy", "hard"):
        contact_sheet(
            [entry for entry in entries if entry["difficulty"] == difficulty],
            f"Available {difficulty} trajectories: 3 sequences x 3 modes",
            root / f"results/A/figures/{difficulty}_available_trajectories.png",
        )
    print(manifest)


if __name__ == "__main__":
    main()
