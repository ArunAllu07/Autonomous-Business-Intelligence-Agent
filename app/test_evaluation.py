import asyncio

from app.evaluation import evaluate_answer


async def main():

    result = await evaluate_answer(
        "What is the total revenue?",
        """
SQL Query:
SELECT SUM(revenue) FROM sales;

SQL Result:
7055000
"""
    )

    print("\n==============================")
    print("FINAL EVALUATED ANSWER")
    print("==============================\n")

    print(result["answer"])

    print("\n==============================")
    print("STATUS")
    print("==============================\n")

    print(f"Passed: {result['passed']}")
    print(f"Attempts: {result['attempts']}")


if __name__ == "__main__":
    asyncio.run(main())