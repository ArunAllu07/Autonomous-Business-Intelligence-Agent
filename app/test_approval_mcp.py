import asyncio
import sys

from mcp import Client, StdioServerParameters

from app.guardrails import requires_approval, request_approval


async def main():

    sql = "UPDATE sales SET revenue = revenue WHERE id = 1;"

    action = sql.strip().split()[0].upper()

    print("\n==============================")
    print("AURA HUMAN APPROVAL")
    print("==============================")

    print(f"\nRequested SQL action: {action}")
    print(f"SQL: {sql}")

    if requires_approval(action):

        approved = request_approval(action)

        if not approved:
            print("\nACTION REJECTED")
            return

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server"],
    )

    async with Client(server_params) as client:

        print("\nExecuting approved MCP operation...")

        result = await client.call_tool(
            "execute_sql",
            {
                "sql": sql
            }
        )

        print("\n==============================")
        print("MCP RESULT")
        print("==============================")

        print(result)


if __name__ == "__main__":
    asyncio.run(main())