# backend/chatbot_logic.py
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize the Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_coffee_bot_response(user_query: str):
    # 1. Guardrail (Same as before)
    coffee_keywords = ['coffee', 'leaf', 'bean', 'arabica', 'robusta', 'nutrient', 'deficiency', 'plant', 'soil', 'nitrogen', 'potassium']
    query_lower = user_query.lower()
    is_coffee_related = any(keyword in query_lower for keyword in coffee_keywords)

    if not is_coffee_related:
        return "I am a specialized Coffee Plant Assistant. I can only answer questions related to coffee plants, their growth, and health."

    # 2. Updated Model ID to the Stable version
    system_prompt = (
        "You are an expert agronomist specializing in Coffee plants. "
        "Answer the user's question concisely (under 3 sentences). "
        "If suggesting a remedy, ensure it is safe for coffee plants."
    )
    
    try:
        # Changed 'gemini-3-flash' to 'gemini-2.5-flash' for stability
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=f"{system_prompt}\n\nUser Question: {user_query}"
        )
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"