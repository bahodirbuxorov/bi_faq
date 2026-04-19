import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Available Models for embedding:")
for m in client.models.list():
    if "embedContent" in m.supported_actions or "embedText" in m.supported_actions:
        print(m.name)

print("Trying text-embedding-004 specifically...")
print("Available Models for generateContent:")
for m in client.models.list():
    if "generateContent" in m.supported_actions:
        print(m.name)



