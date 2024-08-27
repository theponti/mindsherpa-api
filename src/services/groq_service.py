import os

import groq
from langchain_groq import ChatGroq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)

groq_client = groq.Groq()

groq_chat = ChatGroq(
    model="llama3-70b-8192", max_retries=8000, temperature=0.3, stop_sequences="###"
)
