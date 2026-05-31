# Claude Execution Prompt

## 1. Requirement
{requirement}

## 2. Rules and Constraints
* You MUST read and follow the rules defined in the following files before making changes:
  - [AGENTS.md](file:///home/mhhan/projects/wt/260416-work/AGENTS.md)
  - [AI_RULES.md](file:///home/mhhan/projects/wt/260416-work/AI_RULES.md)
  - [VALIDATION.md](file:///home/mhhan/projects/wt/260416-work/VALIDATION.md)

* **Forbidden Files & Commands**:
  - Never edit `.env` or `analysis.db`.
  - Do not delete past reports under `reports/`.
  - Do not use commands: `git reset --hard`, `git clean`, `rm -rf`, `sudo`.
  - Never report task completion while tests are failing.

## 3. Required Output
Please provide the final output in the following structure:
* **changed files**: A list of paths of all files created or modified.
* **summary**: A detailed description of the changes made and the implementation logic.
* **test command used**: The command(s) run to verify the changes.
* **remaining risks**: Any potential side-effects, risks, or untested parts.
