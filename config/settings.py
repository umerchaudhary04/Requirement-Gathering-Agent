import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

# Pre-configured developer email
DEFAULT_DEVELOPER_EMAIL = "umerasgharkpr123@gmail.com"

# Default Gemini model
DEFAULT_GEMINI_MODEL = "gemini/gemini-1.5-flash"

def get_developer_email() -> str:
    return os.getenv("DEVELOPER_EMAIL", DEFAULT_DEVELOPER_EMAIL)

def get_llm(api_key: str = None, model_name: str = DEFAULT_GEMINI_MODEL) -> LLM:
    """
    Returns a configured CrewAI LLM instance using Google Gemini.
    Free API key: https://aistudio.google.com
    """
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("Google Gemini API Key is required. Please provide it in the sidebar or in your .env file.")
    
    os.environ["GEMINI_API_KEY"] = gemini_key

    return LLM(
        model=model_name,
        api_key=gemini_key,
        temperature=0.3
    )
