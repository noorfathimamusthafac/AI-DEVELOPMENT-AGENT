import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, AgentRun, AgentActivityLog
from app.auth.dependencies import get_current_user
from app.openproject.client import openproject_client, MOCK_WORK_PACKAGES, WorkPackageItem
from app.agent.orchestrator import AgentOrchestrator, event_generator
from app.mcp.tools import default_mcp_tools
import subprocess

router = APIRouter(prefix="/api", tags=["Agent & OpenProject"])

@router.get("/openproject/work_packages", response_model=list[WorkPackageItem])
async def list_work_packages(current_user: User = Depends(get_current_user)):
    """Fetch available work packages from OpenProject."""
    return await openproject_client.get_work_packages()

@router.get("/openproject/work_packages/{ticket_id}", response_model=WorkPackageItem)
async def get_work_package(ticket_id: str, current_user: User = Depends(get_current_user)):
    """Get single work package details."""
    item = await openproject_client.get_work_package(ticket_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Work package {ticket_id} not found")
    return item

@router.post("/agent/run/{ticket_id}")
async def trigger_agent_run(
    ticket_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger an autonomous agent run for a specific work item."""
    ticket = await openproject_client.get_work_package(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found in OpenProject")

    # Create new AgentRun record in SQLite
    run = AgentRun(
        ticket_id=ticket.id,
        ticket_title=ticket.subject,
        ticket_type=ticket.type,
        status="pending",
        user_id=current_user.id
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    orchestrator = AgentOrchestrator(run_id=run.id)
    # Run in background task
    background_tasks.add_task(orchestrator.execute, ticket_id=ticket.id)

    return {
        "success": True,
        "run_id": run.id,
        "ticket_id": ticket.id,
        "status": "started"
    }

@router.get("/agent/runs")
def list_agent_runs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List historical agent runs."""
    runs = db.query(AgentRun).order_by(AgentRun.created_at.desc()).all()
    results = []
    for r in runs:
        results.append({
            "id": r.id,
            "ticket_id": r.ticket_id,
            "ticket_title": r.ticket_title,
            "ticket_type": r.ticket_type,
            "status": r.status,
            "branch_name": r.branch_name,
            "commit_hash": r.commit_hash,
            "summary": r.summary,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "log_count": len(r.logs)
        })
    return results

@router.get("/agent/runs/{run_id}")
def get_agent_run(run_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve details and activity logs for a specific run."""
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    logs = db.query(AgentActivityLog).filter(AgentActivityLog.run_id == run_id).order_by(AgentActivityLog.id.asc()).all()
    return {
        "id": run.id,
        "ticket_id": run.ticket_id,
        "ticket_title": run.ticket_title,
        "ticket_type": run.ticket_type,
        "status": run.status,
        "branch_name": run.branch_name,
        "commit_hash": run.commit_hash,
        "summary": run.summary,
        "test_output": run.test_output,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        "logs": [
            {
                "id": l.id,
                "step": l.step,
                "status": l.status,
                "message": l.message,
                "details": l.details,
                "timestamp": l.timestamp.isoformat() if l.timestamp else None
            }
            for l in logs
        ]
    }

@router.get("/agent/stream/{run_id}")
async def stream_agent_events(run_id: int):
    """Server-Sent Events (SSE) stream for live agent execution."""
    return StreamingResponse(
        event_generator(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/agent/diff")
def get_target_diff(current_user: User = Depends(get_current_user)):
    """Retrieve the git diff of the target repository."""
    return default_mcp_tools.git_diff()

@router.post("/agent/reset_demo")
def reset_demo(current_user: User = Depends(get_current_user)):
    """Resets the demo repository and mock tickets so the user can re-run the demo seamlessly."""
    repo = default_mcp_tools.repo_path
    try:
        # Checkout master
        subprocess.run(["git", "checkout", "master"], cwd=str(repo), capture_output=True)
        # Restore buggy version
        buggy_code = '''"""
Authentication and User Service.
"""

USERS_DATABASE = {
    "alice@example.com": {
        "password_hash": "hashed_alice_secret",
        "name": "Alice Developer",
        "role": "developer"
    },
    "bob@example.com": {
        "password_hash": "hashed_bob_secret",
        "name": "Bob Admin",
        "role": "admin"
    }
}

def verify_credentials(email: str, password: str) -> bool:
    """
    Verify user login credentials.
    BUG-101: If an unknown email or invalid password is provided,
    this currently raises an unhandled KeyError instead of returning False.
    """
    # BUGGY IMPLEMENTATION
    user = USERS_DATABASE[email]  # Raises KeyError if email doesn't exist
    expected_hash = f"hashed_{password}"
    if user["password_hash"] != expected_hash:
        raise KeyError("Invalid password credentials provided") # Buggy: raises KeyError instead of False
    return True

def get_user_profile(email: str) -> dict | None:
    """Retrieve user profile by email."""
    return USERS_DATABASE.get(email)
'''
        (repo / "auth_service.py").write_text(buggy_code, encoding="utf-8")
        subprocess.run(["git", "add", "auth_service.py"], cwd=str(repo), capture_output=True)
        subprocess.run(["git", "commit", "-m", "reset: restore initial buggy state"], cwd=str(repo), capture_output=True)
        
        # Reset mock tickets
        if "BUG-101" in MOCK_WORK_PACKAGES:
            MOCK_WORK_PACKAGES["BUG-101"].status = "New"
            MOCK_WORK_PACKAGES["BUG-101"].comments = []

        return {"success": True, "message": "Test repository and mock work item reset to initial state."}
    except Exception as e:
        return {"success": False, "error": str(e)}
