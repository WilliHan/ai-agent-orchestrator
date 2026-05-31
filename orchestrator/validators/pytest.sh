#!/bin/bash

if [ -z "$1" ]; then
  echo "Error: RUN_DIR argument is missing."
  echo "Usage: $0 <RUN_DIR>"
  exit 1
fi

RUN_DIR="$1"
LOG_FILE="$RUN_DIR/test_result.log"

mkdir -p "$RUN_DIR"

echo "[$(date)] Starting pytest validation..." | tee "$LOG_FILE"

# Run pytest. We preserve the PYTHONPATH as 'src' if needed, or run directly.
# Run pytest using local virtual environment to avoid global dependency
if [ -f ".venv/bin/python" ]; then
  PYTEST_CMD=".venv/bin/python -m pytest"
elif [ -f "../.venv/bin/python" ]; then
  PYTEST_CMD="../.venv/bin/python -m pytest"
else
  echo "Error: Local .venv/bin/python not found. Please setup local virtualenv." | tee -a "$LOG_FILE"
  exit 1
fi

set +e
$PYTEST_CMD > >(tee -a "$LOG_FILE") 2>&1
EXIT_CODE=$?
set -e

echo "[$(date)] pytest finished with exit code: $EXIT_CODE" | tee -a "$LOG_FILE"
exit $EXIT_CODE
