import os

import groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)

groq_client = groq.Groq()
