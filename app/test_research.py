import asyncio

from agents import Runner

from app.research_agent import research_agent


async def main():

    result = await Runner.run(
        research_agent,
        "What is my educational background?"
    )

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================\n")

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())