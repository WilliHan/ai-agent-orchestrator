#!/bin/bash

if [ -z "$1" ]; then
  echo "오류: RUN_DIR 인자가 누락되었습니다."
  echo "사용법: $0 <RUN_DIR> [--dry-run]"
  exit 1
fi

RUN_DIR="$1"
DRY_RUN_MODE=false

if [ "$2" == "--dry-run" ]; then
  DRY_RUN_MODE=true
fi

LOG_FILE="$RUN_DIR/smoke_result.log"
mkdir -p "$RUN_DIR"

echo "[$(date)] 스모크 테스트 검증 시작..." > "$LOG_FILE"

# dry-run인 경우 스킵 처리
if [ "$DRY_RUN_MODE" = true ]; then
  echo "상태: SKIPPED" >> "$LOG_FILE"
  echo "사유: dry-run 모드에서는 실제 보고서 산출물을 생성하지 않으므로 smoke test를 건너뜀" >> "$LOG_FILE"
  echo "결과: SKIPPED" | tee -a "$LOG_FILE"
  exit 0
fi

# 실제 실행 모드
# 실제 smoke test 명령 후보 파일 검사
SMOKE_CMD=""
if [ -f "tools/run_system_diagnostic.sh" ]; then
  SMOKE_CMD="bash tools/run_system_diagnostic.sh"
elif [ -f "scripts/smoke_test.sh" ]; then
  SMOKE_CMD="bash scripts/smoke_test.sh"
fi

if [ -n "$SMOKE_CMD" ]; then
  echo "발견된 스모크 테스트 명령어: $SMOKE_CMD" | tee -a "$LOG_FILE"
  set +e
  $SMOKE_CMD >> "$LOG_FILE" 2>&1
  EXIT_CODE=$?
  set -e
  
  if [ $EXIT_CODE -eq 0 ]; then
    echo "상태: PASSED" >> "$LOG_FILE"
    echo "사유: 실제 스모크 테스트 명령이 실행되었고 성공함" >> "$LOG_FILE"
    echo "[$(date)] 스모크 테스트 완료 (상태: PASSED)" | tee -a "$LOG_FILE"
    exit 0
  else
    echo "상태: FAILED" >> "$LOG_FILE"
    echo "사유: 실제 스모크 테스트 명령이 실행되었고 실패함 (Exit Code: $EXIT_CODE)" >> "$LOG_FILE"
    echo "[$(date)] 스모크 테스트 완료 (상태: FAILED, Exit Code: $EXIT_CODE)" | tee -a "$LOG_FILE"
    exit 1
  fi
else
  echo "상태: SKIPPED" >> "$LOG_FILE"
  echo "사유: 프로젝트 내에 명확한 스모크 테스트 스크립트나 명령어가 정의되어 있지 않아 스킵합니다." >> "$LOG_FILE"
  echo "결과: SKIPPED" | tee -a "$LOG_FILE"
  exit 0
fi
