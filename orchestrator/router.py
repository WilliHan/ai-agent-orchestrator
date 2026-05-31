import os
import yaml
from datetime import datetime

# Common repo installation path root
orchestrator_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Phase 7: Support auto-task classification and agent selection routing integration

def determine_task_weight(task_type, weight_opt=None):
    if weight_opt:
        return weight_opt
        
    defaults = {
        "documentation": "light",
        "test_fix": "medium",
        "python_code_fix": "medium",
        "refactor": "heavy",
        "large_context_review": "heavy",
        "final_review": "light",
        "auto": "medium"
    }
    return defaults.get(task_type, "medium")

def route_agent(task_type, task_weight_opt=None, set_states=None, run_dir=None):
    """
    Agent Pool Router 로직
    반환값: (selected_agent, selection_reason, excluded_agents_dict)
    """
    set_states = set_states or {}
    
    # 1. Load agent_status.yaml
    status_path = os.path.join(orchestrator_path, "orchestrator/agent_status.yaml")
    if os.path.exists(status_path):
        with open(status_path, "r", encoding="utf-8") as f:
            agent_status = yaml.safe_load(f) or {}
    else:
        agent_status = {}

    # 2. Load agent_policy.yaml
    policy_path = os.path.join(orchestrator_path, "orchestrator/policies/agent_policy.yaml")
    if os.path.exists(policy_path):
        with open(policy_path, "r", encoding="utf-8") as f:
            agent_policy = yaml.safe_load(f) or {}
    else:
        agent_policy = {}

    task_weight = determine_task_weight(task_type, task_weight_opt)

    # 3. Determine Candidate List from routing table
    routing_table = agent_policy.get("routing", {})
    route_info = routing_table.get(task_type, {})
    
    candidates = []
    primary = route_info.get("primary")
    if primary:
        candidates.append(primary)
    fallback_list = route_info.get("fallback", [])
    for fb in fallback_list:
        if fb not in candidates:
            candidates.append(fb)

    # If routing table has no entry, check general role matching (fallback logic)
    if not candidates:
        # Fallback to scanning all agents matching roles
        for name, info in agent_status.items():
            roles = info.get("role", [])
            if task_type in roles:
                candidates.append(name)

    excluded_agents = {}
    selected_agent = None
    selection_reason = ""
    
    # Filter candidates
    active_candidates = []
    for agent in candidates:
        # State override for testing
        state = set_states.get(agent) or agent_status.get(agent, {}).get("quota_state", "green")
        enabled = agent_status.get(agent, {}).get("enabled", True)
        quality_score = agent_status.get(agent, {}).get("quality_score", 0.0)
        
        # Check enabled
        if not enabled:
            excluded_agents[agent] = "비활성화 상태 (enabled=false)"
            continue
            
        # Check red/black
        if state in ["red", "black"]:
            excluded_agents[agent] = f"배정 금지 상태 (quota_state: {state})"
            continue
            
        # Check yellow + heavy
        if task_weight == "heavy" and state == "yellow":
            excluded_agents[agent] = "heavy 작업에는 yellow 상태의 에이전트를 배정할 수 없음"
            continue
            
        # Check quality score
        min_quality = agent_policy.get("agent_selection_policy", {}).get("min_quality_score", 0.70)
        if quality_score < min_quality:
            excluded_agents[agent] = f"품질 점수({quality_score})가 최소 기준({min_quality}) 미만임"
            continue
            
        # Antigravity review_only 보호 (코딩 작업일 때 antigravity는 primary coding agent 배정 금지)
        coding_tasks = ["documentation", "python_code_fix", "test_fix", "refactor", "auto"]
        if task_type in coding_tasks and agent == "antigravity_cli":
            excluded_agents[agent] = "Antigravity는 코딩 작업 유형에 primary coding agent로 배정될 수 없음 (review_only)"
            continue

        active_candidates.append(agent)

    # Select the first candidate remaining in prioritized list
    if active_candidates:
        selected_agent = active_candidates[0]
        # Determine if it's primary or fallback
        if selected_agent == primary:
            selection_reason = f"{task_type}의 primary 에이전트이고 quota_state가 정상임"
        else:
            selection_reason = f"{task_type}의 fallback 후보 중 우선순위가 가장 높고 quota_state가 정상임"
    else:
        selected_agent = None
        selection_reason = "사용 가능한 에이전트 후보가 없음 (모든 후보가 제외되거나 없음)"

    # 4. Record agent_selection.log
    if run_dir:
        log_path = os.path.join(run_dir, "agent_selection.log")
        os.makedirs(run_dir, exist_ok=True)
        
        # Prepare Agent status representation for log
        status_representation = []
        for name, info in agent_status.items():
            curr_state = set_states.get(name) or info.get("quota_state", "green")
            status_representation.append(f"{name}: {curr_state} (enabled: {info.get('enabled', True)}, quality: {info.get('quality_score', 0.0)})")
            
        log_lines = [
            "=== 에이전트 라우팅 결정 기록 ===",
            f"일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"작업 유형 (task_type): {task_type}",
            f"작업 무게 (task_weight): {task_weight}",
            f"우선순위 후보 목록: {', '.join(candidates) if candidates else '없음'}",
            f"전체 에이전트 상태: {', '.join(status_representation)}",
            "",
            "## 제외된 에이전트 목록 및 사유:"
        ]
        
        if excluded_agents:
            for k, v in excluded_agents.items():
                log_lines.append(f"- {k}: {v}")
        else:
            log_lines.append("- 없음")
            
        log_lines.extend([
            "",
            f"## 최종 선택 에이전트: {selected_agent if selected_agent else '선택 불가 (N/A)'}",
            f"선택 사유: {selection_reason}"
        ])
        
        with open(log_path, "w", encoding="utf-8") as lf:
            lf.write("\n".join(log_lines) + "\n")

    return selected_agent, selection_reason, excluded_agents

def save_agent_status(status_dict, dest_path):
    with open(dest_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(status_dict, f, default_flow_style=False, allow_unicode=True)

def load_agent_status():
    status_path = os.path.join(orchestrator_path, "orchestrator/agent_status.yaml")
    if os.path.exists(status_path):
        with open(status_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def update_agent_state_file(agent_name, new_state, new_error=None, dry_run=False, run_dir=None):
    status_dict = load_agent_status()
    
    if run_dir:
        before_path = os.path.join(run_dir, "agent_status_before.yaml")
        save_agent_status(status_dict, before_path)
        
    if agent_name in status_dict:
        status_dict[agent_name]["quota_state"] = new_state
        status_dict[agent_name]["last_error"] = new_error
        if new_state in ["red", "black"]:
            status_dict[agent_name]["cooldown_until"] = datetime.now().isoformat()
        else:
            status_dict[agent_name]["cooldown_until"] = None
            
    if run_dir:
        after_path = os.path.join(run_dir, "agent_status_after.yaml")
        save_agent_status(status_dict, after_path)
        
    if not dry_run:
        save_agent_status(status_dict, os.path.join(orchestrator_path, "orchestrator/agent_status.yaml"))
