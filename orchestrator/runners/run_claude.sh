#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Error: RUN_DIR argument is missing."
  echo "Usage: $0 <RUN_DIR>"
  exit 1
fi

RUN_DIR="$1"
PROMPT_FILE="$RUN_DIR/claude_prompt.md"
LOG_FILE="$RUN_DIR/claude_output.log"

# Ensure output directory exists
mkdir -p "$RUN_DIR"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: Prompt file $PROMPT_FILE not found." | tee -a "$LOG_FILE"
  exit 1
fi

# Check if 'claude' command is installed
if ! command -v claude &> /dev/null; then
  echo "Error: 'claude' command is not installed or not in PATH." | tee -a "$LOG_FILE"
  exit 127
fi

echo "[$(date)] Starting Claude Execution..." | tee -a "$LOG_FILE"
# Running claude in non-interactive or input-redirected mode
# Note: Since claude code runner might run interactively, we pass the prompt via stdin
set +e
claude < "$PROMPT_FILE" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
set -e

echo "[$(date)] Claude Execution Finished with exit code: $EXIT_CODE" | tee -a "$LOG_FILE"
exit $EXIT_CODE
