import sys
import os
import re

def main():
    if len(sys.argv) < 2:
        print("오류: RUN_DIR 인자가 누락되었습니다.")
        sys.exit(1)

    run_dir = sys.argv[1]
    os.makedirs(run_dir, exist_ok=True)
    log_path = os.path.join(run_dir, "final_report_check.log")
    report_path = os.path.join(run_dir, "final_report.md")

    required_sections = {
        "작업 ID": ["작업 ID", "Task ID"],
        "요구사항": ["요구사항", "Requirement"],
        "작업 유형": ["작업 유형", "Task Type"],
        "실행 Agent": ["실행 Agent", "Execution Agent"],
        "실행 결과": ["실행 결과", "Execution Result"],
        "변경 파일": ["변경 파일", "Changed Files"],
        "테스트 결과": ["테스트 결과", "Test Results"],
        "diff 요약": ["diff 요약", "Diff Summary"],
        "남은 리스크": ["남은 리스크", "Remaining Risks"],
        "최종 상태": ["최종 상태", "Final Status"],
        "스모크 테스트 결과": ["Smoke Test 결과", "스모크 테스트 결과"],
        "Agent 선택 결과": ["Agent 선택 결과", "agent 선택 결과"],
        "Usage Limit / Failover 결과": ["Usage Limit / Failover 결과"],
        "Failover Chain": ["Failover Chain"]
    }

    # Phase 7 모드 판정
    is_phase7 = os.path.exists(os.path.join(run_dir, "task_classification.log")) or os.path.exists(os.path.join(run_dir, "operation_summary.md"))
    if is_phase7:
        required_sections["최종 운영 모드 결과"] = ["최종 운영 모드 결과"]
        required_sections["사용자 검토 요약"] = ["사용자 검토 요약"]

    missing_sections = []

    with open(log_path, "w", encoding="utf-8") as log_f:
        log_f.write(f"최종 보고서 검증 시작... (대상 폴더: {run_dir})\n")
        
        if not os.path.exists(report_path):
            log_f.write(f"오류: final_report.md 파일이 존재하지 않습니다: {report_path}\n")
            log_f.write("결과: 실패 (보고서 없음)\n")
            print("final_report.md 파일이 존재하지 않습니다.")
            sys.exit(1)

        with open(report_path, "r", encoding="utf-8") as rf:
            content = rf.read()

        for section_name, keywords in required_sections.items():
            found = False
            for kw in keywords:
                if re.search(re.escape(kw), content, re.IGNORECASE):
                    found = True
                    break
            if not found:
                missing_sections.append(section_name)

        if missing_sections:
            log_f.write("누락된 필수 섹션 발견:\n")
            for section in missing_sections:
                log_f.write(f"- {section}\n")
            log_f.write("결과: 실패 (필수 섹션 누락)\n")
            print(f"필수 섹션 누락이 발견되었습니다: {', '.join(missing_sections)}")
            sys.exit(1)

        # 스모크 테스트 상태 FAILED 검사
        smoke_failed_match = re.search(r"-\s*상태\s*:\s*(FAILED)", content, re.IGNORECASE)
        
        if smoke_failed_match:
            log_f.write("스모크 테스트 실패 감지 (상태: FAILED)\n")
            log_f.write("결과: 실패 (스모크 테스트 실패)\n")
            print("최종 보고서 검사 실패: 스모크 테스트 결과 상태가 FAILED입니다.")
            sys.exit(1)

        log_f.write("결과: 성공 (모든 필수 섹션 검증 통과 및 스모크 테스트 성공/SKIPPED 확인)\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
