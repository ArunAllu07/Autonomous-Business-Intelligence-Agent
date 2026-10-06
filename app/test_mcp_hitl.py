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
    ) as mcp_server:

        agent = Agent(
            name="AURA MCP HITL Agent",
            instructions="""
You are AURA's database operations agent.

Use the MCP database tools when the user asks you to
perform database operations.

For this test, execute the requested SQL operation using
the available MCP tools.

Do not invent database results.
""",
            model=model,
            mcp_servers=[mcp_server],
        )

        print("\n==============================")
        print("AURA MCP + HITL TEST")
        print("==============================")

        result = await Runner.run(
            agent,
            """
Execute this harmless database update:

UPDATE sales
SET revenue = revenue
WHERE id = 1;
"""
        )

        interruptions = result.interruptions

        print("\n==============================")
        print("APPROVAL STATUS")
        print("==============================")

        print(f"Pending approvals: {len(interruptions)}")

        if not interruptions:
            print("\nNo approval request was generated.")
            print("Final output:", result.final_output)
            return

        for interruption in interruptions:

            print("\nTool:", interruption.name)
            print("Arguments:", interruption.arguments)

            response = input(
                "\nApprove this operation? (yes/no): "
            ).strip().lower()

            if response == "yes":

                result.state.approve(interruption)

                print("\nAPPROVED")

            else:

                result.state.reject(interruption)

                print("\nREJECTED")

        print("\n==============================")
        print("RESUMING AURA")
        print("==============================")

        result = await Runner.run(
            agent,
            result.to_state()
        )

        print("\n==============================")
        print("FINAL RESULT")
        print("==============================")

        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())