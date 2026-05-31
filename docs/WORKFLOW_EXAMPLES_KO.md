# AI Agent Orchestrator 작업 예시 (상황별 레시피)

본 문서는 형님이 소프트웨어 개발 프로젝트를 일일 운영할 때 빈번히 마주하는 7가지 대표 상황을 가정하고, 오케스트레이터를 통해 문제를 기계적으로 안전하게 해결하는 실제 활용 시나리오입니다.

---

## 예시 1. README 문서 수정 (documentation 태스크)
- **언제 쓰는지**: README나 기획 문서에 운영 정책, 혹은 API 목록을 갱신하거나 보완 지시를 내리고 싶을 때 사용합니다.
- **사전 점검 (dry-run) 명령**:
  ```bash
  cd /home/mhhan/projects/ai-agent-orchestrator
  /home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
    --project-root /home/mhhan/projects/wt/260416-work \
    --task-type auto \
    --auto-run \
    --dry-run \
    --requirement "README.md에 AI Agent Harness 운영 규칙 섹션을 추가하라. README.md만 수정하라."
  ```
- **실전 기동 명령**:
  ```bash
  cd /home/mhhan/projects/ai-agent-orchestrator
  /home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
    --project-root /home/mhhan/projects/wt/260416-work \
    --task-type auto \
    --auto-run \
    --requirement "README.md에 AI Agent Harness 운영 규칙 섹션을 추가하라. README.md만 수정하라."
  ```
- **확인할 파일**:
  1. `operation_summary.md` -> 최종 판정이 **PASS** 상태인지 검수
  2. `final_report.md` -> `Changed Files` 항목에 README.md가 정상적으로 포함되었는지 대조

---

## 예시 2. pytest 실패 수정 (test_fix 태스크)
- **언제 쓰는지**: 일일 빌드 중 `pytest` 로그에 경로 에러나 타입 예외 에러가 검출되어, 테스트 케이스를 통과하도록 소스 코드를 기계적으로 수정하고 싶을 때 사용합니다.
- **요구사항 작성 팁**: pytest 오류 로그의 traceback 핵심 문구를 요구사항에 붙여넣어 주면 코딩 에이전트가 단번에 원인을 파악합니다.
- **실행 명령**:
  ```bash
  cd /home/mhhan/projects/ai-agent-orchestrator
  /home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
    --project-root /home/mhhan/projects/wt/260416-work \
    --task-type auto \
    --auto-run \
    --requirement "pytest 실패 로그 'FileNotFoundError: conftest.py not found'를 보고 원인을 수정하여 테스트가 다 통과하게 하라."
  ```
- **결과 확인**:
  - `operation_summary.md` 에서 `pytest: PASSED` 및 `final_report_check: PASSED`를 최종 봅니다.

---

## 예시 3. 코드 오류 수정 (python_code_fix 태스크)
- **언제 쓰는지**: 일반 파이썬 모듈 구동 중 예외(traceback)나 로직 누락이 일어나 코드의 미진한 로직을 긴급 수선하고 싶을 때 사용합니다.
- **실행 명령**:
  ```bash
  cd /home/mhhan/projects/ai-agent-orchestrator
  /home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
    --project-root /home/mhhan/projects/wt/260416-work \
    --task-type auto \
    --auto-run \
    --requirement "run_daily_ops.py에서 금융통계 수집 시 발생하는 NoneType traceback 에러를 수정하라."
  ```
- **Failover 발생 시 작동 흐름**:
  1. Claude Code 에이전트가 가동되어 수정을 하려다 한도 초과(429)로 멈춥니다.
  2. 하네스가 Claude 상태를 `red`로 잠그고, 수정한 내역을 `next_action.md`에 보관합니다.
  3. 자동으로 2순위 에이전트인 Codex CLI를 호출하여 끊긴 시점부터 이어서 개발하여 완결시킵니다.
  4. 형님은 그냥 마지막에 `operation_summary.md`만 확인하면 됩니다. (이력이 `failover_chain.md`에 다 기록됩니다.)

---

## 예시 4. 리팩터링 검토 (refactor 태스크)
- **언제 쓰는지**: 스크립트 결합도를 낮추거나 중복 모듈을 정합하여 소스 가독성을 대폭 끌어올리고 싶을 때 사용합니다.
- **안전 규칙 (중요)**: 리팩터링은 변경 범위가 매우 넓으므로 **반드시 dry-run 또는 리뷰 중심으로 시작**해야 합니다. 바로 실전 가동하여 소스를 헤집어놓지 않도록 통제하십시오.
- **안전 기동 명령 (dry-run)**:
  ```bash
  cd /home/mhhan/projects/ai-agent-orchestrator
  /home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
    --project-root /home/mhhan/projects/wt/260416-work \
    --task-type auto \
    --auto-run \
    --dry-run \
    --requirement "전체 오케스트레이터 호출 아키텍처를 구조 개선하라."
  ```
