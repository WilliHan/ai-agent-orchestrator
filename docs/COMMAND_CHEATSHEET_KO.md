# AI Agent Orchestrator 명령어 치트시트

본 치트시트는 형님이 터미널 창에서 작업할 때 빠르게 복사하고 붙여넣어(복붙) 사용할 수 있는 핵심 명령어 모음집입니다.

---

## 1. 공통 레포지토리로 이동
오케스트레이터 공통 엔진 명령을 기동하기 위해 공통 폴더로 이동합니다.
```bash
cd /home/mhhan/projects/ai-agent-orchestrator
```
*설명: 공통 엔진 저장소 경로로 이동합니다.*

---

## 2. 대상 프로젝트 및 프로필 확인
연동할 프로젝트의 프로필 설정이 올바르게 맺어져 있는지 검사합니다.
```bash
cd /home/mhhan/projects/wt/260416-work
cat .aiagent/project.yaml
```
*설명: 대상 프로젝트 루트로 이동하여 연동 설정을 출력해 봅니다.*

---

## 3. dry-run 기본 명령
실제 코드를 고치지 않고 동작 유형 및 배정될 에이전트만 사전 시뮬레이션해 봅니다.
```bash
cd /home/mhhan/projects/ai-agent-orchestrator

/home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
  --project-root /home/mhhan/projects/wt/260416-work \
  --task-type auto \
  --auto-run \
  --dry-run \
  --requirement "README.md에 공통 AI Agent Orchestrator 사용법 섹션을 추가하라. README.md만 수정하라."
```
*설명: `--dry-run` 옵션을 주어 가상 분석 설계 과정만 점검합니다.*

---

## 4. 실제 실행 기본 명령
시뮬레이션 검수가 끝난 요구사항을 바탕으로 실제 에이전트를 가동해 소스를 수정합니다.
```bash
cd /home/mhhan/projects/ai-agent-orchestrator

/home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
  --project-root /home/mhhan/projects/wt/260416-work \
  --task-type auto \
  --auto-run \
  --requirement "README.md에 공통 AI Agent Orchestrator 사용법 섹션을 추가하라. README.md만 수정하라."
```
*설명: 실제 코드를 수정하고 단위 테스트 및 기능 스모크 테스트까지 완결합니다.*

---

## 5. 최신 run 확인 (가장 최근 실행 디렉토리 파악)
가장 마지막에 기동한 에이전트의 TASK_ID 디렉토리 위치를 빠르게 파악합니다.
```bash
cd /home/mhhan/projects/wt/260416-work
ls -1dt .aiagent/runs/*/ | head -1
```
*설명: 생성 일자별로 정렬하여 가장 최신의 runs 하위 폴더명을 알아냅니다.*

---

## 6. 요약 보고서 (operation_summary.md) 확인
에이전트가 완수한 작업의 합격 여부를 즉각 한눈에 훑어봅니다.
```bash
cd /home/mhhan/projects/wt/260416-work
cat $(ls -1dt .aiagent/runs/*/ | head -1)/operation_summary.md
```
*설명: 최신 실행 폴더에 들어 있는 초압축 PASS/FAIL 요약서를 터미널 창에 출력합니다.*

---

## 7. 상세 보고서 (final_report.md) 확인
작업 유형, 변경 파일 상세 내역, 단위 테스트 합격 로그 및 라우터 매칭 근거를 확인합니다.
```bash
cd /home/mhhan/projects/wt/260416-work
cat $(ls -1dt .aiagent/runs/*/ | head -1)/final_report.md
```
*설명: 최신 실행 폴더의 final_report.md 상세 로그를 조회합니다.*

---

## 8. 실패 보고서 (failure_report.md) 확인
작업 검수가 실패했을 때 에러 원인과 재실행 및 복원 명령을 상세히 읽습니다.
```bash
cd /home/mhhan/projects/wt/260416-work
cat $(ls -1dt .aiagent/runs/*/ | head -1)/failure_report.md
```
*설명: 최신 실행 폴더의 failure_report.md 파일이 존재할 경우 에러 조치 요령을 출력합니다.*

---

