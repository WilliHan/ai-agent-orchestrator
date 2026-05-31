# AI Agent Orchestrator

## 목적
여러 AI Agent를 작업 유형, 사용량 상태, 검증 결과에 따라 자동 라우팅하고 failover하는 로컬 오케스트레이터다.

## 핵심 기능
- task_type 자동 추론
- task_weight 자동 추론
- Agent Router
- Claude Code primary
- Codex fallback
- Antigravity review-only
- Usage Limit Failover
- policy_check
- final_report_check
- operation_summary.md 생성
- failure_report.md 생성

## 기본 사용법

```bash
python orchestrator/run_task.py \
  --project-root /path/to/project \
  --task-type auto \
  --auto-run \
  --requirement "요구사항"
```

## 안전한 dry-run 사용법

```bash
python orchestrator/run_task.py \
  --project-root /path/to/project \
  --task-type auto \
  --auto-run \
  --dry-run \
  --requirement "요구사항"
```

## 개별 프로젝트 연동
각 프로젝트에는 .aiagent/project.yaml을 둔다.

## 운영 원칙
- 사용자는 요구사항만 입력한다.
- Orchestrator가 task_type, task_weight, Agent를 자동 선택한다.
- 실패 시 auto-failover를 수행한다.
- 사용자는 operation_summary.md를 먼저 확인한다.

## 리뷰 3대 관점
- Red Teaming 검토
- Negative Testing / Review
- Stress Testing & Resilience Review

## 승인 정책
- Read 계열 명령은 무승인 진행
- 간단한 edit은 무승인 진행
- 위험 명령은 사용자 승인 필요
