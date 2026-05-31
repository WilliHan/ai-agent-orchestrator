# GITHUB SETUP GUIDE (GitHub 저장소 연동 가이드)

본 가이드는 공통 `ai-agent-orchestrator` 로컬 저장소를 원격 GitHub 저장소에 올리고 안전하게 형상 관리 및 버전 통제를 시작하는 절차를 안내합니다.

> [!IMPORTANT]
> 로컬의 Quota 상태나 실행 스크립트에는 민감한 권한이나 로컬 경로가 포함될 수 있으므로, 반드시 **Private Repository(비공개 저장소)**로 생성하여 팀 내에서만 공유할 것을 강력히 권장합니다.

## 1. 사전 확인 명령 (민감 파일 검사)
저장소 초기화 및 첫 커밋을 올리기 전에 로컬에 민감 설정 파일(`.env`)이나 임시 실행 디렉토리(`runs/` 하위 로그)가 포함되어 있는지 반드시 자가 진단을 수행하십시오.
```bash
cd /home/mhhan/projects/ai-agent-orchestrator
git status --short
# .gitignore가 제대로 적용되어 임시 로그나 가상환경이 무시되고 있는지 확인합니다.
```

## 2. GitHub 원격 저장소 연동 순서 (명령어 예시)
실제 원격 형상 관리를 동기화하려면 아래의 명령 조합을 순차적으로 수행하십시오.

```bash
# 1) 로컬 Git 저장소 초기화
git init

# 2) 파일 상태 요약 확인
git status --short

# 3) 현재 파일들을 스테이징 영역에 추가
git add .

# 4) 최초 커밋 수행
git commit -m "tooling(orchestrator): add multi-agent AI harness"

# 5) 기본 브랜치 이름을 main으로 수정
git branch -M main

# 6) GitHub에 생성한 Private Repo 원격 저장소 추가
git remote add origin git@github.com:<USER>/ai-agent-orchestrator.git

# 7) 원격 main 브랜치로 push 수행
git push -u origin main
```

## 3. 주의사항
- 실제 `git init`, `git commit`, `git remote add`, `git push` 등 형상 상태를 영구적으로 변경하는 파괴적 형상 명령은 오케스트레이션 설계와 최초 복사 검증이 끝난 후 **사용자 승인 하에 안전하게 직접 수행**해야 합니다.
- 실수로 큰 데이터베이스(`analysis.db`)나 개인 토큰이 들어간 파일이 원격 저장소에 업로드되지 않도록 항상 `.gitignore`를 점검하고 사용하십시오.
