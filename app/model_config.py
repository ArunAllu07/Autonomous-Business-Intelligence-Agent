import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agents import (
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)


load_dotenv()


freellmapi_key = os.getenv(
    "FREELLMAPI_API_KEY"
)

if not freellmapi_key:
    raise ValueError(
        "FREELLMAPI_API_KEY is missing from .env"
    )


client = AsyncOpenAI(
    api_key=freellmapi_key,
    base_url="http://127.0.0.1:31415/v1",
)


set_tracing_disabled(True)


model = OpenAIChatCompletionsModel(
    model="auto",
    openai_client=client,
)