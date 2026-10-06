import asyncio
import time

from app.mcp_client import create_mcp_server
from app.evaluation import evaluate_answer
from app.evaluation_dataset import EVALUATION_CASES


def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace(",", "")
    text = text.replace("$", "")
    text = text.replace("₹", "")
    return text.strip()


def check_expected_answer(
    actual_answer: str,
    expected_answer: str,
) -> bool:

    actual = normalize(actual_answer)
    expected = normalize(expected_answer)

    return expected in actual


async def run_benchmark():

    print("\n======================================")
    print("AURA — Evaluation Benchmark")
    print("======================================\n")

    results = []

    async with create_mcp_server() as mcp_server:

        for case in EVALUATION_CASES:

            case_id = case["id"]
            question = case["question"]
            expected = case["expected"]

            print("--------------------------------------")
            print(f"Test: {case_id}")
            print(f"Question: {question}")

            start_time = time.perf_counter()

            try:

                evaluation_result = await evaluate_answer(
                    user_question=question,
                    mcp_server=mcp_server,
                )

                answer = evaluation_result["answer"]

                critic_passed = evaluation_result["passed"]

                attempts = evaluation_result["attempts"]

                evaluation = evaluation_result["evaluation"]

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                answer_correct = check_expected_answer(
                    answer,
                    expected,
                )

                final_pass = (
                    answer_correct
                    and critic_passed
                )

                results.append(
                    {
                        "id": case_id,
                        "question": question,
                        "expected": expected,
                        "answer": answer,
                        "answer_correct": answer_correct,
                        "critic_passed": critic_passed,
                        "attempts": attempts,
                        "evaluation": evaluation,
                        "latency": elapsed,
                        "passed": final_pass,
                    }
                )

                status = (
                    "PASS"
                    if final_pass
                    else "FAIL"
                )

                print(f"Expected: {expected}")
                print(f"Actual: {answer}")

                print(
                    f"Answer Correct: "
                    f"{answer_correct}"
                )

                print(
                    f"Critic Passed: "
                    f"{critic_passed}"
                )

                print(
                    f"Attempts: "
                    f"{attempts}"
                )

                print(
                    f"Status: {status}"
                )

                print(
                    f"Latency: "
                    f"{elapsed:.2f}s"
                )

            except Exception as exc:

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                results.append(
                    {
                        "id": case_id,
                        "question": question,
                        "expected": expected,
                        "answer": "",
                        "answer_correct": False,
                        "critic_passed": False,
                        "attempts": 0,
                        "evaluation": "",
                        "latency": elapsed,
                        "passed": False,
                        "error": str(exc),
                    }
                )

                print("Status: ERROR")
                print(f"Error: {exc}")
                print(
                    f"Latency: "
                    f"{elapsed:.2f}s"
                )

    # ------------------------------------------
    # SUMMARY
    # ------------------------------------------

    total = len(results)

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    answer_correct_count = sum(
        1
        for result in results
        if result["answer_correct"]
    )

    critic_passed_count = sum(
        1
        for result in results
        if result["critic_passed"]
    )

    total_attempts = sum(
        result["attempts"]
        for result in results
    )

    accuracy = (
        answer_correct_count / total * 100
        if total
        else 0
    )

    critic_pass_rate = (
        critic_passed_count / total * 100
        if total
        else 0
    )

    benchmark_pass_rate = (
        passed / total * 100
        if total
        else 0
    )

    average_attempts = (
        total_attempts / total
        if total
        else 0
    )

    average_latency = (
        sum(
            result["latency"]
            for result in results
        )
        / total
        if total
        else 0
    )

    # ------------------------------------------
    # FINAL REPORT
    # ------------------------------------------

    print("\n======================================")
    print("AURA EVALUATION REPORT")
    print("======================================")

    print(f"Total Tests          : {total}")
    print(
        f"Answer Accuracy      : "
        f"{accuracy:.2f}%"
    )
    print(
        f"Critic Pass Rate     : "
        f"{critic_pass_rate:.2f}%"
    )
    print(
        f"Benchmark Pass Rate  : "
        f"{benchmark_pass_rate:.2f}%"
    )
    print(
        f"Average Attempts     : "
        f"{average_attempts:.2f}"
    )
    print(
        f"Average Latency      : "
        f"{average_latency:.2f}s"
    )

    print("======================================\n")

    return results


if __name__ == "__main__":

    asyncio.run(
        run_benchmark()
    )