# AI Agent Common Working Rules (AGENTS.md)

This document defines the common working rules and guidelines for all AI agents working on this repository.

## 1. Core Principles
* **Verify Objective and Scope Before Starting**: Every agent must clearly understand and verify the objective and scope of the task before performing any write operations.
* **Never Edit Forbidden Files**: Under no circumstances should an agent modify files restricted by `AI_RULES.md` or task-specific restrictions.
* **No Completion Report on Test Failures**: Never report a task as complete if tests are failing. All tests must pass, or failures must be explicitly justified and handled if they are out of scope.
* **Mandatory Git Diff Summary**: After completing changes, the agent must provide a clear and concise summary of the git diff (changed files, lines added/removed, etc.).
* **Never Guess - Verify Logs and Files**: When unsure about code behavior, database schemas, or test errors, do not guess. Inspect the logs, run diagnostics, and read the relevant source files.

## 2. Agent Collaboration & Failover Roadmap
This harness supports an **Agent Pool Router** (Phase 5) which automatically dispatches tasks based on task_type, task_weight, and agent status policies:
* **Primary Agent**: Claude Code
* **Fallback Agent**: Codex CLI
* **Independent Reviewer (review_only)**: Antigravity CLI
* **Routing Rules**:
  - Exclude any agents in `red` or `black` state.
  - Exclude `yellow` state agents from `heavy` weight tasks.
  - Exclude agents with quality scores below 0.70.
  - Antigravity cannot be assigned to coding primary roles (always review_only).
* **Usage Limit & Failover Process**:
  - When an agent encounters usage limits, missing runner, or error, its state is dynamically changed to `red` or `black` in `agent_status.yaml`.
  - Under `--auto-failover`, the harness automatically dispatches the task to the next highest-priority candidate.
  - If all coding agents fail, the task terminates immediately with a `needs_human_review` status, writing a `failure_report.md`.
* **Final Operation Mode (Phase 7)**:
  - Users run tasks in `auto` mode where the orchestrator automatically detects task type and weight.
  - Verification logs are simplified into `operation_summary.md` so that the operator can quickly check PASS/FAIL status.

## 3. General Execution Rules
1. Always run verification scripts (like `pytest`) after modifications.
2. Maintain documentation integrity. Do not delete existing comments or docstrings unless explicitly requested.
3. Commit message should follow project rules and clearly represent the change.

## 4. 리뷰·검토 3대 관점 필수 적용
리뷰 및 검토 작업 시 다음 3대 관점을 반드시 엄격히 검토해야 합니다.
1. **Red Teaming 검토 (적대적 관점)**: 설계 취약점, 우회 경로, 위험한 가정, 왜곡 신호 오발동 가능성을 식별합니다.
2. **Negative Testing / Review (부정·예외 방어적 관점)**: Null/None, Type Mismatch, Zero Division, 파일 부재, 명령 부재, 산출물 누락에 대한 방어 처리를 검증합니다.
3. **Stress Testing & Resilience Review (부하·복원력 관점)**: 대량 데이터 처리 성능, 장애 복구, 부분 재실행, Agent handoff, 디스크/로그 누적에 대한 복원력을 평가합니다.

## 5. 작업 승인 정책 (무승인 & 승인 필요 구분)
작업이 끊기지 않고 원활히 진행될 수 있도록 승인 여부를 명확히 구분합니다.

### 5.1 승인 없이 즉시 진행할 작업
* **조회 및 Read 계열 명령**: `pwd`, `ls`, `find`, `grep`, `cat`, `sed -n` 등 리드 명령 및 `git status`, `git diff`, `git log` 등 조회 명령
* **검토/확인**: 로그 파일 확인, 템플릿 수정, 테스트 및 검증 명령 실행
* **제한적 수정**: `AGENTS.md`, `AI_RULES.md`, `VALIDATION.md` 등 문서 파일의 제한적 수정, `orchestrator/` 하위 스크립트 및 템플릿 수정, run 결과 파일 생성

### 5.2 사용자 승인이 필요한 작업 (위험 명령)
* **환경 및 데이터 오염**: `.env` 수정, `analysis.db` 수정/삭제, `reports/` 하위 과거 산출물 수정/삭제
* **파괴적/보안 명령**: `rm`, `rm -rf`, `find -delete` 등 삭제 명령, `git reset --hard`, `git clean -fdx`, `sudo` 명령, `chmod -R 777`
* **광범위한 변경**: 패키지 설치 또는 시스템 환경 변경, 대규모 리팩터링, 핵심 로직의 광범위한 변경, `git commit`, `push`, `merge`

### 5.3 행동 원칙
* Read 계열 명령과 간단한 edit 작업은 승인 요청 없이 즉시 진행합니다.
* 위험 명령은 반드시 작업을 중단하고 사용자 확인을 받습니다.
* 불확실하면 위험도가 낮은 Read 명령으로 먼저 확인합니다.
