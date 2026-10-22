import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FREESOUND_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "FREESOUND_API_KEY not found in .env"
    )

url = "https://freesound.org/apiv2/search/text/"

params = {
    "query": "footsteps",
    "token": API_KEY,
    "page_size": 5,
}

response = requests.get(
    url,
    params=params,
    timeout=30
)

print("HTTP status:", response.status_code)

if response.ok:
    data = response.json()

    print("API connection successful!")
    print("Results:", data.get("count"))

    for result in data.get("results", []):
        print(
            result.get("id"),
            "-",
            result.get("name")
        )

else:
    print("FreeSound API request failed.")
    print(response.text)
