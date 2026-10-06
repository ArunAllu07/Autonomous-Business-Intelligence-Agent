import asyncio

from dotenv import load_dotenv
from agents import Runner

from app.orchestrator import create_orchestrator
from app.mcp_client import create_mcp_server
from app.memory import load_memory, add_memory

from app.observability import (
    configure_logging,
    create_request_id,
    trace_operation,
    log_event,
)


load_dotenv()

configure_logging()


async def main():

    print("\n================================")
    print("AURA — Autonomous Business Intelligence Agent")
    print("================================")

    print("\nType 'exit' to stop AURA.\n")

    conversation = load_memory()

    log_event(
        "cli_started",
        "CLI",
        conversation_messages=len(conversation),
    )

    async with create_mcp_server() as mcp_server:

        orchestrator = create_orchestrator(mcp_server)

        while True:

            user_question = input("You: ").strip()

            if user_question.lower() == "exit":

                log_event(
                    "cli_stopped",
                    "CLI",
                )

                print("\nAURA session ended.")
                break

            if not user_question:
                continue

            request_id = create_request_id()

            with trace_operation(
                "cli_request",
                request_id,
            ):

                log_event(
                    "request_received",
                    request_id,
                    message_length=len(user_question),
                )

                conversation.append({
                    "role": "user",
                    "content": user_question
                })

                with trace_operation(
                    "orchestrator_run",
                    request_id,
                ):

                    result = await Runner.run(
                        orchestrator,
                        conversation
                    )

                answer = result.final_output

                conversation.append({
                    "role": "assistant",
                    "content": answer
                })

                with trace_operation(
                    "memory_persistence",
                    request_id,
                ):

                    add_memory(
                        "user",
                        user_question
                    )

                    add_memory(
                        "assistant",
                        answer
                    )

                log_event(
                    "request_completed",
                    request_id,
                    response_length=len(answer),
                )

                print("\nAURA:")
                print(answer)
                print()


if __name__ == "__main__":
    asyncio.run(main())