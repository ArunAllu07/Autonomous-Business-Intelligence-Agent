import asyncio

from app.evaluation import evaluate_answer


async def main():

    result = await evaluate_answer(
        "Analyze sales performance by region.",
        """
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
    )

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================\n")

    print(result["answer"])

    print("\n==============================")
    print("EVALUATION STATUS")
    print("==============================\n")

    print(f"Passed: {result['passed']}")
    print(f"Attempts: {result['attempts']}")


if __name__ == "__main__":
    asyncio.run(main())