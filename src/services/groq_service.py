import os
import groq
from langchain_groq import ChatGroq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)

groq_client = groq.Groq()

groq_chat = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    max_tokens=8000,
    model_name="llama3-70b-8192",
    temperature=0.3,
)