import os
from dotenv import load_dotenv

load_dotenv()


BASE_URL = os.getenv("BASE_URL").strip()
CLI_BASE_URL = os.getenv("CLI_BASE_URL").strip()


if not BASE_URL:
	raise ValueError("Error: BASE_URL is not set in your .env file!")