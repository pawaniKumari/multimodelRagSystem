from google import genai
from src.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

print("--- Available Models supporting generateContent ---")
for model in client.models.list():
    if "generateContent" in getattr(model, "supported_actions", []):
        print(model.name)