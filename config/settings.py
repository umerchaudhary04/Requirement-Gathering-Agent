import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

DEFAULT_DEVELOPER_EMAIL = "umerasgharkpr123@gmail.com"

def get_developer_email() -> str:
    """Returns the pre-configured developer destination email."""
    return os.getenv("DEVELOPER_EMAIL", DEFAULT_DEVELOPER_EMAIL)

def get_llm(model_provider: str = "groq", api_key: str = None) -> LLM:
    """Configures free LLMs (Groq Llama 3.3 or Google Gemini)."""
    if model_provider == "groq":
        groq_key = api_key or os.getenv("GROQ_API_KEY")
        if not groq_key:
            raise ValueError("Groq API Key is required. Please enter it in the sidebar.")
        return LLM(model="groq/llama-3.3-70b-versatile", api_key=groq_key, temperature=0.3)
    elif model_provider == "gemini":
        gemini_key = api_key or os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("Gemini API Key is required. Please enter it in the sidebar.")
        return LLM(model="gemini/gemini-1.5-flash", api_key=gemini_key, temperature=0.3)
    else:
        raise ValueError(f"Unsupported model provider: {model_provider}")
