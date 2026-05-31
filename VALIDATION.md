# Validation Rules and Criteria (VALIDATION.md)

This document defines how tasks are validated and the criteria for completing them.

## 1. Validation Commands
* **Default Validation Command**: `pytest` (executed via `.venv/bin/python -m pytest`)
* **Smoke Tests**: Validated via `smoke_report.sh`. If no explicit smoke test exists in the repository, it logs "SKIPPED" without triggering a failure.
* **Policy Validator**: Checks for modifications in restricted paths (e.g., `.env`, `analysis.db`, `reports/`, `.git/`) using `policy_check.py`.
* **Report Validator**: Verifies formatting structure of `final_report.md` using `final_report_check.py`.

## 2. Completion Criteria (Phase 2 Automated)
A task is considered complete only when all the following items are met:
1. **pytest Log**: A test execution log (`test_result.log`) must show successful results.
2. **Smoke Test Result**: A smoke execution log (`smoke_result.log`) must be present (can be "SKIPPED").
3. **Policy Verification**: A policy check log (`policy_check.log`) must indicate all policies are respected.
4. **Saved Git Diff**: The git status, diff stats, and full patch must be saved in the task run directory.
5. **Final Report Check**: A final report check log (`final_report_check.log`) must verify that `final_report.md` contains all required sections.
6. **Final Report**: A `final_report.md` must be successfully generated, containing:
   - 작업 ID (Task ID)
   - 요구사항 (Requirement)
   - 작업 유형 (Task Type)
   - 실행 Agent (Execution Agent)
   - 실행 결과 (Execution Result)
   - 변경 파일 (Changed Files)
   - 테스트 결과 (Test Results)
   - diff 요약 (Diff Summary)
   - 남은 리스크 (Remaining Risks)
   - 최종 상태 (Final Status)

## 3. Fallback Verification (Phase 3)
In case of primary agent (Claude Code) failures or usage limit blocks, the following fallback verification is performed:
1. **Claude Failure Detection**: Detects rate limits or runner errors via output log analysis or simulation flags.
2. **State & Handoff Logs**: Verifies `state.md` is updated with `handoff` status, reason, and target agent.
3. **Next Action Report**: Generates `next_action.md` describing failure context, files, and guidance to prevent cold-restarts.
4. **Handoff Prompt**: Generates `codex_prompt.md` containing rules and boundaries for the fallback agent.
5. **Codex Runner Execution**: Executes `run_codex.sh` with the generated prompt.
6. **Fallback History**: Records the complete fallback chain details in `final_report.md`.

## 4. Antigravity Review Verification (Phase 4)
When `--with-antigravity-review` option is enabled:
1. **Prompt Generation**: Verifies `antigravity_prompt.md` is generated in the run directory.
2. **Runner Execution**: Executes `run_antigravity.sh` using the generated prompt.
3. **Execution Output**: Verifies `antigravity_output.log` is generated in the run directory.
4. **Review Report**: Verifies `antigravity_review.md` is generated, or a reason for review skipping is recorded.
5. **Report Integration**: Validates that Antigravity review outcomes (verdict, opinions, and next steps) are integrated into `final_report.md`.
## 5. Agent Router Verification (Phase 5)
When `--use-agent-router` option is enabled:
1. **Agent Router Selection**: Verifies the selected agent conforms to the routing priorities in `agent_policy.yaml`.
2. **Quota State & Exclusions**:
   - Ensures agents with `red` or `black` status are excluded from selection.
   - Ensures agents with `yellow` status are excluded from `heavy` weight tasks.
3. **Quality Score Threshold**: Ensures agents with a quality score below 0.70 are excluded.
4. **Antigravity Review-Only Constraint**: Verifies Antigravity is not assigned as primary coding executor (only valid for `final_review` and `large_context_review` tasks).
5. **Selection Logs**: Verifies `agent_selection.log` is generated containing 후보 Agent, 각 Agent 상태, 제외 이유, 선택 사유.
6. **Report Integration**: Verifies `final_report.md` contains the Agent 선택 결과 block with all selection parameters.

## 6. Usage Limit Failover Verification (Phase 6)
When usage limit, quota exceeded, runner missing, or agent error occurs:
1. **Rate Limit Detection**: Automatically scans logs for 13 usage limit keywords (case-insensitive) to detect rate limit states.
2. **Runner Missing Detection**: Scans exit code 127 and command not found errors to detect missing runners.
3. **Agent Error Detection**: Scans general execution failure exit codes.
4. **Agent Status Update**: Updates `quota_state` of the failed agent in `agent_status.yaml` (`red` for rate_limit/agent_error, `black` for runner_missing).
5. **State Backups**: Verifies `agent_status_before.yaml` and `agent_status_after.yaml` are generated in the run directory.
6. **Handoff Records**: Updates `state.md` with `handoff` status and reason, and generates `next_action.md` to guide the next agent.
7. **Failover Chain**: Records the dynamic routing transitions in `failover_chain.md` and `final_report.md`.
8. **Failure Report**: Generates `failure_report.md` when all agents are unavailable or policy violation occurs.
9. **Needs Human Review**: Ensures the task ends with `Needs Human Review` verdict and warning logs without trying to promote Antigravity review agent as coding primary.

## 7. Final Operation Mode Verification (Phase 7)
Under the final operation mode:
1. **Task Type Auto-Classification**: Matches keywords in the requirement text to dynamically classify the `task_type` and writes the details to `task_classification.log`.
2. **Task Weight Auto-Classification**: Determines the weight based on defaults and keywords (e.g. `전체`, `대규모` forces `heavy` weight classification).
3. **Auto-Run Bundle**: Verification of `--auto-run` activating router, auto-failover, and Antigravity independent review concurrently.
4. **Operation Summary md**: Verifies `operation_summary.md` is generated and structured containing verdict, summary log, and validation metrics for the operator.
5. **Dry-run Final Operation**: Verifies the safety flow in dry-run with router enabled, classification completed, and SKIPPED status log generated without actual files modification.
6. **Failure Report Enrichment**: Verifies state transitions, rerun instructions, and raw summary logs are properly appended to `failure_report.md` on failures.
7. **Report Integration**: Verifies Phase 7 metadata ("최종 운영 모드 결과", "사용자 검토 요약") is successfully appended to `final_report.md` and validated under `final_report_check.py`.
