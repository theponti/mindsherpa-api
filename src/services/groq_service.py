import os

import groq
from langchain_groq import ChatGroq

from src.utils.ai_models import llama31_70b

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)

groq_client = groq.Groq()

groq_chat = ChatGroq(model=llama31_70b, max_retries=8000, temperature=0.3, stop_sequences="###", verbose=True)
