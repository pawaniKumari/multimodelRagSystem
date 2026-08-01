from google import genai
from google.genai.errors import APIError
from src.config import GEMINI_API_KEY

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from your .env file!")

# Initialize Google GenAI Client
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_multimodal_rag_response(user_query: str, retrieved_context: list) -> str:
    """Generates a grounded response using Google gemini-3.6-flash."""
    if not retrieved_context:
        return "No relevant destinations were found in the database matching your search criteria."

    # Format retrieved database context
    formatted_context = ""
    for idx, doc in enumerate(retrieved_context, 1):
        formatted_context += f"""
        Destination #{idx}:
        - Name: {doc['name']}
        - Category: {doc['category']}
        - District: {doc['district']}
        - Entrance Fee: LKR {doc['entrance_fee']}
        - Trekking Difficulty: {doc['trekking_difficulty']}
        - Description: {doc['description']}
        -----------------------------------
        """

    system_instruction = (
        "You are an expert Sri Lanka Tourism Intelligent Assistant. "
        "Answer the user query strictly using ONLY the provided destination context retrieved from the database. "
        "If the information cannot be answered using the provided context, explicitly inform the user."
    )

    prompt = f"Context from Database:\n{formatted_context}\n\nUser Question: {user_query}"

    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',  # Updated to active free-tier model
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            ),
        )
        return response.text

    except APIError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return "⚠️ **Rate Limit Reached**: Free tier limit reached. Please wait 15–30 seconds and try again."
        return f"An API Error occurred: {str(e)}"