- **판정 검수**:
  - `task_classification.log`를 열어 `task_weight: heavy`로 승격된 이유를 점검하고, 에이전트 배치 계획을 먼저 눈으로 검토하십시오.

---

## 예시 5. 최근 diff 최종 리뷰 (final_review 태스크)
- **언제 쓰는지**: 실제 소스 변경은 끝났으나, 형님이 형상 관리(Git)에 반영하기 전 변경된 패치가 시스템 3대 안전 규칙(적대적, 방어적, 복원력)을 완벽히 지키고 있는지 검증하고 싶을 때 사용합니다.
- **실행 명령**:
  ```bash
  cd /home/mhhan/projects/ai-agent-orchestrator
  /home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
    --project-root /home/mhhan/projects/wt/260416-work \
    --task-type auto \
    --auto-run \
    --requirement "최근 변경된 diff 패치를 3대 관점으로 검수하고 최종 리뷰 의견서를 작성하라."
  ```
- **동작 원리**:
  - 요구사항 키워드 분석으로 `final_review` 태스크 타입이 식별됩니다.
  - 코딩이 필요하지 않은 순수 리뷰이므로 `antigravity_cli`가 단독 1순위로 배정됩니다.
  - Antigravity가 패치를 열어본 뒤 `.aiagent/runs/{TASK_ID}/antigravity_review.md`에 검수 판정을 렌더링합니다.

---

## 예시 6. Claude 사용량 제한 발생 (Failover 실전 대응)
- **상황**: 일일 빌드 중 `Claude Code` API 호출량이 제한되어 작업을 중간에 토해내고 탈출한 상태입니다.
- **하네스 복원 프로세스**:
  1. Claude가 한계에 봉착하여 `usage limit reached / capacity limit` 등의 로그가 검출되면, 하네스가 즉시 `agent_status.yaml`의 Claude quota_state를 `red`로 돌립니다.
  2. `state.md`를 Handoff로 갱신하여 인계 상태를 알립니다.
  3. `next_action.md`를 빌드하여 "Claude가 어디까지 변경했고, Codex가 무엇을 인계받아야 하는지" 가이드를 생성합니다.
  4. Codex CLI 에이전트가 가상 TUI로 이어받아 최종 테스트 통과까지 개발을 계속 수행합니다.
- **형님의 대응**:
  - 작업이 에러 없이 무사히 마무리되었다면 `.aiagent/runs/{TASK_ID}/failover_chain.md`를 가볍게 확인하여 Handoff가 원활했는지 모니터링하시면 됩니다.

---

## 예시 7. 모든 코딩 Agent 사용 불가 (비상 대응)
- **상황**: Claude가 `red`로 차단된 상황에서 연이어 Codex 마저 `red` 상태가 되어, 일을 수행할 코딩 에이전트가 아무도 남아 있지 않은 심각한 상태입니다.
- **하네스 안전 복원 장치**:
  - 오케스트레이터는 리뷰 전용인 Antigravity를 강제로 코딩 용도로 강등/승격하지 않습니다.
  - 작업은 즉각 중단되고, 최종 판정은 **`NEEDS_HUMAN_REVIEW`**로 동결됩니다.
  - 실패 조치서인 `failure_report.md`가 긴급 생성됩니다.
- **형님의 해결 순서**:
  1. `failure_report.md`에 명시된 에러 로그를 읽고 계정 및 API Quota 한도를 확인합니다.
  2. Quota 한도 대기(쿨다운 시간 경과) 또는 계정 교체가 완료되면, 실패 조치서 하단의 **Recommended Rerun Command**를 복사합니다.
  3. 아래와 같이 리셋 옵션을 붙여 재가동합니다:
     ```bash
     cd /home/mhhan/projects/ai-agent-orchestrator
     /home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
       --project-root /home/mhhan/projects/wt/260416-work \
       --task-type auto \
       --auto-run \
       --reset-agent-state claude_code=green \
       --reset-agent-state codex_cli=green \
       --requirement "작은 Python 코드 오류를 수정하라."
     ```
  4. 상태 리셋과 동시에 작업이 무결하게 재수행됩니다.
