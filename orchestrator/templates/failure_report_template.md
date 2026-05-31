# Task Failure Report (작업 실패 및 중단 보고서)

## 1. 실패 단계 (Failure Stage)
- **중단 지점**: {failure_stage}

## 2. 실패 Agent (Failed Agent)
- **최종 시도 Agent**: {failed_agent}

## 3. 실패 사유 (Reason)
- **주요 원인**: {failure_reason}

## 4. 현재 Agent 상태 (Agent Status Summary)
- **상태 목록**:
{agent_status_summary}

## 5. 이미 수행한 작업 (Completed Steps)
- **완료된 내역**:
{completed_steps}

## 6. 남은 작업 (Remaining Tasks)
- **미완료 내역**:
{remaining_tasks}

## 7. 사용자가 확인해야 할 사항 (Action Required)
- **조치 권고**:
{human_actions}

## 8. 재실행 권장 명령 (Recommended Rerun Command)
- **실행 명령**:
`{rerun_command}`

## 9. 상태 변경 (State Changes)
- **이전 -> 이후**: {state_change_summary}

## 10. 수동 조치 필요 여부 (Manual Action Required)
- **여부**: {manual_action_required_flag}

## 11. 다음에 붙여넣을 요약 로그 (Summary Log)
```
{summary_log_content}
```
