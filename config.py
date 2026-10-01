import os
from dotenv import load_dotenv

load_dotenv()

ORACLE_BASE_URL = os.getenv("ORACLE_BASE_URL")
ORACLE_USERNAME = os.getenv("ORACLE_USERNAME")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")