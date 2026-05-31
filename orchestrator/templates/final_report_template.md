# Final Task Report (최종 작업 보고서)

- **작업 ID (Task ID)**: {task_id}
- **요구사항 (Requirement)**: {requirement}
- **작업 유형 (Task Type)**: {task_type}
- **실행 Agent (Execution Agent)**: {execution_agent}
- **실행 결과 (Execution Result)**: {execution_result}

## 변경 파일 (Changed Files)
{changed_files}

## 테스트 결과 (Test Results)
{test_results}

## diff 요약 (Diff Summary)
{diff_summary}

## 남은 리스크 (Remaining Risks)
{remaining_risks}

## Smoke Test 결과
- 상태: {smoke_status}
- 사유: {smoke_reason}
- 로그 파일: smoke_result.log

## Fallback 결과
- fallback 발생 여부: {fallback_occurred}
- 최초 Agent: {initial_agent}
- 실패 사유: {failure_reason}
- 대체 Agent: {alternative_agent}
- 대체 Agent 실행 결과: {alternative_agent_result}
- 최종 상태: {final_status}

## Agent 선택 결과
- Router 사용 여부: {router_used}
- 작업 유형: {task_type}
- 작업 무게: {task_weight}
- 선택 Agent: {selected_agent}
- 선택 사유: {selection_reason}
- 제외된 Agent: {excluded_agents_names}
- 제외 사유: {excluded_agents_reasons}
- 최종 실행 Agent: {final_execution_agent}

## Antigravity 리뷰 결과
- 실행 여부: {antigravity_executed}
- 실행 결과: {antigravity_result}
- 리뷰 파일: {antigravity_review_file}
- 최종 판정: {antigravity_verdict}
- 주요 의견: {antigravity_opinion}
- 다음 단계 진행 가능 여부: {antigravity_next_step}

## Usage Limit / Failover 결과
- auto-failover 사용 여부: {auto_failover_used}
- 사용량 제한 감지 여부: {usage_limit_detected}
- 실패 Agent: {failover_failed_agent}
- 실패 사유: {failover_failure_reason}
- 상태 변경: {failover_state_change}
- 대체 Agent: {failover_alternative_agent}
- 대체 실행 결과: {failover_alternative_result}
- 모든 Agent 사용 불가 여부: {all_agents_unavailable}
- 최종 상태: {failover_final_status}
- 수동 조치 필요 여부: {human_action_required}

## Failover Chain
1. 최초 Agent: {fc_initial_agent}
2. 실패 사유: {fc_failure_reason}
3. 상태 전환: {fc_state_change}
4. 다음 후보 Agent: {fc_next_candidate}
5. 선택 사유: {fc_selection_reason}
6. 대체 Agent 실행 결과: {fc_alternative_result}
7. 최종 상태: {fc_final_status}

## 최종 운영 모드 결과
- auto-run 사용 여부: {autorun_used}
- task_type 자동 추론 여부: {task_type_auto_classified}
- 추론된 task_type: {classified_task_type}
- task_weight: {classified_task_weight}
- Agent Router 사용 여부: {router_used_p7}
- auto-failover 사용 여부: {autofailover_used_p7}
- Antigravity final review 사용 여부: {antigravity_review_used_p7}
- 최종 상태: {final_status_p7}
- 사용자 확인 필요 여부: {human_action_required_p7}

## 사용자 검토 요약
- 형님이 확인할 핵심 결과: {major_points_p7}
- 수정된 파일: {changed_files_p7}
- 검증 결과: {validation_results_p7}
- 남은 리스크: {remaining_risks_p7}
- 다음 권장 조치: {next_action_p7}
