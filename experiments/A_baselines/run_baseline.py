#!/usr/bin/env python3
"""Execute one headless ORB-SLAM3 TartanAir baseline run."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def git_head(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def materialize_orb_trajectory(
    output: Path, settings: Path, mode: str
) -> str:
    raw_path = output / "trajectory_orb_raw.tum"
    if not raw_path.exists() or raw_path.stat().st_size == 0:
        return "per_frame_fallback_empty_official"
    rows = np.loadtxt(raw_path, ndmin=2)
    if rows.size == 0:
        return "per_frame_fallback_empty_official"
    # The official EuRoC save path is the authoritative optimized trajectory
    # for inertial modes. For monocular RGB, keep the per-frame trajectory
    # already transformed to the TartanAir body frame by run_tartanair.
    if mode == "rgb":
        return "per_frame_body"
    if np.median(rows[:, 0]) > 1e6:
        rows[:, 0] /= 1e9
    if rows.shape[0] < 3:
        return "per_frame_fallback_degenerate_official"
    covariance_rank = np.linalg.matrix_rank(
        np.cov(rows[:, 1:4], rowvar=False)
    )
    if covariance_rank < 2:
        return "per_frame_fallback_degenerate_official"

    np.savetxt(
        output / "trajectory_est.tum",
        rows,
        fmt="%.17g",
        delimiter=" ",
    )
    return "orb_save_largest_map"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--vocab", required=True, type=Path)
    parser.add_argument("--settings", required=True, type=Path)
    parser.add_argument(
        "--mode", required=True, choices=["rgb", "rgb_imu", "rgbd_imu"]
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--imu", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--orb-root", required=True, type=Path)
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing run directory: {output}")
    output.mkdir(parents=True)

    shutil.copy2(args.settings, output / "settings_snapshot.yaml")
    shutil.copy2(args.manifest, output / "manifest_snapshot.csv")
    shutil.copy2(args.imu, output / "imu_snapshot.csv")

    command = [
        str(args.binary.resolve()),
        str(args.vocab.resolve()),
        str(args.settings.resolve()),
        args.mode,
        str(args.manifest.resolve()),
        str(args.imu.resolve()),
        str(output),
        str(args.seed),
    ]
    meta = {
        "command": command,
        "mode": args.mode,
        "seed": args.seed,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "cwd": str(Path.cwd()),
        "git_commit": git_head(args.orb_root),
        "environment": {
            key: os.environ.get(key)
            for key in [
                "CONDA_PREFIX",
                "CMAKE_PREFIX_PATH",
                "LD_LIBRARY_PATH",
                "CPATH",
                "TMPDIR",
            ]
        },
    }

    with (output / "run.log").open("w", encoding="utf-8") as log:
        log.write("COMMAND=" + json.dumps(command) + "\n")
        log.flush()
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            log.write(line)
        return_code = process.wait()

    meta["return_code"] = return_code
    meta["finished_utc"] = datetime.now(timezone.utc).isoformat()
    meta["status"] = "ok" if return_code == 0 else "failed"
    meta["trajectory_source"] = materialize_orb_trajectory(
        output, args.settings.resolve(), args.mode
    )
    (output / "run_meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
