"""
Model Context Protocol (MCP) Server for Development Agent Tools.
Supports JSON-RPC standard method invocations for tools:
- read_file
- search_code
- write_file
- run_tests
- git_status
- git_create_branch
- git_commit
"""
import sys
import json
from pathlib import Path

# Add backend to path to reuse MCPTools
BACKEND_PATH = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.append(str(BACKEND_PATH))

from app.mcp.tools import MCPTools

mcp_tools = MCPTools()

TOOLS_MANIFEST = [
    {
        "name": "read_file",
        "description": "Read contents of a file in the workspace",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Relative file path"}},
            "required": ["path"]
        }
    },
    {
        "name": "search_code",
        "description": "Search code files for a given query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Text query"},
                "subpath": {"type": "string", "default": "."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "write_file",
        "description": "Write or overwrite content of a file in the workspace",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative file path"},
                "content": {"type": "string", "description": "File text content"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "run_tests",
        "description": "Run the test suite in the repository",
        "parameters": {
            "type": "object",
            "properties": {
                "test_command": {"type": "string", "default": "pytest -v"}
            }
        }
    },
    {
        "name": "git_status",
        "description": "Get git branch and status of modified files",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "git_create_branch",
        "description": "Create and switch to a new git branch",
        "parameters": {
            "type": "object",
            "properties": {"branch_name": {"type": "string"}},
            "required": ["branch_name"]
        }
    },
    {
        "name": "git_commit",
        "description": "Stage changes and commit with a message",
        "parameters": {
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"]
        }
    }
]

def handle_rpc(request: dict) -> dict:
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_MANIFEST}}

    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        func = getattr(mcp_tools, tool_name, None)
        if not func:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
            }
        try:
            result = func(**args)
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method '{method}' not found"}}

if __name__ == "__main__":
    # Test execution or CLI invocation
    print(json.dumps(handle_rpc({"id": "init", "method": "tools/list"}), indent=2))
