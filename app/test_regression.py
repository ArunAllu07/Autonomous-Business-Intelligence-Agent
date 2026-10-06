import asyncio

from app.evaluation import evaluate_answer


TEST_CASES = [
    {
        "name": "Total Revenue",
        "question": "What is the total revenue?",
        "evidence": """
SQL Query:
SELECT SUM(revenue) FROM sales;

SQL Result:
7055000
"""
    },
    {
        "name": "Highest Revenue Region",
        "question": "Which region generated the highest revenue?",
        "evidence": """
Regional revenue:
North: 1,200,000
South: 1,700,000
East: 2,000,000
West: 2,155,000
"""
    },
    {
        "name": "Regional Sales Analysis",
        "question": "Analyze sales performance by region.",
        "evidence": """
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
    }
]


async def main():

    passed = 0

    print("\n================================")
    print("AURA REGRESSION TEST SUITE")
    print("================================")

    for test in TEST_CASES:

        print(f"\nRunning: {test['name']}")

        result = await evaluate_answer(
            test["question"],
            test["evidence"]
        )

        if result["passed"]:
            passed += 1
            print("STATUS: PASS")
        else:
            print("STATUS: FAIL")

        print(f"Attempts: {result['attempts']}")

    print("\n================================")
    print("REGRESSION SUMMARY")
    print("================================")

    print(f"Passed: {passed}/{len(TEST_CASES)}")
    print(f"Failed: {len(TEST_CASES) - passed}/{len(TEST_CASES)}")


if __name__ == "__main__":
    asyncio.run(main())