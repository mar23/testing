#!/usr/bin/env bash
set -euo pipefail

# Paste this file into LEXIS Data Management -> Job Scripts.
# Relative input/output paths are relative to the HPC job directory.
JOB_DIR="$PWD"
REPO_URL="${REPO_URL:-https://github.com/mar23/testing.git}"
REVISION="${1:-${REPO_REVISION:-ae4f9b326353159cf78612e5ace9b20ba242f455}}"
INPUT_DATASET="${INPUT_DATASET:-input/benchmark_dataset.csv}"
case "$INPUT_DATASET" in
    /*) ;;
    *) INPUT_DATASET="$JOB_DIR/$INPUT_DATASET" ;;
esac

# LEXIS stages each input dataset into input/<dataset name>/, so look there too.
if [[ ! -r "$INPUT_DATASET" && -d "$JOB_DIR/input" ]]; then
    found="$(find "$JOB_DIR/input" -type f -name "$(basename "$INPUT_DATASET")" | head -n 1)"
    [[ -n "$found" ]] && INPUT_DATASET="$found"
fi
echo "Input dataset: $INPUT_DATASET"

for command in git python3; do
    command -v "$command" >/dev/null || { echo "Missing command: $command" >&2; exit 1; }
done
[[ -r "$INPUT_DATASET" ]] || { echo "Cannot read dataset: $INPUT_DATASET" >&2; exit 1; }

mkdir -p "$JOB_DIR/output"
WORK_DIR="$(mktemp -d "$JOB_DIR/benchmark-work.XXXXXX")"
echo "Cloning $REPO_URL at $REVISION"
git clone -- "$REPO_URL" "$WORK_DIR/repo_code"
git -C "$WORK_DIR/repo_code" checkout --detach "$REVISION"
git -C "$WORK_DIR/repo_code" rev-parse HEAD > "$JOB_DIR/output/commit.txt"

# The public Python revision expects ../datasets/benchmark_dataset.csv
# relative to its working directory. Keep that path available.
mkdir -p "$WORK_DIR/datasets"
ln -s "$INPUT_DATASET" "$WORK_DIR/datasets/benchmark_dataset.csv"
cd "$WORK_DIR/repo_code"
[[ -f src/sum_dataset.py ]] || { echo "Missing src/sum_dataset.py" >&2; exit 1; }
python3 src/sum_dataset.py "$INPUT_DATASET" 2>&1 | tee "$JOB_DIR/output/result.txt"
# The public script prints errors but still exits 0, so check its output.
grep -q "^Celkový součet:" "$JOB_DIR/output/result.txt" || { echo "sum_dataset.py did not produce a result" >&2; exit 1; }
echo "Job completed; results: $JOB_DIR/output"
