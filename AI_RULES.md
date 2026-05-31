# Absolute Forbidden Rules for AI Agents (AI_RULES.md)

These rules are strictly enforced. Violation of any rule below is considered a critical failure.

## 1. Absolute Forbidden Rules

1. **No Direct Work on `main` Branch**: Never perform any changes or commits directly on the `main` branch. Always work on a feature branch.
2. **No Editing of `.env` File**: The `.env` configuration file must not be modified or created.
3. **No Direct Modification or Deletion of `analysis.db`**: Do not delete or directly edit `analysis.db`. It is the central database hub.
4. **No Deletion of Past Reports**: Do not delete past outputs or artifacts located under `reports/` or other report directories.
5. **No `git reset --hard`**: Never perform hard resets that discard unstaged or staged changes.
6. **No `git clean -fdx`**: Do not run clean commands that delete untracked files or directories.
7. **No `rm -rf`**: Do not use `rm -rf` or similar recursive forced removal commands.
8. **No `sudo` Commands**: Do not request or execute command elevation using `sudo`.
9. **No Completion Reports on Test Failures**: Reporting a task as complete while in a test-failing state is strictly forbidden.
10. **No Evading Real-Data Validation with Mock/Fallback**: Do not write mocks or fake fallbacks to bypass actual verification against real data when real validation is required.
11. **Exclude Execution Results**: All runtime execution logs and metadata generated in `orchestrator/runs/` must be excluded from git commits (configured via `.gitignore`). Only `orchestrator/runs/.gitkeep` should be tracked.
12. **Block Forbidden Modifications**: Any attempts or actual modifications to forbidden files (e.g. `.env`, `analysis.db`, `reports/`, `.git/`) will be automatically detected by `policy_check.py` and immediately trigger a task failure.
13. **Handoff Continuity Policy**: Even if an agent fails, the task must not restart from scratch. It must be resumed continuously based on the context in `state.md` and `next_action.md`.
14. **No Discarding Previous Progress**: The fallback agent must not ignore, discard, or overwrite changes made by the previous agent.
15. **Mandatory Fallback Documentation**: If any agent transition or fallback takes place, the complete history and details must be recorded under the Fallback 결과 section in `final_report.md`.
16. **Antigravity Review-Only Role**: Antigravity is strictly confined to a `review_only` role. It must never perform code changes or create/modify source code files during the review phase.
17. **Soft Fallback on Reviewer Absence**: The absence of Antigravity CLI (runner missing) or review execution failures must not automatically flag the entire task as failed if the prior agent completed successfully.
18. **Review Failure Severity**: Any review failures or omission errors must be logged as either `warning` or `needs_human_review` to prevent destructive task failovers.
19. **No Allocation of Red/Black Agents**: Under no circumstances should an agent in `red` or `black` status be allocated for tasks or fallback.
20. **No Allocation of Yellow Agents to Heavy Tasks**: Agents with `yellow` status must not be allocated to tasks with `heavy` weight.
21. **Antigravity Review-Only Maintenance**: Antigravity must maintain its `review_only` role in Phase 5 and never be promoted to primary coding executor.
22. **Mandatory Routing Reason Logging**: The reasons for choosing or excluding any agent must be logged in `agent_selection.log` and integrated into the final report.
23. **Usage Limit as Normal Event**: Usage limit / rate limit triggers are treated as normal operational events, not system crashes.
24. **Handoff Documentation on Limits**: When usage limits or runner missing errors occur, state.md and next_action.md must be updated immediately to guide the fallback agent.
25. **Agent Status and Report Auditing**: Every agent state transition must be recorded in agent_status.yaml and audited under the Usage Limit / Failover 결과 and Failover Chain sections of final_report.md.
26. **No Coding Promotion for Antigravity**: If all coding agents (Claude/Codex) are unavailable, never force the promotion of Antigravity review agent as primary coding agent. The task must terminate with needs_human_review and generate failure_report.md.
27. **Zero-Touch Classification**: Under the final operation mode, users only enter requirements. The orchestrator must automatically infer the task_type and weight.
28. **Summary-First Auditing**: Users primarily verify task success or failure via `operation_summary.md` and check details in `final_report.md`.
29. **Enriched Failure Documentation**: On any task failures, `failure_report.md` must be generated with state transitions, rerun commands, and raw error log excerpts.
30. **No Anti-Promotion in Final Mode**: Under all coding agents unavailable scenarios, the orchestrator must never auto-promote Antigravity review-only agent as a coding primary.

## 2. 리뷰·검토 3대 관점 필수 적용 규칙
모든 에이전트는 리뷰 요청 또는 검토 단계에서 아래 3대 관점을 필수로 적용하여 엄격하게 검증해야 합니다.
1. **Red Teaming 검토 (적대적 관점)**: 설계 취약점, 우회 경로, 위험한 가정, 왜곡 신호 오발동 가능성을 확인합니다.
2. **Negative Testing / Review (부정·예외 방어적 관점)**: Null/None, Type Mismatch, Zero Division, 파일 부재, 명령 부재, 산출물 누락 등 비정상 입력 및 인프라 에러 예외 처리를 검증합니다.
3. **Stress Testing & Resilience Review (부하·복원력 관점)**: 대량 데이터 처리 성능, 장애 복구, 부분 재실행, Agent handoff, 디스크/로그 누적에 대한 복원력을 평가합니다.

## 3. 작업 승인 정책 (무승인 & 승인 필요 구분)
대기 시간을 줄이고 업무 효율성을 극대화하기 위해 다음과 같이 승인 경계를 준수해야 합니다.

* **승인 없이 즉시 진행할 작업 (Read/조회 및 경미한 수정)**
  - Read 계열 명령 실행: `pwd`, `ls`, `find`, `grep`, `cat`, `sed -n` 등
  - 조회 명령 실행: `git status`, `git diff`, `git log` 등
  - 로그 파일 확인 및 템플릿 파일 수정
  - `AGENTS.md`, `AI_RULES.md`, `VALIDATION.md` 등 프로젝트 내 문서 파일의 제한적 수정
  - `orchestrator/` 하위 스크립트의 제한적 수정 및 run 결과 파일 생성
  - 테스트 및 검증 명령 실행

* **사용자 승인이 필요한 작업 (위험 명령 및 파괴적 액션)**
  - `.env` 수정
  - `analysis.db` 수정/삭제
  - `reports/` 하위 과거 산출물 수정/삭제
  - `rm`, `rm -rf`, `find -delete` 등 삭제 명령 실행
  - `git reset --hard` 및 `git clean -fdx`
  - `sudo` 및 `chmod -R 777` 등 권한/시스템 계정 변경 명령
  - 패키지 설치 또는 시스템 환경 변경
  - 대규모 리팩터링 및 프로젝트 핵심 로직의 광범위한 변경
  - `git commit`, `push`, `merge` 등 형상 관리 영구 변경

* **기본 행동 원칙**
  - Read 계열 명령 및 간단한 edit 작업은 승인 요청 없이 즉시 진행합니다.
  - 위험 명령은 반드시 작업을 중단하고 사용자 확인을 거칩니다.
  - 불확실하면 위험도가 낮은 Read 명령으로 먼저 확인합니다.



