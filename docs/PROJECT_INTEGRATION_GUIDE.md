# PROJECT INTEGRATION GUIDE (개별 프로젝트 연동 가이드)

본 가이드는 공통 `ai-agent-orchestrator`를 개별 소프트웨어 프로젝트에 연동하여 AI Agent 하네스 기능을 수행하는 방법을 설명합니다.

## 1. 개별 프로젝트 설정 (.aiagent/project.yaml)
오케스트레이터를 적용하려는 모든 대상 프로젝트의 루트 디렉토리에 `.aiagent/project.yaml` 파일을 다음과 같이 생성해야 합니다.

```yaml
project:
  name: "프로젝트명"
  root: "대상 프로젝트의 절대 경로"

orchestrator:
  path: "/home/mhhan/projects/ai-agent-orchestrator"

validation:
  python: ".venv/bin/python"                 # 프로젝트 내의 파이썬 인터프리터 경로
  pytest: ".venv/bin/python -m pytest"        # 프로젝트 내의 pytest 명령

forbidden:
  files:
    - ".env"
    - "analysis.db"
  dirs:
    - "reports/"
    - ".git/"

runtime:
  runs_dir: ".aiagent/runs"
  reports_dir: ".aiagent/reports"

agents:
  claude_code:
    enabled: true
  codex_cli:
    enabled: true
  antigravity_cli:
    enabled: true
    role: "review_only"
```

또한 실행 로그 저장 및 무시 설정을 위해 아래 디렉토리 구조를 생성해야 합니다.
```bash
mkdir -p .aiagent/runs
touch .aiagent/runs/.gitkeep
```

대상 프로젝트의 `.gitignore` 파일에 아래 규칙을 덧붙여 실행 로그가 git 커밋에 포함되지 않도록 제외하십시오.
```gitignore
.aiagent/runs/*
!.aiagent/runs/.gitkeep
```

## 2. 공통 오케스트레이터 실행 방법
공통 오케스트레이터를 호출할 때는 `--project-root` 옵션을 통하여 대상 프로젝트 루트를 지정해 주어야 합니다.

### 기본 실행 명령 (Auto-run)
요구사항을 분석하여 태스크 타입과 가중치를 자동으로 파악하고, 최적의 에이전트 라우팅과 검증, 리뷰를 진행합니다.
```bash
python /home/mhhan/projects/ai-agent-orchestrator/orchestrator/run_task.py \
  --project-root /home/mhhan/projects/wt/260416-sugup \
  --task-type auto \
  --auto-run \
  --requirement "README.md에 마이너 에러 수정 문구를 보완하고, README.md만 수정하라."
```

### 안전한 dry-run 실행 명령
실제 에이전트 동작과 파일 쓰기를 건너뛰고, 오케스트레이터가 판단할 task_type, weight, Agent 라우팅과 프롬프트 생성 등의 사전 설계 과정만 검증합니다.
```bash
python /home/mhhan/projects/ai-agent-orchestrator/orchestrator/run_task.py \
  --project-root /home/mhhan/projects/wt/260416-sugup \
  --task-type auto \
  --auto-run \
  --dry-run \
  --requirement "README.md에 마이너 에러 수정 문구를 보완하고, README.md만 수정하라."
```

## 3. 결과 확인 파일
실행 시 대상 프로젝트의 `.aiagent/runs/{TASK_ID}/` 폴더 하위에 다음과 같은 산출물이 남게 됩니다.

1. **`operation_summary.md`**: 최종 요약 보고서 (합격 여부 `PASS`/`FAIL`/`WARNING`/`NEEDS_HUMAN_REVIEW` 신속 판정용)
2. **`final_report.md`**: 작업의 라우팅 매칭 근거, 테스트 로그, 정책 준수 보고 등을 담은 정밀 보고서
3. **`failure_report.md`**: 에이전트 실패 혹은 오케스트레이터 실행 제한 시 참조할 정밀 장애대응 및 재실행 조치 보고서
4. **`task_classification.log`**: 태스크 분류 논리 및 가중치 판단 로그
5. **`agent_selection.log`**: Quota 상태 및 가중치 제약에 따른 에이전트 제외/배정 이력 로그

## 4. 핵심 정책 준수
- **금지 파일 정책**: 대상 프로젝트 내의 `.env`, `analysis.db` 및 `reports/` 하위 과거 산출물 수정을 절대적으로 차단합니다.
- **리뷰 3대 관점**: 모든 수동/자동 리뷰 시 적대적 검토(Red Teaming), 예외 방어 검증(Negative Review), 그리고 복원력 및 부하 검증(Resilience Review)을 엄격하게 견지합니다.
- **승인 정책**: Read 조회 계열 명령과 경미한 마크다운 문서 수정은 승인 없이 바로 실행하며, 데이터 유실/영구 형상 변경(rm, reset --hard, commit/push, sudo 등) 명령은 엄격하게 사용자 승인을 받아 실행해야 합니다.
