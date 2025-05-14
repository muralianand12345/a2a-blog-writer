import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "8000"))

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
