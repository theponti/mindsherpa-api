import os

from openai import AsyncOpenAI, OpenAI


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)

openai_client = OpenAI(api_key=OPENAI_API_KEY)

openai_async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
