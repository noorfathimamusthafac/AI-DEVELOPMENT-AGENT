# AI-Powered Development Agent (OpenProject Work Board Integration)

An intelligent, autonomous software development assistant that bridges project management with automated codebase operations. The agent monitors the **OpenProject Work Board**, parses requirement tickets, inspects the codebase, applies code patches, executes unit tests, commits changes to a Git branch, and updates the OpenProject ticket status.

---

## 🎬 Live Demo Video

![AI Dev Agent Workflow Demo](docs/assets/demo_video.webp)

---

## 🎯 Architecture & Workflow


┌────────────────────────────────────────────────────────┐
│               OpenProject Work Board                   │
│   (Work items: BUG-101, FEAT-102, Status, Priority)    │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI Backend                      │
│  ├── JWT Authentication & RBAC (Developer / Admin)     │
│  ├── OpenProject Client (API v3 REST & Mock Engine)    │
│  ├── SQLite Database (Users, Runs, Logs)               │
│  └── SSE Real-time Activity Streaming                  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                       AI Agent                         │
│  1. Retrieve Work Item & Analyze Requirement           │
│  2. Analyze Repository Structure & Search Code         │
│  3. Formulate & Apply Code Modifications               │
│  4. Execute Pytest Test Suite                          │
│  5. Create Git Branch (fix/bug-... or feat/...)        │
│  6. Git Commit & Update OpenProject Work Item          │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│              Target Codebase (test-repository)         │
│  ├── auth_service.py (Real authentication service)     │
│  └── test_auth_service.py (Pytest unit test suite)     │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

1. **Authentication & Role-Based Access Control**:
   - Secure password hashing using bcrypt.
   - JWT access tokens with protected API routes.
   - Pre-seeded accounts:
     - **Developer**: `dev@example.com` / `password123`
     - **Admin**: `admin@example.com` / `admin123`

2. **OpenProject Integration**:
   - Native integration with OpenProject REST API v3.
   - Dual-mode support: connects to live OpenProject servers or seamlessly switches to embedded zero-config Mock Mode.
   - Automatic ticket transition to `Resolved` with detailed completion comments.

3. **Autonomous 10-Step Software Lifecycle**:
   - `✓ Work item retrieved`
   - `✓ Requirement analyzed`
   - `✓ Repository analyzed`
   - `✓ Relevant files identified`
   - `✓ Code modified`
   - `✓ Tests executed`
   - `✓ Tests passed`
   - `✓ Git branch created`
   - `✓ Changes committed`
   - `✓ OpenProject updated`

4. **Model Context Protocol (MCP) Tooling**:
   - Modular tools layer exposing `read_file`, `search_code`, `write_file`, `run_tests`, `git_status`, `git_create_branch`, and `git_commit`.
   - Standalone JSON-RPC 2.0 MCP server in `mcp-server/tools/server.py`.

5. **Modern Glassmorphic Vue 3 Dashboard**:
   - Built with Vue 3, Vite, TypeScript, and Vanilla CSS design tokens.
   - Real-time animated 10-step progress stepper.
   - Live streaming terminal log viewer using Server-Sent Events (SSE).
   - Instant Git diff inspector and one-click demo state reset.

---

## 🛠️ Quick Start Guide

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- Git

## 🧪 Running Automated Tests

Run backend integration and auth tests:
```bash
cd backend
python -m pytest tests/test_backend.py
```

Run test suite on the target repository:
```bash
cd test-repository
python -m pytest -v
```

---

## 📂 Project Structure

```text
ai-dev-agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # App settings & environment variables
│   │   ├── database.py          # SQLite connection & sessionmaker
│   │   ├── models.py            # SQLAlchemy database models
│   │   ├── auth/                # JWT auth, security, & RBAC dependencies
│   │   ├── openproject/         # OpenProject API v3 client & mock engine
│   │   ├── agent/               # Agent orchestrator & SSE event broadcaster
│   │   ├── mcp/                 # MCP tools (file, test, git operations)
│   │   └── api/                 # API routers for work packages, agent, & runs
│   ├── tests/                   # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/          # Navbar, WorkItemCard, AgentExecutionModal
│   │   ├── views/               # DashboardView, LoginView, RegisterView
│   │   ├── services/            # Typed API client & interfaces
│   │   ├── router/              # Vue Router with auth guards
│   │   ├── style.css            # Modern glassmorphism CSS design system
│   │   ├── App.vue
│   │   └── main.ts
│   ├── Dockerfile
│   └── package.json
│
├── mcp-server/
│   └── tools/
│       └── server.py            # JSON-RPC 2.0 Model Context Protocol server
│
├── test-repository/             # Real target codebase with test suite and git
│   ├── auth_service.py
│   └── test_auth_service.py
│
├── docker-compose.yml
├── .env.example
└── README.md
```
