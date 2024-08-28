import os

import groq
from langchain_groq import ChatGroq

from src.utils.ai_models import llama3_8b_8192

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)

groq_client = groq.Groq()

groq_chat = ChatGroq(model="llama-3.1-70b-versatile", max_retries=8000, temperature=0.3, stop_sequences="###")
