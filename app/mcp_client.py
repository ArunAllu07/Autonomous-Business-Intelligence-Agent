import sys

from agents.mcp import MCPServerStdio


def create_mcp_server():

    return MCPServerStdio(
        name="AURA Business Data Server",
        params={
            "command": sys.executable,
            "args": ["-m", "app.mcp_server"],
        },
        require_approval={"execute_sql": "always"},
    )