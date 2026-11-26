#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel)"
if [[ -z "${A_ROOT:-}" ]]; then
  A_ROOT="$(cd "${REPO_ROOT}/../.." && pwd)"
  export A_ROOT
fi
source "${REPO_ROOT}/scripts/A/activate_a_orb.sh"

root="${A_ROOT}"
python_bin="${A_CONDA_ENV}/bin/python"
runner="${root}/build/A_baselines/run_tartanair"
vocab="${REPO_ROOT}/Vocabulary/ORBvoc.txt"
settings="${REPO_ROOT}/configs/A/tartanair.yaml"
output_root="${A_OUTPUT_ROOT:-${REPO_ROOT}/results/A}"
data_root="${TARTANAIR_ROOT:-${root}/data/TartanAirV2}"

for difficulty in easy hard; do
  sequence="${data_root}/OldTownSummer/Data_${difficulty}/P000"
  inputs="${output_root}/inputs_final/OldTownSummer/${difficulty}/P000_2p0s_9p9s"

  if [[ ! -f "${inputs}/manifest.csv" ]]; then
    "${python_bin}" "${root}/experiments/A_baselines/prepare_sequence.py" \
      --sequence-root "${sequence}" \
      --start-frame 200 \
      --num-frames 100 \
      --output "${inputs}"
  fi

  for mode in rgb rgb_imu rgbd_imu; do
    for seed in 0 1 2; do
      run_dir="${output_root}/baseline_final/${difficulty}/P000_window_200_299/${mode}_seed${seed}"
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
      run_status=$?
      echo "RUN ${difficulty} ${mode} ${seed}: exit=${run_status}"
      if [[ ${run_status} -ne 0 && ! -s "${run_dir}/trajectory_est.tum" ]]; then
        printf '{"status":"failed","error":"runner exit %s and no trajectory"}\n' \
          "${run_status}" > "${run_dir}/metrics.json"
        continue
      fi

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
      echo "EVAL ${difficulty} ${mode} ${seed}: exit=$?"
    done
  done
done

"${python_bin}" "${REPO_ROOT}/experiments/A_baselines/summarize_baseline.py" \
  --root "${REPO_ROOT}"
