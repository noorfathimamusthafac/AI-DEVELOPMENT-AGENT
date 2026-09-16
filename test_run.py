import sys
import httpx
import time

# Set utf-8 encoding for standard output
sys.stdout.reconfigure(encoding='utf-8')

# 1. Authenticate as Developer
res = httpx.post("http://127.0.0.1:8000/api/auth/login", json={"email": "dev@example.com", "password": "password123"})
assert res.status_code == 200, f"Login failed: {res.text}"
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("[OK] Logged in successfully as Developer")

# 2. Reset demo to fresh state
reset_res = httpx.post("http://127.0.0.1:8000/api/agent/reset_demo", headers=headers)
print(f"[OK] Demo reset status: {reset_res.json().get('message')}")

# 3. Trigger Agent Run on BUG-101
run_res = httpx.post("http://127.0.0.1:8000/api/agent/run/BUG-101", headers=headers)
assert run_res.status_code == 200, f"Run start failed: {run_res.text}"
run_data = run_res.json()
run_id = run_data["run_id"]
print(f"[OK] Started Agent Run #{run_id} on {run_data['ticket_id']}")

# 4. Monitor execution steps
print("[INFO] Waiting for autonomous 10-step execution...")
for i in range(25):
    time.sleep(1)
    status_res = httpx.get(f"http://127.0.0.1:8000/api/agent/runs/{run_id}", headers=headers)
    data = status_res.json()
    status = data.get("status")
    logs = data.get("logs", [])
    if logs:
        last_step = logs[-1]
        print(f"    Step ({len(logs)}/10): {last_step['step']} -> [{last_step['status'].upper()}] {last_step['message'][:60]}...")
    if status in ("completed", "failed"):
        print(f"\n[OK] Run reached terminal state: {status.upper()}")
        print(f"    Branch created: {data.get('branch_name')}")
        print(f"    Commit hash:    {data.get('commit_hash')}")
        print(f"    Summary:        {data.get('summary')}")
        break

# 5. Check work package status in OpenProject
pkg_res = httpx.get("http://127.0.0.1:8000/api/openproject/work_packages/BUG-101", headers=headers)
pkg = pkg_res.json()
print(f"[OK] OpenProject ticket BUG-101 status is now: {pkg.get('status')}")
assert pkg.get("status") == "Resolved", "Ticket status should be Resolved"
print("\nEntire autonomous development lifecycle executed and verified successfully!")
