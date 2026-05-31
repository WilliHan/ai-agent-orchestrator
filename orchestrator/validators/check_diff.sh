#!/bin/bash

if [ -z "$1" ]; then
  echo "Error: RUN_DIR argument is missing."
  echo "Usage: $0 <RUN_DIR>"
  exit 1
fi

RUN_DIR="$1"

mkdir -p "$RUN_DIR"

echo "Collecting git diff and status information..."

# Save git status --short
git status --short > "$RUN_DIR/git_status.txt" 2>&1 || true

# Save git diff --stat
git diff --stat > "$RUN_DIR/diff_stat.txt" 2>&1 || true

# Save git diff (full patch)
git diff > "$RUN_DIR/full_diff.patch" 2>&1 || true

echo "Git diff info successfully saved to $RUN_DIR"
