import asyncio
import sys

from agents import Agent, Runner
from agents.mcp import MCPServerStdio

from app.model_config import model


async def main():

    async with MCPServerStdio(
        name="AURA Business Data Server",
        params={
            "command": sys.executable,
            "args": ["-m", "app.mcp_server"],
        },
    ) as server:

        agent = Agent(
            name="AURA MCP Agent",
            instructions="""
You are a business data assistant.

Use the MCP tools provided by the AURA Business Data Server
when answering questions about the sales database.

Do not guess database values.
Use the available MCP tools to retrieve the required data.
Explain the result clearly and concisely.
""",
            model=model,
            mcp_servers=[server],
        )

        result = await Runner.run(
            agent,
            "What is the total revenue in the sales database?"
        )

        print("\n==============================")
        print("AURA MCP AGENT RESULT")
        print("==============================\n")

        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())