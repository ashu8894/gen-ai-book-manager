import base64
from dotenv import load_dotenv
import os

# Load environment variables from the .env.test file
load_dotenv(".env.test")

# Generate HTTP Basic Auth headers using credentials from environment variables
def basic_auth_headers(username=os.getenv("USERNAME"), password=os.getenv("PASSWORD")):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}