## 9. 에이전트 Quota 상태 확인
에이전트들의 현재 쿨다운 상태 및 quota_state(green/red/black) 상태를 파악합니다.
```bash
cat /home/mhhan/projects/ai-agent-orchestrator/orchestrator/agent_status.yaml
```
*설명: 공통 엔진 내의 Quota DB를 직접 열어 차단된 에이전트가 있는지 조회합니다.*

---

## 10. Claude Quota 상태 복구 및 에이전트 선택 확인
Claude가 rate limit으로 인해 `red` 상태가 되었을 때, 강제로 상태를 `green`으로 돌려놓고 정상 라우팅되는지 확인합니다.
```bash
cd /home/mhhan/projects/ai-agent-orchestrator

/home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
  --project-root /home/mhhan/projects/wt/260416-work \
  --task-type python_code_fix \
  --use-agent-router \
  --reset-agent-state claude_code=green \
  --show-agent-selection \
  --requirement "Agent 상태 복구 테스트"
```
*설명: `--reset-agent-state` 명령으로 Quota를 복구한 후 `--show-agent-selection`을 통해 실제로 Claude가 정상 1순위로 지목되는지 검수하고 바로 종료합니다.*

---

## 11. dry-run 리뷰 요청
실제 코딩은 하지 않고, 완성된 코드가 들어있다고 가정했을 때 Antigravity independent review가 동작할 환경인지 사전 시험합니다.
```bash
cd /home/mhhan/projects/ai-agent-orchestrator

/home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
  --project-root /home/mhhan/projects/wt/260416-work \
  --task-type auto \
  --auto-run \
  --dry-run \
  --requirement "최근 변경된 diff를 최종 리뷰하라."
```
*설명: requirement 내 '리뷰' 패턴을 타서 task_type이 `final_review`로 추론되고 Antigravity를 매칭하는 흐름을 시뮬레이션합니다.*

---

## 12. 3대 관점 리뷰 요청 (Antigravity 직접 가동)
실제로 Antigravity CLI를 기동하여 3대 안전 관점(적대적, 방어적, 복원력)에 입각한 마크다운 검수 보고서를 작성하게 합니다. (dry-run이 아니며, antigravity review_only 러너가 실제 구동됩니다.)
```bash
cd /home/mhhan/projects/ai-agent-orchestrator

/home/mhhan/projects/wt/260416-work/.venv/bin/python orchestrator/run_task.py \
  --project-root /home/mhhan/projects/wt/260416-work \
  --task-type final_review \
  --use-agent-router \
  --with-antigravity-review \
  --requirement "최근 변경된 소스 코드를 3대 관점으로 정밀 검수하라."
```
*설명: `final_review` 태스크로 고정 구동하여 Antigravity가 소스 검토 및 보고서를 빌드하게 합니다.*

---

## 13. 실패 보고 요약 로그 확인
장애나 정책 위반으로 실행이 도중에 끊겼을 때 체티에게 보낼 압축 오류 문자열을 바로 가져옵니다.
```bash
cd /home/mhhan/projects/wt/260416-work
tail -n 10 $(ls -1dt .aiagent/runs/*/ | head -1)/failure_report.md
```
*설명: failure_report.md의 맨 마지막 섹션에 기재된 '다음에 붙여넣을 요약 로그'를 긁어오기 위해 끝에서 10줄을 봅니다.*

---

## 14. 대상 프로젝트 git 상태 확인
본체 프로젝트 내에 지저분한 파일이나 비정상 변경이 없는지 이동하지 않고 조회합니다.
```bash
git -C /home/mhhan/projects/wt/260416-work status --short
```
*설명: git -C 옵션으로 wt 폴더로 자리를 옮기지 않고도 단번에 git 단축 상태를 봅니다.*

---

## 15. 금지 파일 수정 여부 즉각 판정
`.env`나 `analysis.db` 등 절대 건드려서는 안 되는 핵심 파일이나 산출물이 에이전트 수정 과정에서 오염되었는지 1초 만에 걸러냅니다.
```bash
git -C /home/mhhan/projects/wt/260416-work status --short | grep -E '\.env|analysis\.db|reports/' || echo "금지 파일 수정 없음"
```
*설명: grep 필터를 통과한 파일이 없다면 '금지 파일 수정 없음' 문구를 보장 출력합니다.*
