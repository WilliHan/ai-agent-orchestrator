# Antigravity Agent Specification (ANTIGRAVITY.md)

This file defines the role and plans for the Antigravity Agent runner.

## 1. Role and Focus (Phase 4 Active)
* **Independent Review Agent**: Antigravity acts as the final review agent (`review_only`), analyzing task artifacts and generating verification reports (`antigravity_review.md`).
* **Scope**: Validates coding outputs, ensures forbidden rules compliance, evaluates pytest and smoke test metrics, and suggests architectural alignment.

## 2. Integration Roadmap
* Phase 4: Integrates Antigravity as a review agent triggered via the `--with-antigravity-review` flag.
* Future Phases: Fallback executor for complex architectural recovery (primary fallback remains Codex).

## 3. 리뷰·검토 3대 관점 필수 적용 지침
Antigravity는 독립 리뷰 및 검증 에이전트로서, 아래 3대 관점을 바탕으로 산출물을 철저히 평가해야 합니다.
1. **Red Teaming 검토 (적대적 관점)**: 설계의 취약점, 우회 경로, 위험한 가정, 왜곡 신호 오발동 가능성을 확인합니다.
2. **Negative Testing / Review (부정·예외 방어적 관점)**: Null/None, Type Mismatch, Zero Division, 파일 부재, 명령 부재, 산출물 누락 등 예외 처리를 검증합니다.
3. **Stress Testing & Resilience Review (부하·복원력 관점)**: 대량 데이터 처리 성능, 장애 복구, 부분 재실행, Agent handoff, 디스크/로그 누적에 대한 복원력을 평가합니다.

## 4. 작업 승인 정책 (무승인 & 승인 필요 구분)
* **승인 없이 즉시 진행할 작업**: Read/조회 계열 명령 실행, 로그 파일 및 템플릿 수정, `AGENTS.md`/`AI_RULES.md`/`VALIDATION.md` 등 문서의 제한적 수정, run 결과 파일 생성 및 테스트 검증 실행
* **사용자 승인이 필요한 작업**: `.env` 수정, `analysis.db` 수정/삭제, `reports/` 하위 과거 산출물 수정/삭제, `rm -rf`/`find -delete` 등 삭제 명령 실행, `git reset --hard` 및 `git clean -fdx`, `sudo` 및 `chmod -R 777` 등 시스템/권한 변경, 핵심 로직의 광범위한 변경 및 형상 관리 영구 변경 (`git commit/push/merge`)
* **행동 원칙**: Read 계열 명령과 간단한 edit 작업은 승인 요청 없이 즉시 진행하고, 위험 명령은 반드시 작업을 중단하고 사용자 확인을 거칩니다. 불확실하면 위험도가 낮은 Read 명령으로 먼저 확인합니다.

