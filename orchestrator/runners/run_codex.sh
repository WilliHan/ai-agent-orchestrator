#!/bin/bash

if [ -z "$1" ]; then
  echo "Error: RUN_DIR argument is missing."
  echo "Usage: $0 <RUN_DIR>"
  exit 1
fi

RUN_DIR="$1"
PROMPT_FILE="$RUN_DIR/codex_prompt.md"
LOG_FILE="$RUN_DIR/codex_output.log"

# Ensure output directory exists
mkdir -p "$RUN_DIR"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "오류: 프롬프트 파일 $PROMPT_FILE을 찾을 수 없습니다." | tee -a "$LOG_FILE"
  exit 1
fi

# Check if 'codex' command is installed
if ! command -v codex &> /dev/null; then
  echo "오류: 'codex' 명령어가 설치되어 있지 않거나 PATH에 존재하지 않습니다." | tee -a "$LOG_FILE"
  exit 127
fi

echo "[$(date)] Starting Codex Execution..." | tee -a "$LOG_FILE"
codex < "$PROMPT_FILE" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "[$(date)] Codex Execution Finished with exit code: $EXIT_CODE" | tee -a "$LOG_FILE"
exit $EXIT_CODE
