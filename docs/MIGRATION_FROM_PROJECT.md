# MIGRATION FROM PROJECT (프로젝트 이관 기록)

## 1. 분리 목적
- 기존 `sugup-pivot` 프로젝트에 종속되어 있던 AI Agent Orchestrator 및 하네스 구성요소를 범용적으로 사용 가능한 공통 라이브러리로 분리합니다.
- 공통 저장소 `ai-agent-orchestrator`를 만들어 다양한 프로젝트에서 독립적으로 연동 및 재사용할 수 있도록 관리 환경을 분리 및 단순화합니다.

## 2. 이관 경로 정보
- **원본 프로젝트 경로**: `/home/mhhan/projects/wt/260416-work`
- **신규 공통 repo 경로**: `/home/mhhan/projects/ai-agent-orchestrator`

## 3. 이관 파일 목록 (복사 완료)
공통 오케스트레이터의 핵심 동작과 정책, 가이드를 포함하는 모든 파일들을 안전하게 이관하였습니다.
- **문서 파일**: `AGENTS.md`, `AI_RULES.md`, `VALIDATION.md`, `CLAUDE.md`, `CODEX.md`, `ANTIGRAVITY.md`
- **핵심 모듈**: `orchestrator/run_task.py`, `orchestrator/router.py`, `orchestrator/task_classifier.py`
- **구성/설정 파일**: `orchestrator/agent_status.yaml`
- **동작 정책 디렉토리**: `orchestrator/policies/` (`agent_policy.yaml`, `command_policy.yaml`, `file_policy.yaml`)
- **실행 러너 디렉토리**: `orchestrator/runners/` (`run_claude.sh`, `run_codex.sh`, `run_antigravity.sh`)
- **템플릿 디렉토리**: `orchestrator/templates/` (`claude_prompt_template.md`, `codex_prompt_template.md`, `antigravity_review_prompt_template.md`, `final_report_template.md`, `failure_report_template.md`, `operation_summary_template.md`)
- **검증 도구 디렉토리**: `orchestrator/validators/` (`pytest.sh`, `smoke_report.sh`, `check_diff.sh`, `policy_check.py`, `final_report_check.py`)
- **운영 가이드 디렉토리**: `orchestrator/docs/` (`PHASE7_OPERATION_GUIDE.md`)

## 4. 이관 제외 파일 목록 (복사하지 않음)
실행 결과 로그, 민감 구성 정보, 그리고 기존 프로젝트 고유의 소스 코드는 공통 repo로 이관하지 않고 철저히 격리하였습니다.
- **실행 결과 데이터**: `orchestrator/runs/` 하위의 개별 실행 폴더 (예: `260531-*`, `task-*` 등)
- **비밀 설정**: `.env`
- **로컬 데이터베이스**: `analysis.db`
- **프로젝트 고유 산출물**: `reports/` 하위 폴더 및 파일
- **프로젝트 소스 코드**: `src/`, `tests/`, `webapp/`
- **기타 로컬 미추적 파일**: `.playwright-mcp/`, `Report_email_list00.txt`, `docs/design/system_upgrade_v2.6.0.md`

## 5. 기존 프로젝트에 남긴 파일 및 연동 설정
- **설정 파일**: `.aiagent/project.yaml` (대상 프로젝트의 이름, 경로, 오케스트레이터 매핑 정보 포함)
- **동작 추적 파일**: `.aiagent/runs/.gitkeep` (실행 결과가 저장될 디렉토리 뼈대 유지)
- **형상 제외 파일**: `.gitignore` 에 `.aiagent/runs/*` 규칙 추가
- **기존 오케스트레이터 폴더**: `orchestrator/` (공통 repo 연동에 따른 부작용 검증이 완전히 끝날 때까지 삭제를 보류하고 안전하게 유지합니다.)

## 6. 향후 정리 후보
- 기존 프로젝트의 `orchestrator/` 디렉토리는 새 공통 오케스트레이터의 실전 연동 검증이 완벽히 완료된 후 안전하게 삭제할 예정입니다.
- 개별 프로젝트의 `.venv/` 파이썬 경로를 `.aiagent/project.yaml`을 통해 오케스트레이터가 더 유연하게 호출하도록 래핑 레이어를 보강할 것입니다.

## 7. 주의사항
- 공통 오케스트레이터 코드를 수정할 경우, 반드시 공통 repo인 `/home/mhhan/projects/ai-agent-orchestrator` 내의 파일들을 편집해야 합니다.
- 원본 프로젝트의 `orchestrator/` 디렉토리를 임의로 삭제하거나 형상을 손상시켜서는 안 됩니다.
