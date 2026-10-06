import asyncio

from agents import Agent, Runner, function_tool
from app.model_config import model


@function_tool(
    needs_approval=True
)
def dangerous_operation(action: str) -> str:
    return f"Executed dangerous operation: {action}"


agent = Agent(
    name="AURA HITL Test Agent",
    instructions="""
You are a test agent for AURA's human approval system.

When the user asks for a dangerous operation,
use the dangerous_operation tool.
""",
    model=model,
    tools=[dangerous_operation],
)


async def main():

    state = None

    result = await Runner.run(
        agent,
        "Delete the test record from the database."
    )

    print("\n==============================")
    print("APPROVAL CHECK")
    print("==============================")

    interruptions = result.interruptions

    print(f"\nPending approvals: {len(interruptions)}")

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

    if interruptions:

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