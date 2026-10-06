import asyncio

from agents import Runner

from app.orchestrator import orchestrator


async def main():

    result = await Runner.run(
        orchestrator,
        "What is the total revenue?"
    )

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================\n")

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())