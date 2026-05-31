import os
import sys
import argparse
from datetime import datetime
import subprocess
import re
from router import route_agent, determine_task_weight, update_agent_state_file, load_agent_status
from task_classifier import classify_task

def generate_task_id(project_root, runs_dir_sub):
    today_str = datetime.now().strftime('%y%m%d')
    runs_dir = os.path.join(project_root, runs_dir_sub)
    os.makedirs(runs_dir, exist_ok=True)
    
    counter = 1
    while True:
        task_id = f"{today_str}-{counter:03d}"
        if not os.path.exists(os.path.join(runs_dir, task_id)):
            return task_id
        counter += 1

def update_state(run_dir, task_id, status, details=None):
    state_path = os.path.join(run_dir, "state.md")
    timestamp = datetime.now().isoformat()
    
    lines = [
        f"# Task State: {task_id}",
        "",
        f"- **Status**: {status}",
        f"- **Last Updated**: {timestamp}",
        ""
    ]
    if details:
        lines.append("## Details")
        for k, v in details.items():
            lines.append(f"- **{k}**: {v}")
    
    with open(state_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def update_state_handoff(run_dir, task_id, handoff_reason):
    state_path = os.path.join(run_dir, "state.md")
    timestamp = datetime.now().isoformat()
    
    lines = [
        f"# Task State: {task_id}",
        "",
        f"- **Status**: handoff",
        f"- **Last Updated**: {timestamp}",
        "",
        "## 현재 진행 상태",
        "Claude Code 실행 중 실패 또는 사용량 제한 감지",
        "",
        "## 마지막 Agent",
        "claude_code",
        "",
        "## Handoff Reason",
        handoff_reason,
        "",
        "## 다음 Agent",
        "codex_cli",
        "",
        "## 다음 작업",
        "next_action.md 기준으로 이어받기"
    ]
    with open(state_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def extract_section(content, section_name):
    pattern = rf"(?i)(?:^|\n)(?:\*?\s*\*\*?{section_name}\*\*?:?|###?\s*{section_name})\s*\n*(.*?)(?=\n(?:\*?\s*\*\*?[a-zA-Z\s_-]+\*\*?:?|###?\s*[a-zA-Z\s_-]+)|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def fill_template(template, data):
    result = template
    for key, val in data.items():
        result = result.replace(f"{{{key}}}", str(val))
    return result

def load_rate_limit_keywords():
    keywords = [
        "rate limit", "usage limit", "quota exceeded", "too many requests",
        "limit reached", "try again later", "429", "insufficient quota",
        "daily limit", "weekly limit", "monthly limit", "usage cap", "capacity limit"
    ]
    policy_path = "orchestrator/policies/agent_policy.yaml"
    if os.path.exists(policy_path):
        try:
            with open(policy_path, "r", encoding="utf-8") as f:
                content = f.read()
            matches = re.findall(r'-\s*"([^"]+)"', content)
            if matches:
                keywords = list(set(keywords + matches))
        except Exception:
            pass
    return keywords

def main():
    parser = argparse.ArgumentParser(description="AI Agent Orchestrator Phase 7")
    parser.add_argument("--task-type", required=True, help="Task type (auto, refactor, doc etc)")
    parser.add_argument("--requirement", help="Requirement text")
    parser.add_argument("--requirement-file", help="Path to requirement file")
    parser.add_argument("--task-id", help="Explicit Task ID")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    # Target Project Root
    parser.add_argument("--project-root", help="Target project root directory")
    
    # Phase 3 Fallback Options
    parser.add_argument("--enable-codex-fallback", action="store_true", help="Enable Codex CLI fallback")
    parser.add_argument("--simulate-rate-limit", action="store_true", help="Simulate Claude rate limit failure")
    parser.add_argument("--simulate-claude-failure", action="store_true", help="Simulate Claude general runner failure")
    
    # Phase 4 Antigravity Options
    parser.add_argument("--with-antigravity-review", action="store_true", help="Enable Antigravity independent review")
    parser.add_argument("--simulate-antigravity-missing", action="store_true", help="Simulate Antigravity CLI missing")
    parser.add_argument("--simulate-claude-success", action="store_true", help="Simulate Claude runner success without execution")
    parser.add_argument("--simulate-pytest-success", action="store_true", help="Simulate pytest validation success")
    parser.add_argument("--simulate-smoke-success", action="store_true", help="Simulate smoke_report validation success")
    
    # Phase 5 Agent Pool Router Options
    parser.add_argument("--use-agent-router", action="store_true", help="Enable Agent Pool Router")
    parser.add_argument("--task-weight", choices=["light", "medium", "heavy"], help="Specify task weight")
    parser.add_argument("--set-agent-state", action="append", help="Set temporary agent state")
    parser.add_argument("--show-agent-selection", action="store_true", help="Show chosen agent and selection reason, then exit")
    
    # Phase 6 Usage Limit Failover Options
    parser.add_argument("--auto-failover", action="store_true", help="Automatically switch to fallback agent on failure")
    parser.add_argument("--simulate-agent-rate-limit", action="append", help="Simulate rate limit for specific agent")
    parser.add_argument("--simulate-agent-error", action="append", help="Simulate execution error for specific agent")
    parser.add_argument("--simulate-runner-missing", action="append", help="Simulate missing runner for specific agent")
    parser.add_argument("--reset-agent-state", action="append", help="Reset agent state")
    
    # Phase 7 Final Operation Options
    parser.add_argument("--auto-run", action="store_true", help="Enable automatic execution configurations")
    
    args = parser.parse_args()
    
    # Setup Orchestrator path and Project root
    orchestrator_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = args.project_root
    if not project_root:
        project_root = os.getcwd()
    project_root = os.path.abspath(project_root)
    
    # Phase 7 --auto-run 옵션 묶음 처리
    if args.auto_run:
        args.use_agent_router = True
        args.auto_failover = True
        args.with_antigravity_review = True
    
    if not args.requirement and not args.requirement_file:
        parser.error("Either --requirement or --requirement-file must be provided.")
        
    requirement_content = ""
    if args.requirement:
        requirement_content = args.requirement
    elif args.requirement_file:
        if not os.path.exists(args.requirement_file):
            print(f"Error: Requirement file '{args.requirement_file}' not found.")
            sys.exit(1)
        with open(args.requirement_file, 'r', encoding='utf-8') as f:
            requirement_content = f.read()
            
    # Resolve runs subdirectory from project config
    project_config_path = os.path.join(project_root, ".aiagent/project.yaml")
    runs_dir_sub = "orchestrator/runs"
    if os.path.exists(project_config_path):
        try:
            import yaml
            with open(project_config_path, "r", encoding="utf-8") as pf:
                cfg = yaml.safe_load(pf)
                runs_dir_sub = cfg.get("runtime", {}).get("runs_dir", ".aiagent/runs")
        except Exception:
            runs_dir_sub = ".aiagent/runs"
    else:
        if os.path.exists(os.path.join(project_root, "orchestrator/runs")):
            runs_dir_sub = "orchestrator/runs"
        else:
            runs_dir_sub = ".aiagent/runs"
            
    # Task ID generation
    task_id = args.task_id
    if not task_id:
        task_id = generate_task_id(project_root, runs_dir_sub)
        
    run_dir = os.path.join(project_root, runs_dir_sub, task_id)
    os.makedirs(run_dir, exist_ok=True)
    
    # Phase 7 --task-type auto 추론 지원
    task_type_auto_classified = "No"
    classified_task_type = args.task_type
    classified_task_weight = args.task_weight if args.task_weight else "N/A"
    
    if args.task_type == "auto":
        inferred_type, inferred_weight, confidence, classification_reason = classify_task(requirement_content)
        args.task_type = inferred_type
        task_type_auto_classified = "Yes"
        classified_task_type = inferred_type
        
        if not args.task_weight:
            args.task_weight = inferred_weight
            classified_task_weight = inferred_weight
            
        classification_log_path = os.path.join(run_dir, "task_classification.log")
        with open(classification_log_path, "w", encoding="utf-8") as clf:
            clf.write(f"=== 요구사항 기반 태스크 자동 추론 기록 ===\n")
            clf.write(f"입력 요구사항: {requirement_content}\n")
            clf.write(f"추론된 task_type: {inferred_type}\n")
            clf.write(f"추론 근거: {classification_reason}\n")
            clf.write(f"task_weight: {args.task_weight}\n")
            clf.write(f"신뢰도: {confidence}\n")
            clf.write(f"모호한 경우 fallback 처리 여부: {'Yes' if confidence < 0.5 else 'No'}\n")
    
    # Phase 6 Reset Agent State
    if args.reset_agent_state:
        for item in args.reset_agent_state:
            if "=" in item:
                k, v = item.split("=", 1)
                agent_name = k.strip()
                new_state = v.strip()
                update_agent_state_file(agent_name, new_state, new_error=None, dry_run=args.dry_run, run_dir=run_dir)
 
    # Phase 5 & 6 Agent Pool Router Parsing & Execution
    set_states = {}
    
    if args.reset_agent_state:
        for item in args.reset_agent_state:
            if "=" in item:
                k, v = item.split("=", 1)
                set_states[k.strip()] = v.strip()
    
    if args.simulate_rate_limit:
        set_states["claude_code"] = "red"
    if args.simulate_claude_failure:
        set_states["claude_code"] = "red"

    if args.set_agent_state:
        for item in args.set_agent_state:
            if "=" in item:
                k, v = item.split("=", 1)
                set_states[k.strip()] = v.strip()
                
    router_used = "Yes" if args.use_agent_router else "No"
    selected_agent = None
    selection_reason = ""
    excluded_agents = {}
    
    if args.use_agent_router:
        selected_agent, selection_reason, excluded_agents = route_agent(
            task_type=args.task_type,
            task_weight_opt=args.task_weight,
            set_states=set_states,
            run_dir=run_dir
        )
        print(f"[{datetime.now()}] Selected Agent: {selected_agent}")
        print(f"[{datetime.now()}] Selection Reason: {selection_reason}")
        
        if args.show_agent_selection:
            print(f"선택 Agent: {selected_agent if selected_agent else 'N/A'}")
            print(f"선택 사유: {selection_reason}")
            sys.exit(0)
    else:
        if args.task_type in ["final_review", "large_context_review"]:
            selected_agent = "antigravity_cli"
        else:
            selected_agent = "claude_code"
        selection_reason = "Router 비활성화로 인한 기본값 배정"
        
        if args.show_agent_selection:
            print(f"선택 Agent: {selected_agent}")
            print(f"선택 사유: {selection_reason}")
            sys.exit(0)
            
    print(f"[{datetime.now()}] Initializing task {task_id} in {run_dir}...")
    
    # 1. Save requirement.md
    with open(os.path.join(run_dir, "requirement.md"), "w", encoding="utf-8") as f:
        f.write(requirement_content)
        
    # 2. Generate claude_prompt.md from template
    template_path = os.path.join(orchestrator_path, "orchestrator/templates/claude_prompt_template.md")
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    else:
        prompt_template = "# Requirement\n{requirement}\n"
    
    claude_prompt = prompt_template.replace("{requirement}", requirement_content)
    with open(os.path.join(run_dir, "claude_prompt.md"), "w", encoding="utf-8") as f:
        f.write(claude_prompt)
        
    # 3. Create state.md
    update_state(run_dir, task_id, "initialized", {"Task Type": args.task_type, "Dry Run": args.dry_run})
    
    # Read final report template
    report_template_path = os.path.join(orchestrator_path, "orchestrator/templates/final_report_template.md")
    if os.path.exists(report_template_path):
        with open(report_template_path, 'r', encoding='utf-8') as f:
            report_template = f.read()
    else:
        report_template = "# Final Task Report\nStatus: {final_status}\n"

    # Execution Flow Variables
    final_status = "성공 (success)"
    execution_result = "성공 (success)"
    
    git_status = ""
    diff_stat = ""
    test_results = "N/A"
    changed_files = "변경 감지 안됨"
    remaining_risks = "없음"
    
    pytest_passed = True
    smoke_passed = True
    policy_passed = True
    
    task_weight_str = determine_task_weight(args.task_type, args.task_weight)
    excluded_names_str = ", ".join(excluded_agents.keys()) if excluded_agents else "없음"
    excluded_reasons_str = ", ".join([f"{k}: {v}" for k, v in excluded_agents.items()]) if excluded_agents else "없음"
    final_execution_agent = "N/A"

    # Fallback Variables
    fallback_occurred = "No"
    initial_agent = selected_agent if selected_agent else "N/A"
    failure_reason = "N/A"
    alternative_agent = "N/A"
    alternative_agent_result = "N/A"
    
    # Antigravity Review Variables
    antigravity_executed = "No"
    antigravity_result = "N/A"
    antigravity_review_file = "N/A"
    antigravity_verdict = "N/A"
    antigravity_opinion = "N/A"
    antigravity_next_step = "N/A"
    
    python_cmd = ".venv/bin/python" if os.path.exists(".venv/bin/python") else "python3"
    
    # Usage Limit Failover Detection Helper
    def detect_rate_limit(log_text):
        keywords = load_rate_limit_keywords()
        log_text_lower = log_text.lower()
        for kw in keywords:
            if kw in log_text_lower:
                return True, kw
        return False, None

    # Handoff Detection Flags
    trigger_fallback = False
    handoff_reason = ""
    
    # Usage Limit / Failover Template Variables (Defaults)
    auto_failover_used = "Yes" if args.auto_failover else "No"
    usage_limit_detected = "No"
    failover_failed_agent = "N/A"
    failover_failure_reason = "N/A"
    failover_state_change = "N/A"
    failover_alternative_agent = "N/A"
    failover_alternative_result = "N/A"
    all_agents_unavailable = "No"
    failover_final_status = "N/A"
    human_action_required = "No"
    
    fc_initial_agent = selected_agent if selected_agent else "N/A"
    fc_failure_reason = "N/A"
    fc_state_change = "N/A"
    fc_next_candidate = "N/A"
    fc_selection_reason = "N/A"
    fc_alternative_result = "N/A"
    fc_final_status = "N/A"
    
    failover_history_list = []
    completed_steps_list = []
    
    review_warning_needed = False
    
    current_agent = selected_agent
    last_attempt_agent = "N/A"
    last_attempt_reason = "N/A"
    
    next_reason = "N/A"
    
    # ------------------
    # Agent Execution Loop
    # ------------------
    max_attempts = 5
    attempt = 0
    
    if args.dry_run:
        print(f"[{datetime.now()}] Dry-run mode enabled. Skipping agent execution and test validation.")
        update_state(run_dir, task_id, "dry-run-initialized", {"Reason": "Dry run requested"})
        execution_result = "Skipped (dry-run)"
        completed_steps_list.append(f"{selected_agent if selected_agent else 'N/A'} (dry-run 실행 시도)")
        
        # dry-run 일 때도 smoke_report.sh를 --dry-run 옵션을 줘서 실행하여 SKIPPED 상태의 smoke_result.log 생성
        print(f"[{datetime.now()}] Running smoke_report validator in dry-run mode...")
        smoke_script = os.path.join(orchestrator_path, "orchestrator/validators/smoke_report.sh")
        subprocess.run(["bash", smoke_script, run_dir, "--dry-run"], capture_output=True, text=True, cwd=project_root)
        final_execution_agent = selected_agent if selected_agent else "N/A"
        
        # dry-run 상태에서 antigravity_prompt.md 생성 여부
        if args.with_antigravity_review:
            review_template_path = os.path.join(orchestrator_path, "orchestrator/templates/antigravity_review_prompt_template.md")
            if os.path.exists(review_template_path):
                with open(review_template_path, "r", encoding="utf-8") as rf:
                    review_prompt_content = rf.read()
            else:
                review_prompt_content = "# Antigravity Review Prompt\nReview dry-run.\n"
            with open(os.path.join(run_dir, "antigravity_prompt.md"), "w", encoding="utf-8") as apf:
                apf.write(review_prompt_content)
            antigravity_result = "Skipped (dry-run)"
            antigravity_opinion = "dry-run 모드이므로 리뷰 실행이 건너뛰어짐"
    else:
        # Real Execution Flow
        while current_agent and attempt < max_attempts:
            attempt += 1
            print(f"[{datetime.now()}] Attempt {attempt}: Executing agent '{current_agent}'")
            last_attempt_agent = current_agent
            final_execution_agent = current_agent
            
            # runner missing 시뮬레이션 체크
            is_simulated_missing = False
            if args.simulate_runner_missing and current_agent in args.simulate_runner_missing:
                is_simulated_missing = True
            if current_agent == "antigravity_cli" and args.simulate_antigravity_missing:
                is_simulated_missing = True
                
            # rate limit 시뮬레이션 체크
            is_simulated_rate_limit = False
            if args.simulate_rate_limit and current_agent == "claude_code":
                is_simulated_rate_limit = True
            if args.simulate_agent_rate_limit and current_agent in args.simulate_agent_rate_limit:
                is_simulated_rate_limit = True
                
            # agent error 시뮬레이션 체크
            is_simulated_error = False
            if args.simulate_claude_failure and current_agent == "claude_code":
                is_simulated_error = True
            if args.simulate_agent_error and current_agent in args.simulate_agent_error:
                is_simulated_error = True
            
            # 로그 파일 정의
            agent_log_path = os.path.join(run_dir, f"{current_agent}_output.log")
            if current_agent == "claude_code":
                agent_log_path = os.path.join(run_dir, "claude_output.log")
            elif current_agent == "codex_cli":
                agent_log_path = os.path.join(run_dir, "codex_output.log")
            elif current_agent == "antigravity_cli":
                agent_log_path = os.path.join(run_dir, "antigravity_output.log")
                
            agent_exit_code = 0
            completed_steps_list.append(f"{current_agent} 실행 시도")
            
            if is_simulated_missing:
                print(f"[{datetime.now()}] Simulating runner missing for {current_agent}...")
                with open(agent_log_path, "w", encoding="utf-8") as lf:
                    lf.write(f"Error: {current_agent} command not found. Runner is missing.\n")
                agent_exit_code = 127
            elif is_simulated_rate_limit:
                print(f"[{datetime.now()}] Simulating rate limit for {current_agent}...")
                with open(agent_log_path, "w", encoding="utf-8") as lf:
                    lf.write(f"Error: 429 too many requests. usage limit reached. rate limit exceeded.\n")
                agent_exit_code = 1
            elif is_simulated_error:
                print(f"[{datetime.now()}] Simulating execution error for {current_agent}...")
                with open(agent_log_path, "w", encoding="utf-8") as lf:
                    lf.write(f"Error: Agent execution failed randomly.\n")
                agent_exit_code = 1
            elif args.simulate_claude_success and current_agent == "claude_code":
                print(f"[{datetime.now()}] Simulating Claude runner success...")
                with open(agent_log_path, "w", encoding="utf-8") as lf:
                    lf.write("changed files:\n- README.md\n\nremaining risks:\n- None")
                agent_exit_code = 0
            else:
                # runner 실행
                runner_script = os.path.join(orchestrator_path, f"orchestrator/runners/run_{current_agent.split('_')[0]}.sh")
                if not os.path.exists(runner_script):
                    print(f"[{datetime.now()}] Warning: Runner script {runner_script} not found.")
                    with open(agent_log_path, "w", encoding="utf-8") as lf:
                        lf.write(f"Error: Runner script {runner_script} not found. Command not found.\n")
                    agent_exit_code = 127
                else:
                    print(f"[{datetime.now()}] Running {runner_script}...")
                    res = subprocess.run(["bash", runner_script, run_dir], capture_output=True, text=True, cwd=project_root)
                    agent_exit_code = res.returncode
                    if not os.path.exists(agent_log_path):
                        with open(agent_log_path, "w", encoding="utf-8") as lf:
                            lf.write(res.stdout + "\n" + res.stderr)
                            
            # 에러 감지 및 사용량 제한 감지
            log_content = ""
            if os.path.exists(agent_log_path):
                with open(agent_log_path, "r", encoding="utf-8") as lf:
                    log_content = lf.read()
                    
            is_rate_limited, matched_kw = detect_rate_limit(log_content)
            
            is_runner_missing = False
            if agent_exit_code == 127:
                is_runner_missing = True
            else:
                missing_kws = ["command not found", "not installed", "runner is missing", "no such file or directory"]
                log_content_lower = log_content.lower()
                for mkw in missing_kws:
                    if mkw in log_content_lower:
                        is_runner_missing = True
                        break
                        
            # 결과 분석 및 상태 변경
            if agent_exit_code == 0 and not is_rate_limited and not is_runner_missing:
                # 실행 성공
                print(f"[{datetime.now()}] Agent '{current_agent}' completed successfully.")
                execution_result = "Success"
                update_state(run_dir, task_id, f"completed-{current_agent.split('_')[0]}")
                
                # Antigravity 일 때의 처리
                if current_agent == "antigravity_cli":
                    antigravity_executed = "Yes"
                    antigravity_result = "Success"
                    review_file_path = os.path.join(run_dir, "antigravity_review.md")
                    if os.path.exists(review_file_path):
                        antigravity_review_file = "antigravity_review.md"
                        try:
                            with open(review_file_path, "r", encoding="utf-8") as rf:
                                review_text = rf.read()
                            v_match = re.search(r"##\s*\[?최종 판정\]?\s*\n*\s*(PASS|WARNING|FAIL)", review_text, re.IGNORECASE)
                            if v_match:
                                antigravity_verdict = v_match.group(1).upper()
                            o_match = re.search(r"## 판정 이유\s*\n*\s*(.*?)(?=\n##|\Z)", review_text, re.DOTALL)
                            if o_match:
                                antigravity_opinion = o_match.group(1).strip()
                            ns_match = re.search(r"## 다음 단계 진행 가능 여부\s*\n*\s*(가능|불가능)", review_text)
                            if ns_match:
                                antigravity_next_step = ns_match.group(1).strip()
                        except Exception as ex:
                            antigravity_opinion = f"리뷰 파일 파싱 중 에러: {ex}"
                    else:
                        review_warning_needed = True
                else:
                    # Coding Agent 실행 성공 시 검증 수행
                    if current_agent != selected_agent:
                        alternative_agent_result = "Success"
                        failover_alternative_result = "Success"
                        
                    if args.simulate_pytest_success:
                        print(f"[{datetime.now()}] Simulating pytest validation success...")
                        pytest_passed = True
                        update_state(run_dir, task_id, "passed-pytest")
                    else:
                        print(f"[{datetime.now()}] Running pytest validator...")
                        pytest_script = os.path.join(orchestrator_path, "orchestrator/validators/pytest.sh")
                        pytest_res = subprocess.run(["bash", pytest_script, run_dir], capture_output=True, text=True, cwd=project_root)
                        if pytest_res.returncode != 0:
                            print(f"[{datetime.now()}] pytest validation failed with code {pytest_res.returncode}")
                            pytest_passed = False
                            update_state(run_dir, task_id, "failed-pytest", {"Exit Code": pytest_res.returncode})
                        else:
                            print(f"[{datetime.now()}] pytest validation passed.")
                            update_state(run_dir, task_id, "passed-pytest")
                            
                    if args.simulate_smoke_success:
                        print(f"[{datetime.now()}] Simulating smoke_report validation success...")
                        smoke_result_path = os.path.join(run_dir, "smoke_result.log")
                        with open(smoke_result_path, "w", encoding="utf-8") as sf:
                            sf.write("상태: PASSED\n사유: 시뮬레이션 성공 통과\n")
                        smoke_passed = True
                        update_state(run_dir, task_id, "passed-smoke")
                    else:
                        print(f"[{datetime.now()}] Running smoke_report validator...")
                        smoke_script = os.path.join(orchestrator_path, "orchestrator/validators/smoke_report.sh")
                        smoke_res = subprocess.run(["bash", smoke_script, run_dir], capture_output=True, text=True, cwd=project_root)
                        if smoke_res.returncode != 0:
                            print(f"[{datetime.now()}] smoke_report validation failed with code {smoke_res.returncode}")
                            smoke_passed = False
                            update_state(run_dir, task_id, "failed-smoke", {"Exit Code": smoke_res.returncode})
                        else:
                            print(f"[{datetime.now()}] smoke_report completed successfully.")
                            update_state(run_dir, task_id, "passed-smoke")
            else:
                # 실행 실패 혹은 사용량 제한
                if is_rate_limited:
                    fail_type = "rate_limit"
                    new_state = "red"
                elif is_runner_missing:
                    fail_type = "runner_missing"
                    new_state = "black"
                else:
                    fail_type = "agent_error"
                    new_state = "red"
                    
                last_attempt_reason = fail_type
                print(f"[{datetime.now()}] Agent '{current_agent}' failed. Type: {fail_type}, state: {new_state}")
                
                # Antigravity CLI의 runner missing 예외 처리
                if current_agent == "antigravity_cli":
                    antigravity_executed = "Yes"
                    antigravity_result = f"Failed ({fail_type})"
                    antigravity_opinion = f"Antigravity 러너 실행 실패: {fail_type}"
                    review_warning_needed = True
                    update_agent_state_file(current_agent, new_state, new_error=fail_type, dry_run=args.dry_run, run_dir=run_dir)
                    set_states[current_agent] = new_state
                    break
                    
                # agent_status.yaml 업데이트
                status_dict = load_agent_status()
                prev_state = status_dict.get(current_agent, {}).get("quota_state", "green")
                update_agent_state_file(current_agent, new_state, new_error=fail_type, dry_run=args.dry_run, run_dir=run_dir)
                set_states[current_agent] = new_state
                
                # Template Variables 업데이트
                usage_limit_detected = "Yes" if fail_type == "rate_limit" else usage_limit_detected
                failover_failed_agent = current_agent
                failover_failure_reason = fail_type
                failover_state_change = f"{prev_state} -> {new_state}"
                
                if current_agent != selected_agent:
                    alternative_agent_result = f"Failed ({fail_type})"
                    failover_alternative_result = f"Failed ({fail_type})"
                    
                # auto-failover 동작 수행
                if args.auto_failover:
                    print(f"[{datetime.now()}] Auto-failover active. Routing next candidate...")
                    trigger_fallback = True
                    handoff_reason = fail_type
                    
                    next_agent, next_reason, next_excluded = route_agent(
                        task_type=args.task_type,
                        task_weight_opt=args.task_weight,
                        set_states=set_states,
                        run_dir=run_dir
                    )
                    
                    # failover chain 변수 채우기
                    fc_initial_agent = selected_agent
                    fc_failure_reason = fail_type
                    fc_state_change = f"{current_agent}: {prev_state} -> {new_state}"
                    fc_next_candidate = next_agent if next_agent else "None"
                    fc_selection_reason = next_reason
                    
                    curr_changed_files = "N/A"
                    if os.path.exists(os.path.join(run_dir, "git_status.txt")):
                        with open(os.path.join(run_dir, "git_status.txt"), "r", encoding="utf-8") as f:
                            curr_changed_files = f.read().strip()
                            
                    # next_action.md 생성 및 보강
                    next_action_path = os.path.join(run_dir, "next_action.md")
                    next_action_content = f"""# Next Action Report (이어받기 작업 명세)

- **이전 Agent가 중단된 이유**: {fail_type}
- **현재까지 생성된 파일**: {curr_changed_files if curr_changed_files else "없음"}
- **다음 Agent가 해야 할 작업**: requirement.md에 기재된 요구사항을 바탕으로 누락되거나 미진한 개발 영역을 계속 코딩하고 pytest 및 스모크 테스트 통과까지 완결할 것
- **주의 사항**:
  - 처음부터 다시 시작하지 말고 이전 Agent의 상태를 기반으로 점진적으로 이어서 진행할 것
  - 금지 파일 및 금지 명령어 정책을 반드시 지킬 것 (rm -rf, sudo, .env 등)
- **테스트 및 보고서 갱신 지시**:
  - 에이전트 수정 완료 후 pytest.sh 및 smoke_report.sh를 직접 구동하여 검증하라.
"""
                    with open(next_action_path, "w", encoding="utf-8") as naf:
                        naf.write(next_action_content)
                        
                    # state.md에 failover 이력 누적
                    timestamp_str = datetime.now().isoformat()
                    history_entry = f"""
## Failover 이력
- 발생 시각: {timestamp_str}
- 실패 Agent: {current_agent}
- 실패 사유: {fail_type}
- 이전 quota_state: {prev_state}
- 변경 quota_state: {new_state}
- 다음 Agent: {next_agent if next_agent else "None"}
- handoff 파일: next_action.md
- 다음 작업: next_action.md 기준으로 이어받기
"""
                    failover_history_list.append(history_entry)
                    update_state_handoff(run_dir, task_id, fail_type)
                    with open(os.path.join(run_dir, "state.md"), "a", encoding="utf-8") as sf:
                        sf.write(history_entry)
                        
                    if next_agent:
                        if next_agent == "codex_cli":
                            # codex_prompt.md 생성
                            codex_prompt_template_path = "orchestrator/templates/codex_prompt_template.md"
                            if os.path.exists(codex_prompt_template_path):
                                with open(codex_prompt_template_path, "r", encoding="utf-8") as cpf:
                                    codex_prompt_content = cpf.read()
                            else:
                                codex_prompt_content = "# Handoff Prompt\nFollow requirement.md and next_action.md.\n"
                            with open(os.path.join(run_dir, "codex_prompt.md"), "w", encoding="utf-8") as cpf:
                                cpf.write(codex_prompt_content)
                                
                        failover_alternative_agent = next_agent
                        current_agent = next_agent
                        fallback_occurred = "Yes"
                        alternative_agent = next_agent
                        continue
                    else:
                        print(f"[{datetime.now()}] No next candidate available. Terminating failover.")
                        all_agents_unavailable = "Yes"
                        current_agent = None
                        break
                else:
                    print(f"[{datetime.now()}] Auto-failover disabled. Stopping execution.")
                    current_agent = None
                    break

    # ------------------
    # Post-Execution: Antigravity Independent Review
    # ------------------
    is_failed_run = False
    if not args.dry_run and (last_attempt_agent == "N/A" or execution_result != "Success"):
        is_failed_run = True
        
    if review_warning_needed and last_attempt_agent == "antigravity_cli":
        is_failed_run = False
        
    if args.with_antigravity_review and antigravity_executed == "No":
        if not is_failed_run:
            antigravity_executed = "Yes"
            print(f"[{datetime.now()}] Antigravity independent review triggered...")
            review_template_path = os.path.join(orchestrator_path, "orchestrator/templates/antigravity_review_prompt_template.md")
            if os.path.exists(review_template_path):
                with open(review_template_path, "r", encoding="utf-8") as rf:
                    review_prompt_content = rf.read()
            else:
                review_prompt_content = "# Antigravity Review Prompt\nReview artifacts in run_dir.\n"
                
            with open(os.path.join(run_dir, "antigravity_prompt.md"), "w", encoding="utf-8") as apf:
                apf.write(review_prompt_content)
                
            if args.dry_run:
                antigravity_result = "Skipped (dry-run)"
                antigravity_opinion = "dry-run 모드이므로 리뷰 실행이 건너뛰어짐"
            else:
                is_ag_missing = False
                if args.simulate_antigravity_missing:
                    is_ag_missing = True
                if args.simulate_runner_missing and "antigravity_cli" in args.simulate_runner_missing:
                    is_ag_missing = True
                    
                if is_ag_missing:
                    print(f"[{datetime.now()}] Simulating Antigravity CLI missing...")
                    antigravity_result = "Skipped (runner_missing)"
                    antigravity_opinion = "Antigravity CLI 미설치 상태 시뮬레이션으로 리뷰 스킵"
                    with open(os.path.join(run_dir, "antigravity_output.log"), "w", encoding="utf-8") as alf:
                        alf.write("오류: 'antigravity' 명령어가 설치되어 있지 않거나 PATH에 존재하지 않습니다.\n")
                    review_warning_needed = True
                    update_agent_state_file("antigravity_cli", "black", new_error="runner_missing", dry_run=args.dry_run, run_dir=run_dir)
                    set_states["antigravity_cli"] = "black"
                else:
                    print(f"[{datetime.now()}] Executing Antigravity review runner...")
                    antigravity_script = os.path.join(orchestrator_path, "orchestrator/runners/run_antigravity.sh")
                    ag_res = subprocess.run(["bash", antigravity_script, run_dir], capture_output=True, text=True, cwd=project_root)
                    if ag_res.returncode != 0:
                        print(f"[{datetime.now()}] Antigravity review failed with code {ag_res.returncode}")
                        antigravity_result = f"Failed (exit code {ag_res.returncode})"
                        antigravity_opinion = f"Antigravity 러너 비정상 오류 종료 (Exit Code: {ag_res.returncode})"
                        review_warning_needed = True
                        
                        ag_fail_type = "runner_missing" if ag_res.returncode == 127 else "agent_error"
                        ag_state = "black" if ag_fail_type == "runner_missing" else "red"
                        update_agent_state_file("antigravity_cli", ag_state, new_error=ag_fail_type, dry_run=args.dry_run, run_dir=run_dir)
                        set_states["antigravity_cli"] = ag_state
                    else:
                        print(f"[{datetime.now()}] Antigravity review completed successfully.")
                        antigravity_result = "Success"
                        review_file_path = os.path.join(run_dir, "antigravity_review.md")
                        if os.path.exists(review_file_path):
                            antigravity_review_file = "antigravity_review.md"
                            try:
                                with open(review_file_path, "r", encoding="utf-8") as rf:
                                    review_text = rf.read()
                                v_match = re.search(r"##\s*\[?최종 판정\]?\s*\n*\s*(PASS|WARNING|FAIL)", review_text, re.IGNORECASE)
                                if v_match:
                                    antigravity_verdict = v_match.group(1).upper()
                                o_match = re.search(r"## 판정 이유\s*\n*\s*(.*?)(?=\n##|\Z)", review_text, re.DOTALL)
                                if o_match:
                                    antigravity_opinion = o_match.group(1).strip()
                                ns_match = re.search(r"## 다음 단계 진행 가능 여부\s*\n*\s*(가능|불가능)", review_text)
                                if ns_match:
                                    antigravity_next_step = ns_match.group(1).strip()
                            except Exception as ex:
                                antigravity_opinion = f"리뷰 파일 파싱 중 에러: {ex}"
                        else:
                            antigravity_opinion = "리뷰 실행 완료되었으나 antigravity_review.md 파일이 생성되지 않음"
                            review_warning_needed = True

    # ------------------
    # Post-Execution: Failure Report & Rerun Info
    # ------------------
    if not args.dry_run and is_failed_run:
        print(f"[{datetime.now()}] Task execution failed. Generating failure report...")
        final_status = "실패 (needs_human_review)"
        failover_final_status = final_status
        human_action_required = "Yes"
        
        failure_template_path = os.path.join(orchestrator_path, "orchestrator/templates/failure_report_template.md")
        if os.path.exists(failure_template_path):
            with open(failure_template_path, "r", encoding="utf-8") as ftf:
                failure_template = ftf.read()
        else:
            failure_template = "# Failure Report\nStage: {failure_stage}\nAgent: {failed_agent}\nReason: {failure_reason}\n"
            
        status_dict = load_agent_status()
        status_summary_lines = []
        for name, info in status_dict.items():
            curr_state = set_states.get(name) or info.get("quota_state", "green")
            status_summary_lines.append(f"  - {name}: {curr_state} (last_error: {info.get('last_error')})")
        agent_status_summary = "\n".join(status_summary_lines)
        
        completed_steps = "\n".join([f"  - {step}" for step in completed_steps_list])
        
        cmd_args = [python_cmd, "orchestrator/run_task.py", f"--task-type {args.task_type}"]
        if args.requirement:
            cmd_args.append(f'--requirement "{args.requirement}"')
        if args.use_agent_router:
            cmd_args.append("--use-agent-router")
        if args.auto_failover:
            cmd_args.append("--auto-failover")
        if args.enable_codex_fallback:
            cmd_args.append("--enable-codex-fallback")
        if args.with_antigravity_review:
            cmd_args.append("--with-antigravity-review")
        cmd_args.append(f"--reset-agent-state {last_attempt_agent}=green")
        rerun_command = " ".join(cmd_args)
        
        # Phase 7 failure summary log content
        summary_log_content = f"최종 실패 상태: {final_status}\n실패 원인: {last_attempt_reason if last_attempt_reason != 'N/A' else '모든 에이전트 사용 불가'}\n에이전트 이력: {', '.join(completed_steps_list)}"
        
        failure_report_content = fill_template(failure_template, {
            "failure_stage": f"{last_attempt_agent} 실행 단계",
            "failed_agent": last_attempt_agent,
            "failure_reason": last_attempt_reason if last_attempt_reason != "N/A" else "모든 에이전트 사용 불가",
            "agent_status_summary": agent_status_summary,
            "completed_steps": completed_steps,
            "remaining_tasks": "  - 요구사항 코딩 및 테스트 검증 수행\n  - 최종 산출물 진단 및 보고서 갱신",
            "human_actions": "  - 실패 원인(Rate Limit 등)을 파악하고 대기 또는 계정 교체\n  - --reset-agent-state 옵션으로 상태를 복구한 후 재실행 권장",
            "rerun_command": rerun_command,
            # Phase 7 추가 바인딩
            "state_change_summary": failover_state_change if failover_state_change != "N/A" else "변경 없음",
            "manual_action_required_flag": "Yes (수동 조치 필요)",
            "summary_log_content": summary_log_content
        })
        
        with open(os.path.join(run_dir, "failure_report.md"), "w", encoding="utf-8") as frf:
            frf.write(failure_report_content)

    # 8. Run check_diff.sh
    print(f"[{datetime.now()}] Running check_diff validator...")
    diff_script = os.path.join(orchestrator_path, "orchestrator/validators/check_diff.sh")
    diff_res = subprocess.run(["bash", diff_script, run_dir], capture_output=True, text=True, cwd=project_root)
    if diff_res.returncode != 0:
        print(f"[{datetime.now()}] check_diff validation failed with code {diff_res.returncode}")
        update_state(run_dir, task_id, "failed-check-diff", {"Exit Code": diff_res.returncode})
    else:
        print(f"[{datetime.now()}] check_diff completed successfully.")
 
    # 9. Run policy_check.py (check_diff 실행 후 실행)
    print(f"[{datetime.now()}] Running policy_check validator...")
    policy_script = os.path.join(orchestrator_path, "orchestrator/validators/policy_check.py")
    policy_res = subprocess.run([python_cmd, policy_script, run_dir], capture_output=True, text=True, cwd=project_root)
    if policy_res.returncode != 0:
        print(f"[{datetime.now()}] policy_check validation failed with code {policy_res.returncode}")
        policy_passed = False
        update_state(run_dir, task_id, "failed-policy-check", {"Exit Code": policy_res.returncode})
    else:
        print(f"[{datetime.now()}] policy_check completed successfully.")
        update_state(run_dir, task_id, "passed-policy-check")
 
    # Collect outputs for final report
    git_status_path = os.path.join(run_dir, "git_status.txt")
    if os.path.exists(git_status_path):
        with open(git_status_path, "r", encoding="utf-8") as f:
            git_status = f.read().strip()
             
    diff_stat_path = os.path.join(run_dir, "diff_stat.txt")
    if os.path.exists(diff_stat_path):
        with open(diff_stat_path, "r", encoding="utf-8") as f:
            diff_stat = f.read().strip()
 
    # smoke_result.log에서 상태 및 사유 파싱
    smoke_status = "SKIPPED"
    smoke_reason = "스모크 테스트가 수행되지 않았습니다."
    smoke_result_path = os.path.join(run_dir, "smoke_result.log")
    if os.path.exists(smoke_result_path):
        with open(smoke_result_path, "r", encoding="utf-8") as sf:
            for line in sf:
                if line.startswith("상태:"):
                    smoke_status = line.replace("상태:", "").strip()
                elif line.startswith("사유:"):
                    smoke_reason = line.replace("사유:", "").strip()
 
    # 테스트 로그 및 변경 파일 설정
    changed_files = "변경 감지 안됨"
    remaining_risks = "없음"
    test_results = "N/A"
    
    if args.dry_run:
        test_results = "N/A (dry-run)"
        changed_files = "N/A (dry-run)"
        remaining_risks = "N/A (dry-run)"
    else:
        test_result_path = os.path.join(run_dir, "test_result.log")
        if os.path.exists(test_result_path):
            with open(test_result_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                test_results = "".join(lines[-50:]).strip()
 
        if os.path.exists(smoke_result_path):
            with open(smoke_result_path, "r", encoding="utf-8") as f:
                smoke_content = f.read().strip()
                test_results += "\n\n[스모크 테스트 결과]\n" + smoke_content
 
        # Try parsing outputs for changed files
        claude_log_path = os.path.join(run_dir, "claude_output.log")
        if os.path.exists(claude_log_path):
            with open(claude_log_path, "r", encoding="utf-8") as f:
                claude_output = f.read()
            parsed_changed = extract_section(claude_output, "changed files")
            if parsed_changed:
                changed_files = parsed_changed
            else:
                changed_files = git_status if git_status else "변경 감지 안됨"
                 
            parsed_risks = extract_section(claude_output, "remaining risks")
            if parsed_risks:
                remaining_risks = parsed_risks
            else:
                remaining_risks = "없음"
         
        # Codex 로그 반영 분기
        codex_log_path = os.path.join(run_dir, "codex_output.log")
        if os.path.exists(codex_log_path):
            with open(codex_log_path, "r", encoding="utf-8") as f:
                codex_output = f.read()
            parsed_changed_codex = extract_section(codex_output, "변경 파일")
            if parsed_changed_codex:
                changed_files += f"\n[Codex 변경 파일]\n{parsed_changed_codex}"
            parsed_risks_codex = extract_section(codex_output, "남은 리스크")
            if parsed_risks_codex:
                remaining_risks += f"\n[Codex 남은 리스크]\n{parsed_risks_codex}"

    # 11. 최종 판정 로직
    validation_status = []
     
    if not args.dry_run:
        if selected_agent is None:
            validation_status.append("사용 가능한 에이전트 후보가 없음 (모든 후보가 제외되거나 없음)")
        if trigger_fallback:
            if not args.enable_codex_fallback and not args.auto_failover:
                validation_status.append("에이전트 실행 실패 (Codex Fallback/Auto-failover 비활성)")
            elif alternative_agent_result.startswith("Failed") or alternative_agent_result == "N/A":
                validation_status.append(f"에이전트 실행 실패 (대체 에이전트 실패: {alternative_agent_result})")
         
        if not pytest_passed:
            validation_status.append("단위 테스트(pytest) 실패")
        if smoke_status == "FAILED" or not smoke_passed:
            validation_status.append("스모크 테스트 실패")
        if is_failed_run:
            validation_status.append("에이전트 실행 실패")
             
    if not policy_passed:
        validation_status.append("파일/경로 정책 위반")
 
    # 상태 문자열 설정
    if validation_status:
        final_status = "실패 (needs_human_review)"
        print(f"[{datetime.now()}] 검증 실패 사항 감지: {', '.join(validation_status)}")
    elif review_warning_needed:
        final_status = "성공 (warning: antigravity_review_missing)"
        print(f"[{datetime.now()}] 작업 성공했으나 Antigravity 독립 리뷰 누락/에러가 감지되었습니다. (Warning 경고 처리)")
    elif args.dry_run:
        final_status = "성공 (dry-run)"
    else:
        final_status = "성공 (success)"
        
    fc_final_status = final_status
    failover_final_status = final_status
    
    # Phase 7 추가 템플릿 바인딩 값 준비
    autorun_used = "Yes" if args.auto_run else "No"
    router_used_p7 = "Yes" if args.use_agent_router else "No"
    autofailover_used_p7 = "Yes" if args.auto_failover else "No"
    antigravity_review_used_p7 = "Yes" if args.with_antigravity_review else "No"
    final_status_p7 = final_status
    human_action_required_p7 = "Yes" if validation_status or is_failed_run or all_agents_unavailable == "Yes" else "No"
    
    major_points_p7 = "작업이 성공적으로 검증 및 완료되었습니다." if final_status.startswith("성공") else "작업 검증 혹은 에이전트 실행 과정에서 실패가 발견되었습니다."
    if review_warning_needed:
        major_points_p7 = "작업은 성공했으나 Antigravity 독립 리뷰가 스킵되거나 완료되지 않아 warning이 감지되었습니다."
        
    changed_files_p7 = changed_files
    
    validation_results_list = []
    validation_results_list.append(f"pytest: {'PASSED' if pytest_passed else 'FAILED' if not args.dry_run else 'SKIPPED'}")
    validation_results_list.append(f"smoke_report: {smoke_status}")
    validation_results_list.append(f"policy_check: {'PASSED' if policy_passed else 'FAILED'}")
    validation_results_list.append(f"final_report_check: PENDING")
    validation_results_list.append(f"Antigravity review: {antigravity_verdict if antigravity_executed == 'Yes' else 'SKIPPED'}")
    validation_results_p7 = ", ".join(validation_results_list)
    
    remaining_risks_p7 = remaining_risks
    next_action_p7 = "다음 단계 작업을 이어서 진행하시기 바랍니다." if final_status in ["성공 (success)", "성공 (dry-run)"] else "오류를 해결하거나 수동 조치 후 재실행을 권장합니다."
 
    # failover chain 파일 작성
    failover_chain_content = f"""## Failover Chain
1. 최초 Agent: {fc_initial_agent}
2. 실패 사유: {fc_failure_reason}
3. 상태 전환: {fc_state_change}
4. 다음 후보 Agent: {fc_next_candidate}
5. 선택 사유: {fc_selection_reason}
6. 대체 Agent 실행 결과: {fc_alternative_result}
7. 최종 상태: {fc_final_status}"""

    with open(os.path.join(run_dir, "failover_chain.md"), "w", encoding="utf-8") as fcf:
        fcf.write(failover_chain_content + "\n")

    # final_report.md 작성
    final_report = fill_template(report_template, {
        "task_id": task_id,
        "requirement": requirement_content,
        "task_type": args.task_type,
        "execution_agent": selected_agent if selected_agent else "None",
        "execution_result": execution_result,
        "changed_files": changed_files,
        "test_results": test_results,
        "diff_summary": diff_stat if diff_stat else "수집된 diff 통계 없음",
        "remaining_risks": remaining_risks,
        "smoke_status": smoke_status,
        "smoke_reason": smoke_reason,
        "fallback_occurred": fallback_occurred,
        "initial_agent": initial_agent,
        "failure_reason": failure_reason,
        "alternative_agent": alternative_agent,
        "alternative_agent_result": alternative_agent_result,
        "antigravity_executed": antigravity_executed,
        "antigravity_result": antigravity_result,
        "antigravity_review_file": antigravity_review_file,
        "antigravity_verdict": antigravity_verdict,
        "antigravity_opinion": antigravity_opinion,
        "antigravity_next_step": antigravity_next_step,
        "final_status": final_status,
        "router_used": router_used,
        "task_weight": task_weight_str,
        "selected_agent": selected_agent if selected_agent else "None",
        "selection_reason": selection_reason,
        "excluded_agents_names": excluded_names_str,
        "excluded_agents_reasons": excluded_reasons_str,
        "final_execution_agent": final_execution_agent,
        # Phase 6
        "auto_failover_used": auto_failover_used,
        "usage_limit_detected": usage_limit_detected,
        "failover_failed_agent": failover_failed_agent,
        "failover_failure_reason": failover_failure_reason,
        "failover_state_change": failover_state_change,
        "failover_alternative_agent": failover_alternative_agent,
        "failover_alternative_result": failover_alternative_result,
        "all_agents_unavailable": all_agents_unavailable,
        "failover_final_status": failover_final_status,
        "human_action_required": "Yes" if is_failed_run or all_agents_unavailable == "Yes" else "No",
        "fc_initial_agent": fc_initial_agent,
        "fc_failure_reason": fc_failure_reason,
        "fc_state_change": fc_state_change,
        "fc_next_candidate": fc_next_candidate,
        "fc_selection_reason": fc_selection_reason,
        "fc_alternative_result": fc_alternative_result,
        "fc_final_status": fc_final_status,
        # Phase 7
        "autorun_used": autorun_used,
        "task_type_auto_classified": task_type_auto_classified,
        "classified_task_type": classified_task_type,
        "classified_task_weight": classified_task_weight,
        "router_used_p7": router_used_p7,
        "autofailover_used_p7": autofailover_used_p7,
        "antigravity_review_used_p7": antigravity_review_used_p7,
        "final_status_p7": final_status_p7,
        "human_action_required_p7": human_action_required_p7,
        "major_points_p7": major_points_p7,
        "changed_files_p7": changed_files_p7,
        "validation_results_p7": validation_results_p7,
        "remaining_risks_p7": remaining_risks_p7,
        "next_action_p7": next_action_p7
    })
 
    with open(os.path.join(run_dir, "final_report.md"), "w", encoding="utf-8") as f:
        f.write(final_report)

    # 12. Run final_report_check.py
    print(f"[{datetime.now()}] Running final_report_check validator...")
    report_check_script = os.path.join(orchestrator_path, "orchestrator/validators/final_report_check.py")
    report_check_res = subprocess.run([python_cmd, report_check_script, run_dir], capture_output=True, text=True, cwd=project_root)
    report_check_passed = "PASSED" if report_check_res.returncode == 0 else "FAILED"
    
    if report_check_res.returncode != 0:
        print(f"[{datetime.now()}] final_report_check failed with code {report_check_res.returncode}")
        final_status = "실패 (needs_human_review)"
        final_report = fill_template(report_template, {
            "task_id": task_id,
            "requirement": requirement_content,
            "task_type": args.task_type,
            "execution_agent": selected_agent if selected_agent else "None",
            "execution_result": execution_result,
            "changed_files": changed_files,
            "test_results": test_results,
            "diff_summary": diff_stat if diff_stat else "수집된 diff 통계 없음",
            "remaining_risks": remaining_risks,
            "smoke_status": smoke_status,
            "smoke_reason": smoke_reason,
            "fallback_occurred": fallback_occurred,
            "initial_agent": initial_agent,
            "failure_reason": failure_reason,
            "alternative_agent": alternative_agent,
            "alternative_agent_result": alternative_agent_result,
            "antigravity_executed": antigravity_executed,
            "antigravity_result": antigravity_result,
            "antigravity_review_file": antigravity_review_file,
            "antigravity_verdict": antigravity_verdict,
            "antigravity_opinion": antigravity_opinion,
            "antigravity_next_step": antigravity_next_step,
            "final_status": final_status,
            "router_used": router_used,
            "task_weight": task_weight_str,
            "selected_agent": selected_agent if selected_agent else "None",
            "selection_reason": selection_reason,
            "excluded_agents_names": excluded_names_str,
            "excluded_agents_reasons": excluded_reasons_str,
            "final_execution_agent": final_execution_agent,
            # Phase 6
            "auto_failover_used": auto_failover_used,
            "usage_limit_detected": usage_limit_detected,
            "failover_failed_agent": failover_failed_agent,
            "failover_failure_reason": failover_failure_reason,
            "failover_state_change": failover_state_change,
            "failover_alternative_agent": failover_alternative_agent,
            "failover_alternative_result": failover_alternative_result,
            "all_agents_unavailable": all_agents_unavailable,
            "failover_final_status": failover_final_status,
            "human_action_required": "Yes" if is_failed_run or all_agents_unavailable == "Yes" else "No",
            "fc_initial_agent": fc_initial_agent,
            "fc_failure_reason": fc_failure_reason,
            "fc_state_change": fc_state_change,
            "fc_next_candidate": fc_next_candidate,
            "fc_selection_reason": fc_selection_reason,
            "fc_alternative_result": fc_alternative_result,
            "fc_final_status": fc_final_status,
            # Phase 7
            "autorun_used": autorun_used,
            "task_type_auto_classified": task_type_auto_classified,
            "classified_task_type": classified_task_type,
            "classified_task_weight": classified_task_weight,
            "router_used_p7": router_used_p7,
            "autofailover_used_p7": autofailover_used_p7,
            "antigravity_review_used_p7": antigravity_review_used_p7,
            "final_status_p7": final_status,
            "human_action_required_p7": "Yes",
            "major_points_p7": major_points_p7,
            "changed_files_p7": changed_files_p7,
            "validation_results_p7": validation_results_p7.replace("PENDING", report_check_passed),
            "remaining_risks_p7": remaining_risks_p7,
            "next_action_p7": next_action_p7
        })
        final_report = final_report.replace("성공 (dry-run)", final_status).replace("성공 (success)", final_status).replace("성공 (warning: antigravity_review_missing)", final_status)
        with open(os.path.join(run_dir, "final_report.md"), "w", encoding="utf-8") as f:
            f.write(final_report)
        update_state(run_dir, task_id, "failed-report-check", {"Exit Code": report_check_res.returncode})
    else:
        print(f"[{datetime.now()}] final_report_check completed successfully.")
        update_state(run_dir, task_id, "passed-report-check")
        
    # Phase 7: operation_summary.md 생성
    summary_template_path = os.path.join(orchestrator_path, "orchestrator/templates/operation_summary_template.md")
    if os.path.exists(summary_template_path):
        with open(summary_template_path, "r", encoding="utf-8") as stf:
            summary_template = stf.read()
            
        final_verdict = "PASS"
        if final_status.startswith("성공 (warning"):
            final_verdict = "WARNING"
        elif final_status == "실패 (needs_human_review)":
            final_verdict = "NEEDS_HUMAN_REVIEW"
        elif not final_status.startswith("성공"):
            final_verdict = "FAIL"
            
        summary_next_step = "다음 단계 진행 가능"
        if final_verdict in ["WARNING", "NEEDS_HUMAN_REVIEW", "FAIL"]:
            summary_next_step = "보류 / 수동 확인 필요"
            
        one_line_summary = f"{classified_task_type} 태스크가 {classified_task_weight} 가중치로 자동 실행 완료되었습니다."
        if task_type_auto_classified == "No":
            one_line_summary = f"수동 지정된 {classified_task_type} 태스크가 실행 완료되었습니다."
            
        major_points_text = "특별히 수동 확인이 필요한 사항은 없습니다."
        if final_verdict == "WARNING":
            major_points_text = "Antigravity 독립 리뷰가 스킵되거나 누락되었습니다. 보고서를 확인하여 조치하십시오."
        elif final_verdict in ["FAIL", "NEEDS_HUMAN_REVIEW"]:
            major_points_text = "에이전트 실행 실패 또는 검증 오류가 감지되었습니다. failure_report.md를 확인하십시오."
            
        summary_content = fill_template(summary_template, {
            "final_verdict": final_verdict,
            "one_line_summary": one_line_summary,
            "major_points": major_points_text,
            "pytest_result": "PASSED" if pytest_passed else "FAILED" if not args.dry_run else "SKIPPED",
            "smoke_report_result": smoke_status,
            "policy_check_result": "PASSED" if policy_passed else "FAILED",
            "final_report_check_result": report_check_passed,
            "antigravity_review_result": antigravity_verdict if antigravity_executed == "Yes" else "SKIPPED",
            "next_step": summary_next_step
        })
        
        with open(os.path.join(run_dir, "operation_summary.md"), "w", encoding="utf-8") as osf:
            osf.write(summary_content)
 
    if final_status.startswith("성공"):
        if fallback_occurred == "Yes":
            update_state(run_dir, task_id, "completed", {
                "최종 상태": final_status,
                "대체 Agent": alternative_agent,
                "이력": f"{initial_agent} 실패 -> {alternative_agent} 대체 성공"
            })
            if failover_history_list:
                with open(os.path.join(run_dir, "state.md"), "a", encoding="utf-8") as sf:
                    sf.write("\n" + "".join(failover_history_list))
        else:
            update_state(run_dir, task_id, "completed", {"최종 상태": final_status})
            if failover_history_list:
                with open(os.path.join(run_dir, "state.md"), "a", encoding="utf-8") as sf:
                    sf.write("\n" + "".join(failover_history_list))
    else:
        if fallback_occurred == "Yes":
            timestamp = datetime.now().isoformat()
            lines = [
                f"# Task State: {task_id}",
                "",
                f"- **Status**: failed-after-handoff",
                f"- **Last Updated**: {timestamp}",
                "",
                "## 현재 진행 상태",
                f"{initial_agent} 실행 중 실패 또는 사용량 제한 감지 후 {alternative_agent} 대체 실행했으나 실패",
                "",
                "## 마지막 Agent",
                f"{last_attempt_agent} ({initial_agent}에서 handoff)",
                "",
                "## Handoff Reason",
                failure_reason,
                "",
                "## 실패 원인",
                ", ".join(validation_status) if validation_status else "보고서 구조 및 결과 정합성 위배"
            ]
            if failover_history_list:
                lines.append("".join(failover_history_list))
            with open(os.path.join(run_dir, "state.md"), "w", encoding="utf-8") as sf:
                sf.write("\n".join(lines))
        else:
            update_state(run_dir, task_id, "failed", {"최종 상태": final_status, "실패 원인": ", ".join(validation_status) if validation_status else "보고서 구조 및 결과 정합성 위배"})
            if failover_history_list:
                with open(os.path.join(run_dir, "state.md"), "a", encoding="utf-8") as sf:
                    sf.write("\n" + "".join(failover_history_list))
 
    print(f"[{datetime.now()}] Task {task_id} execution finished. Final status: {final_status}")

if __name__ == "__main__":
    main()
