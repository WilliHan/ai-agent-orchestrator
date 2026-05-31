import sys
import os
import subprocess

def main():
    if len(sys.argv) < 2:
        print("오류: RUN_DIR 인자가 누락되었습니다.")
        sys.exit(1)

    run_dir = sys.argv[1]
    os.makedirs(run_dir, exist_ok=True)
    log_path = os.path.join(run_dir, "policy_check.log")

    git_status_lines = []
    git_status_path = os.path.join(run_dir, "git_status.txt")

    # 1. git_status.txt 파일 읽기 시도
    if os.path.exists(git_status_path):
        with open(git_status_path, "r", encoding="utf-8") as f:
            git_status_lines = f.readlines()
    else:
        # fallback: 직접 git status 실행
        res = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
        if res.returncode == 0:
            git_status_lines = res.stdout.splitlines()

    forbidden_files = [".env", "analysis.db"]
    forbidden_dirs = ["reports/", ".git/"]
    violations = []

    with open(log_path, "w", encoding="utf-8") as log_f:
        log_f.write(f"정책 검사 시작... (검사 대상 폴더: {run_dir})\n")
        
        for line in git_status_lines:
            line = line.strip()
            if not line:
                continue
            # XY PATH 형태로 파싱
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            status_code, file_path = parts[0], parts[1]
            
            # 따옴표 제거 (파일명에 띄어쓰기가 있거나 한글이 깨지는 경우 대비)
            file_path = file_path.strip('"\'')
            
            # orchestrator/runs/ 경로는 무시
            if file_path.startswith("orchestrator/runs/"):
                continue
                
            # 금지 파일 매칭
            # 1. 정확한 파일 매칭
            if file_path in forbidden_files:
                violations.append(f"금지 파일 수정 감지: {file_path}")
            # 2. 금지 폴더 매칭
            for f_dir in forbidden_dirs:
                if file_path.startswith(f_dir):
                    violations.append(f"금지 경로 하위 파일 수정 감지: {file_path}")

        if violations:
            log_f.write("정책 위반 항목 발견:\n")
            for violation in violations:
                log_f.write(f"- {violation}\n")
            log_f.write("결과: 실패 (정책 위반)\n")
            print("정책 위반이 발견되었습니다. 로그 파일 'policy_check.log'를 확인하세요.")
            sys.exit(1)
        else:
            log_f.write("결과: 성공 (모든 정책 준수)\n")
            sys.exit(0)

if __name__ == "__main__":
    main()
