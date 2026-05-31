# Phase 7 최종 운영 가이드

## 목적
사용자(개발자/운영자)는 복잡한 내부 동작을 알 필요 없이 오직 **요구사항만 입력**하고 **최종 요약 보고서(`operation_summary.md`)만 확인**하여 신속히 합격 여부를 판단합니다.

## 기본 운영 명령 (Auto-run)

```bash
.venv/bin/python orchestrator/run_task.py \
  --task-type auto \
  --auto-run \
  --requirement "요구사항 설명"
```

## 안전한 dry-run 명령 (가상 실행 및 사전 검증)

```bash
.venv/bin/python orchestrator/run_task.py \
  --task-type auto \
  --auto-run \
  --dry-run \
  --requirement "요구사항 설명"
```

## 결과 확인 및 산출물 파일
각 실행의 결과는 `orchestrator/runs/{TASK_ID}/` 디렉토리 하위에 다음과 같이 기록됩니다.
- **operation_summary.md**: 최종 요약 보고서 (가장 먼저 확인)
- **final_report.md**: 상세 보고서 (선택된 에이전트 정보, 세부 검증 로그 수록)
- **failure_report.md**: 에이전트 실패 혹은 검증 실패 시 생성되는 정밀 트러블슈팅 가이드
- **state.md**: 태스크 진행 및 Handoff 상태 관리 마크다운
- **task_classification.log**: 태스크 유형 및 가중치 자동 분류 추론 기록
- **agent_selection.log**: 라우터의 에이전트 배정 및 제외 사유 기록

## 사용자가 주로 확인해야 할 3대 파일
1. **`operation_summary.md`**: 합격 여부(PASS/FAIL) 및 요약 결과
2. **`final_report.md`**: 작업의 세부 내용 검토 필요 시 확인
3. **`failure_report.md`**: 에러 혹은 검증 실패 시 수동 조치를 위해 확인

## 판정 결과에 따른 후속 조치
- **PASS 일 때**: 모든 자동화 검증을 통과했습니다. **다음 단계 진행 가능**.
- **WARNING 일 때**: Antigravity 독립 리뷰 실행 과정에 경고가 감지되었습니다. **보고서를 체티(Cheeti)에게 전달하여 검토를 권장**합니다.
- **FAIL 또는 NEEDS_HUMAN_REVIEW 일 때**: 에이전트 실행 실패 또는 심각한 검증 에러가 있습니다. **수동 판단이 필요하며, failure_report.md를 참고하여 조치하고 보고서를 체티에게 전달**하십시오.

## 절대 금지 사항 (Forbidden Rules)
- `.env` 수정 금지
- `analysis.db` 수정 및 삭제 금지
- `reports/` 하위 과거 산출물 및 이력 데이터 삭제/수정 금지
- `rm`, `rm -rf`, `find -delete` 등 위험 삭제 명령 실행 금지
- `git reset --hard` 및 `git clean -fdx` 금지
- `sudo` 및 `chmod -R 777` 등 권한 승격 명령 금지
- 패키지 임의 설치 금지
- `git commit`, `push`, `merge` 등 형상 관리 영구 변경 명령 임의 실행 금지

## 리뷰·검토 3대 관점 (Mandatory Review Viewpoints)
모든 검증 및 Antigravity 리뷰는 아래 3대 관점을 필수로 유지하여 수행됩니다.
1. **Red Teaming 검토 (적대적 관점)**: 설계 취약점, 우회 경로, 위험한 가정, 왜곡 신호 오발동 가능성을 진단.
2. **Negative Testing / Review (부정·예외 방어적 관점)**: Null/None, Type Mismatch, Zero Division, 인프라 에러 및 파일 부재 등에 대한 예외 처리를 검증.
3. **Stress Testing & Resilience Review (부하·복원력 관점)**: 대량 데이터 처리 성능, 장애 복구, 부분 재실행, Agent handoff, 디스크/로그 누적에 대한 복원력을 평가.
