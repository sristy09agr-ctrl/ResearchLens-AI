
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load the token from .env
load_dotenv()

token = os.getenv("HF_TOKEN")

if not token:
    raise ValueError("HF_TOKEN not found in .env file")

# Connect to Hugging Face
client = InferenceClient(api_key=token)

# Send a test prompt
response = client.chat.completions.create(
    model="openai/gpt-oss-120b:cheapest",
    messages=[
        {
            "role": "user",
            "content": "Explain Artificial Intelligence in 3 simple sentences."
        }
    ],
    max_tokens=100
)

# Display the AI response
print("\nAI RESPONSE:\n")
print(response.choices[0].message.content)
