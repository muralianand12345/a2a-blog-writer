import os
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")

LOG_LEVEL = os.getenv("CLIENT_LOG_LEVEL", "INFO")
