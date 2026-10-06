import asyncio

from agents import Agent, Runner, function_tool
from app.model_config import model


@function_tool(
    needs_approval=True
)
def dangerous_operation(action: str) -> str:
    return f"Executed dangerous operation: {action}"


agent = Agent(
    name="Approval Test Agent",
    instructions="""
You are an approval test agent.

If the user asks you to perform a dangerous operation,
use the dangerous_operation tool.
""",
    model=model,
    tools=[dangerous_operation],
)


async def main():

    result = await Runner.run(
        agent,
        "Delete the test record from the database."
    )

    print("\n==============================")
    print("RUN ITEMS")
    print("==============================")

    for index, item in enumerate(result.new_items, start=1):

        print(f"\nITEM {index}")
        print("TYPE:", type(item).__name__)
        print("ITEM:", item)

    print("\n==============================")
    print("FINAL OUTPUT")
    print("==============================")

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())