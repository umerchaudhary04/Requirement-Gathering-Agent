import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_DEVELOPER_EMAIL = "umerasgharkpr123@gmail.com"

# Default to Gemini 3.5 Flash-Lite (High-throughput, no demand spikes)
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini/gemini-3.5-flash-lite")

os.environ["LITELLM_LOG"] = "ERROR"

def get_secret(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)

def get_developer_email() -> str:
    return get_secret("DEVELOPER_EMAIL", DEFAULT_DEVELOPER_EMAIL)

def get_llm(model_name: str = None):
    selected_model = model_name or get_secret("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    
    gemini_key = get_secret("GEMINI_API_KEY") or get_secret("GOOGLE_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in Streamlit Secrets or .env.")
    
    os.environ["GEMINI_API_KEY"] = gemini_key
    os.environ["GOOGLE_API_KEY"] = gemini_key

    from crewai import LLM
    return LLM(model=selected_model, api_key=gemini_key, temperature=0.3)
