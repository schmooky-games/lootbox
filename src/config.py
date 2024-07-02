from dotenv import load_dotenv
import os

load_dotenv()

REDIS_URI = os.environ.get("REDIS_URI")