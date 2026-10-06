import asyncio

from agents import Runner

from app.critic_agent import critic_agent


async def main():

    user_question = "Analyze sales performance by region."

    bad_answer = """
    The East region generated the highest revenue.
    """

    evidence = """
    Regional revenue:
    North: 1,200,000
    South: 1,700,000
    East: 2,000,000
    West: 2,155,000

    Regional profit:
    North: 250,000
    South: 350,000
    East: 416,000
    West: 453,000
    """

    evaluation_input = f"""
USER QUESTION:
{user_question}

DRAFT ANSWER:
{bad_answer}

EVIDENCE:
{evidence}
"""

    result = await Runner.run(
        critic_agent,
        evaluation_input
    )

    print("\n==============================")
    print("RETRY TEST - CRITIC RESULT")
    print("==============================\n")

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())