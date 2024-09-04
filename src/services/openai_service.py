from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI, OpenAI

from src.utils.config import settings

OPENAI_API_KEY = settings.OPENAI_API_KEY

openai_client = OpenAI(api_key=OPENAI_API_KEY)

openai_async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

openai_chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=OPENAI_API_KEY)
