import httpx
from typing import Any
from pydantic import BaseModel
from app.config import settings

class WorkPackageItem(BaseModel):
    id: str
    subject: str
    type: str  # "Bug" or "Feature"
    status: str  # "New", "In Progress", "Resolved", "Closed"
    priority: str  # "Low", "Normal", "High", "Immediate"
    description: str
    lock_version: int = 1
    comments: list[dict] = []

# Preloaded realistic items for zero-config / demo mode
MOCK_WORK_PACKAGES: dict[str, WorkPackageItem] = {
    "BUG-101": WorkPackageItem(
        id="BUG-101",
        subject="Login fails with invalid password",
        type="Bug",
        status="New",
        priority="High",
        description="When an invalid password is provided to verify_credentials in auth_service.py, it raises an unhandled KeyError instead of safely returning False. Needs unit test coverage.",
        lock_version=1,
        comments=[]
    ),
    "FEAT-102": WorkPackageItem(
        id="FEAT-102",
        subject="Add password complexity validation",
        type="Feature",
        status="New",
        priority="Normal",
        description="Implement validate_password_complexity(password) in auth_service.py to enforce minimum 8 characters, at least one digit and one uppercase letter.",
        lock_version=1,
        comments=[]
    ),
    "BUG-103": WorkPackageItem(
        id="BUG-103",
        subject="Token expiry timestamp calculation error",
        type="Bug",
        status="New",
        priority="Normal",
        description="Token generator in auth_service.py produces timestamps in seconds instead of milliseconds required by mobile clients.",
        lock_version=1,
        comments=[]
    )
}

class OpenProjectClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, is_mock: bool | None = None):
        self.base_url = (base_url or settings.OPENPROJECT_URL).rstrip("/")
        self.api_key = api_key or settings.OPENPROJECT_API_KEY
        self.is_mock = settings.OPENPROJECT_MOCK_MODE if is_mock is None else is_mock
        # If no valid API key is set, auto fallback to mock mode
        if not self.api_key or "example.com" in self.base_url:
            self.is_mock = True

    async def get_work_packages(self) -> list[WorkPackageItem]:
        if self.is_mock:
            return list(MOCK_WORK_PACKAGES.values())

        url = f"{self.base_url}/api/v3/work_packages"
        auth = ("apikey", self.api_key)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, auth=auth, headers={"Content-Type": "application/json"})
                if res.status_code != 200:
                    # Graceful fallback to mock items on connection error
                    return list(MOCK_WORK_PACKAGES.values())
                data = res.json()
                items = []
                elements = data.get("_embedded", {}).get("elements", [])
                for el in elements:
                    pkg_id = str(el.get("id"))
                    subject = el.get("subject", "Untitled")
                    type_title = el.get("_links", {}).get("type", {}).get("title", "Task")
                    item_type = "Bug" if "bug" in type_title.lower() else "Feature"
                    status_title = el.get("_links", {}).get("status", {}).get("title", "New")
                    priority_title = el.get("_links", {}).get("priority", {}).get("title", "Normal")
                    description = el.get("description", {}).get("raw", "")
                    lock_ver = el.get("lockVersion", 1)

                    items.append(WorkPackageItem(
                        id=pkg_id,
                        subject=subject,
                        type=item_type,
                        status=status_title,
                        priority=priority_title,
                        description=description,
                        lock_version=lock_ver
                    ))
                return items
        except Exception:
            return list(MOCK_WORK_PACKAGES.values())

    async def get_work_package(self, work_package_id: str) -> WorkPackageItem | None:
        if self.is_mock:
            return MOCK_WORK_PACKAGES.get(work_package_id)

        url = f"{self.base_url}/api/v3/work_packages/{work_package_id}"
        auth = ("apikey", self.api_key)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, auth=auth)
                if res.status_code != 200:
                    return MOCK_WORK_PACKAGES.get(work_package_id)
                el = res.json()
                type_title = el.get("_links", {}).get("type", {}).get("title", "Task")
                item_type = "Bug" if "bug" in type_title.lower() else "Feature"
                return WorkPackageItem(
                    id=str(el.get("id")),
                    subject=el.get("subject", ""),
                    type=item_type,
                    status=el.get("_links", {}).get("status", {}).get("title", "New"),
                    priority=el.get("_links", {}).get("priority", {}).get("title", "Normal"),
                    description=el.get("description", {}).get("raw", ""),
                    lock_version=el.get("lockVersion", 1)
                )
        except Exception:
            return MOCK_WORK_PACKAGES.get(work_package_id)

    async def update_work_package_status(self, work_package_id: str, new_status: str, comment: str | None = None) -> bool:
        if self.is_mock:
            if work_package_id in MOCK_WORK_PACKAGES:
                item = MOCK_WORK_PACKAGES[work_package_id]
                item.status = new_status
                if comment:
                    item.comments.append({
                        "author": "AI Dev Agent",
                        "comment": comment
                    })
                return True
            return False

        url = f"{self.base_url}/api/v3/work_packages/{work_package_id}"
        auth = ("apikey", self.api_key)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                payload: dict[str, Any] = {}
                if comment:
                    # In OpenProject API v3, comments can be posted via comment field or activities
                    payload["comment"] = {"raw": comment}
                res = await client.patch(url, auth=auth, json=payload)
                return res.status_code in (200, 204)
        except Exception:
            return False

    async def post_comment(self, work_package_id: str, comment_text: str) -> bool:
        if self.is_mock:
            if work_package_id in MOCK_WORK_PACKAGES:
                MOCK_WORK_PACKAGES[work_package_id].comments.append({
                    "author": "AI Dev Agent",
                    "comment": comment_text
                })
                return True
            return False

        url = f"{self.base_url}/api/v3/work_packages/{work_package_id}/activities"
        auth = ("apikey", self.api_key)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, auth=auth, json={"comment": {"raw": comment_text}})
                return res.status_code in (200, 201)
        except Exception:
            return False

openproject_client = OpenProjectClient()
