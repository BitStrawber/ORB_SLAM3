#!/usr/bin/env bash
set -euo pipefail

source /media/SSD0/XCX/ORB_SLAM3_A/activate_a_orb.sh

root="${A_ROOT}"
python_bin="${root}/conda_envs/a_orb/bin/python"
runner="${root}/build/A_baselines/run_tartanair"
vocab="${root}/repos/ORB_SLAM3/Vocabulary/ORBvoc.txt"
settings="${root}/configs/A/tartanair.yaml"

for difficulty in easy hard; do
  sequence="${root}/data/TartanAirV2/OldTownSummer/Data_${difficulty}/P000"
  inputs="${root}/results/A/inputs_final/OldTownSummer/${difficulty}/P000_2p0s_9p9s"

  if [[ ! -f "${inputs}/manifest.csv" ]]; then
    "${python_bin}" "${root}/experiments/A_baselines/prepare_sequence.py" \
      --sequence-root "${sequence}" \
      --start-frame 200 \
      --num-frames 100 \
      --output "${inputs}"
  fi

  for mode in rgb rgb_imu rgbd_imu; do
    for seed in 0 1 2; do
      run_dir="${root}/results/A/baseline_final/${difficulty}/P000_window_200_299/${mode}_seed${seed}"
      if [[ -f "${run_dir}/metrics.json" ]]; then
        echo "SKIP ${difficulty} ${mode} ${seed}"
        continue
      fi

      "${python_bin}" "${root}/experiments/A_baselines/run_baseline.py" \
        --binary "${runner}" \
        --vocab "${vocab}" \
        --settings "${settings}" \
        --mode "${mode}" \
        --manifest "${inputs}/manifest.csv" \
        --imu "${inputs}/imu.csv" \
        --output "${run_dir}" \
        --seed "${seed}" \
        --orb-root "${root}/repos/ORB_SLAM3"

      if [[ "${mode}" == "rgb" ]]; then
        alignment="sim3"
      else
        alignment="se3"
      fi

      "${python_bin}" "${root}/experiments/A_baselines/evaluate_run.py" \
        --estimated "${run_dir}/trajectory_est.tum" \
        --reference "${inputs}/trajectory_gt.tum" \
        --tracking "${run_dir}/tracking.csv" \
        --output "${run_dir}/metrics.json" \
        --alignment "${alignment}" \
        --plot "${run_dir}/trajectory_overlay.png"
    done
  done
done

"${python_bin}" "${root}/experiments/A_baselines/summarize_baseline.py"
