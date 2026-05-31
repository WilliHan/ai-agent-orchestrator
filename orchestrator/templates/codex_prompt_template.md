# Codex Handoff Instruction

이 작업은 Claude Code가 먼저 수행했거나 수행 중 실패한 작업을 이어받는 것이다.
처음부터 다시 시작하지 말고 state.md와 next_action.md를 기준으로 이어서 진행하라.

## 1. 읽어야 할 필수 컨텍스트 파일
* [AGENTS.md](file:///home/mhhan/projects/wt/260416-work/AGENTS.md)
* [AI_RULES.md](file:///home/mhhan/projects/wt/260416-work/AI_RULES.md)
* [VALIDATION.md](file:///home/mhhan/projects/wt/260416-work/VALIDATION.md)
* requirement.md
* state.md
* next_action.md
* test_result.log
* git_status.txt
* diff_stat.txt

## 2. 금지 사항 및 규칙 제약 (Forbidden)
* `.env` 파일 수정 금지
* `analysis.db` 수정/삭제 금지
* `reports/` 하위 과거 산출물 수정/삭제 금지
* `git reset --hard` 금지
* `git clean -fdx` 금지
* `rm -rf` 금지
* `sudo` 명령어 사용 금지
* 기존 테스트 검증 약화 금지

## 3. Required Output (최종 반환 구조)
작업 완료 시 반드시 다음의 정형 데이터 구조로 출력을 정리하여 보고하라:
* **변경 파일**: 수정한 파일들의 경로 목록
* **이어받은 내용**: 이전 세션 또는 에이전트가 수행하다 남겨둔 내용 요약
* **수행한 수정**: 본 에이전트가 직접 추가하거나 보완한 소스 내역
* **실행한 검증**: 동작 확인을 위해 구동한 명령어와 결과 로그
* **남은 리스크**: 작업 완료 후에도 잔존하는 불안 요소 혹은 확인이 필요한 사안
* **최종 상태**: 작업의 완결 여부 및 성공 판정
