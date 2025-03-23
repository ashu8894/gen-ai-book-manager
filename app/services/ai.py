import httpx
from dotenv import load_dotenv
import os

MODEL_BASE_URL = os.getenv("MODEL_BASE_URL")

async def generate_summary(prompt: str) -> str:
    print(MODEL_BASE_URL)
    try:
        timeout = httpx.Timeout(300)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{MODEL_BASE_URL}/api/generate",
                headers={"Content-Type": "application/json"},
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
    except Exception as e:
        print("AI Summary Error:", e)
        return "Failed to generate summary"
