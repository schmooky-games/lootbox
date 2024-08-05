from dotenv import load_dotenv
import os

load_dotenv()

REDIS_URI = os.environ.get("REDIS_URI")
TEMP_TOKEN = os.environ.get("TEMP_TOKEN")
SECRET_KEY = os.environ.get("SECRET_KEY")
FRONT_URL = os.environ.get("FRONT_URL")
