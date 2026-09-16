import os
import subprocess
from pathlib import Path
from app.config import settings

class MCPTools:
    def __init__(self, repo_path: str | None = None):
        self.repo_path = Path(repo_path or settings.TARGET_REPO_PATH).resolve()
        if not (self.repo_path / ".git").exists() and self.repo_path.exists():
            try:
                subprocess.run(["git", "init"], cwd=str(self.repo_path), capture_output=True)
                subprocess.run(["git", "config", "user.name", "AI Agent"], cwd=str(self.repo_path), capture_output=True)
                subprocess.run(["git", "config", "user.email", "agent@openproject.local"], cwd=str(self.repo_path), capture_output=True)
                subprocess.run(["git", "add", "-A"], cwd=str(self.repo_path), capture_output=True)
                subprocess.run(["git", "commit", "-m", "initial commit"], cwd=str(self.repo_path), capture_output=True)
            except Exception:
                pass

    def _resolve_safe_path(self, rel_or_abs: str) -> Path:
        target = Path(rel_or_abs)
        if not target.is_absolute():
            target = (self.repo_path / rel_or_abs).resolve()
        # Security check to prevent directory traversal outside repo
        if not str(target).startswith(str(self.repo_path)):
            raise ValueError(f"Path '{rel_or_abs}' is outside the target repository boundary.")
        return target

    def read_file(self, path: str) -> dict:
        try:
            target_path = self._resolve_safe_path(path)
            if not target_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            content = target_path.read_text(encoding="utf-8", errors="replace")
            return {"success": True, "content": content, "path": str(target_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_code(self, query: str, subpath: str = ".") -> dict:
        try:
            search_dir = self._resolve_safe_path(subpath)
            matches = []
            for root, _, files in os.walk(search_dir):
                if ".git" in root or "__pycache__" in root or ".pytest_cache" in root:
                    continue
                for file in files:
                    if file.endswith((".py", ".json", ".md", ".txt", ".yaml", ".yml", ".toml", ".ini")):
                        file_path = Path(root) / file
                        try:
                            lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
                            for idx, line in enumerate(lines, start=1):
                                if query.lower() in line.lower():
                                    matches.append({
                                        "file": str(file_path.relative_to(self.repo_path)).replace("\\", "/"),
                                        "line_number": idx,
                                        "line_content": line.strip()
                                    })
                        except Exception:
                            continue
            return {"success": True, "query": query, "count": len(matches), "matches": matches}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, path: str, content: str) -> dict:
        try:
            target_path = self._resolve_safe_path(path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding="utf-8")
            return {"success": True, "path": str(target_path.relative_to(self.repo_path)).replace("\\", "/")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_tests(self, test_command: str = "python -m pytest -v", cwd: str | None = None) -> dict:
        working_dir = str(self._resolve_safe_path(cwd) if cwd else self.repo_path)
        try:
            # Run command in working directory
            process = subprocess.run(
                test_command,
                cwd=working_dir,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "success": process.returncode == 0,
                "exit_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "passed": process.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": "Test execution timed out after 60s", "passed": False}
        except Exception as e:
            return {"success": False, "exit_code": -1, "stdout": "", "stderr": str(e), "passed": False}

    def git_status(self) -> dict:
        try:
            branch_proc = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            branch = branch_proc.stdout.strip()

            status_proc = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            files = [line.strip() for line in status_proc.stdout.splitlines() if line.strip()]
            return {
                "success": True,
                "current_branch": branch,
                "modified_files": files,
                "is_dirty": len(files) > 0
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def git_create_branch(self, branch_name: str) -> dict:
        try:
            # Checkout or create
            res = subprocess.run(
                ["git", "checkout", "-B", branch_name],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            if res.returncode == 0:
                return {"success": True, "branch": branch_name}
            return {"success": False, "error": res.stderr or res.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def git_commit(self, message: str) -> dict:
        try:
            # Stage all changes
            add_res = subprocess.run(
                ["git", "add", "-A"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            if add_res.returncode != 0:
                return {"success": False, "error": f"Failed to git add: {add_res.stderr}"}

            # Commit
            commit_res = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            if commit_res.returncode != 0 and "nothing to commit" not in commit_res.stdout:
                return {"success": False, "error": commit_res.stderr or commit_res.stdout}

            # Get latest commit hash
            rev_proc = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            commit_hash = rev_proc.stdout.strip()
            return {
                "success": True,
                "commit_hash": commit_hash,
                "message": message
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def git_diff(self, branch: str = "HEAD~1") -> dict:
        try:
            diff_proc = subprocess.run(
                ["git", "diff", branch],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            return {"success": True, "diff": diff_proc.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

default_mcp_tools = MCPTools()
