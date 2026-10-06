import asyncio
import sys

from mcp import Client, StdioServerParameters


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server"],
    )

    async with Client(server_params) as client:

        tools = await client.list_tools()

        print("\n==============================")
        print("MCP TOOLS")
        print("==============================\n")

        for tool in tools.tools:
            print(f"- {tool.name}")
            print(f"  {tool.description}")

        print("\n==============================")
        print("TESTING query_sales")
        print("==============================\n")

        result = await client.call_tool(
            "query_sales",
            {
                "sql": "SELECT SUM(revenue) AS total_revenue FROM sales;"
            }
        )

        print(result)


if __name__ == "__main__":
    asyncio.run(main())