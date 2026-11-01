
import os
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Initialize Gemini
client = genai.Client(api_key=api_key)

# Send a test prompt
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Explain Artificial Intelligence in 3 simple sentences."
)

# Print response
print("\nGEMINI RESPONSE:\n")
print(response.text)
