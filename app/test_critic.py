import asyncio

from agents import Runner

from app.critic_agent import critic_agent


async def main():

    user_question = "What is the total revenue?"

    draft_answer = """
    The total revenue is 7,055,000.
    """

    evidence = """
    SQL Query:
    SELECT SUM(revenue) FROM sales;

    SQL Result:
    7055000
    """

    evaluation_input = f"""
USER QUESTION:
{user_question}

DRAFT ANSWER:
{draft_answer}

EVIDENCE:
{evidence}
"""

    result = await Runner.run(
        critic_agent,
        evaluation_input
    )

    print("\n==============================")
    print("CRITIC EVALUATION")
    print("==============================\n")

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())