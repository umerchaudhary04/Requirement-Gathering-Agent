import streamlit as st
import os
from config.settings import get_llm, get_developer_email
from agent.crew_manager import create_requirement_agent, elicit_requirements, generate_and_email_report

st.set_page_config(page_title="AI Requirement Gathering Assistant", page_icon="📋", layout="wide")

DEVELOPER_EMAIL = get_developer_email()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "srs_report" not in st.session_state:
    st.session_state.srs_report = None
if "project_name" not in st.session_state:
    st.session_state.project_name = "My Software App"

# Sidebar
with st.sidebar:
    st.title("⚙️ Project Settings")
    provider = st.selectbox("LLM Provider (Free Tier)", ["groq", "gemini"], format_func=lambda x: "🚀 Groq (Llama 3.3 - Free)" if x == "groq" else "✨ Google Gemini (Free)")

    api_key = st.text_input("API Key", value=os.getenv("GROQ_API_KEY", "") if provider == "groq" else os.getenv("GEMINI_API_KEY", ""), type="password")
    if not api_key:
        st.info("💡 Free API key: [console.groq.com](https://console.groq.com) or [aistudio.google.com](https://aistudio.google.com)")

    st.divider()
    st.session_state.project_name = st.text_input("Product / App Name", value=st.session_state.project_name)

    # Read-only developer email display
    st.markdown("**Developer Destination:**")
    st.code(DEVELOPER_EMAIL, language="text")
    st.caption("ℹ️ Pre-configured in code. Reports are sent here automatically.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.messages = []
            st.session_state.srs_report = None
            st.rerun()
    with col2:
        dispatch_btn = st.button("📧 Email SRS", use_container_width=True, type="primary", disabled=(len(st.session_state.messages) < 2))

# Main UI
st.title("📋 AI Software Requirement Gathering Assistant")
st.caption("Powered by CrewAI | Discovers User Stories & Technical SRS with Automated Email Delivery")

if not st.session_state.messages:
    st.info(f"👋 Welcome! Please share your **Product Name** and initial **User Story** (what you want to build and who it is for). I will ask 1-2 focused questions at a time to uncover missing requirements. *(Note: I strictly gather technical requirements and do not estimate budgets/costs.)* Once complete, the full document will be emailed directly to `{DEVELOPER_EMAIL}`.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Trigger Report & Email Dispatch
if dispatch_btn:
    if not api_key:
        st.error("Please enter your API Key in the left sidebar first.")
    else:
        with st.spinner(f"Compiling User Story & SRS, then dispatching to {DEVELOPER_EMAIL}..."):
            try:
                llm = get_llm(model_provider=provider, api_key=api_key)
                agent = create_requirement_agent(llm)
                res = generate_and_email_report(agent, st.session_state.messages, st.session_state.project_name, DEVELOPER_EMAIL)
                st.session_state.srs_report = res["report"]
                
                notify = f"🎉 **Requirements Gathering Complete!**\n\nYour **User Story and Software Requirements Specification (SRS)** have been compiled and dispatched directly to the development team at **`{DEVELOPER_EMAIL}`**."
                st.session_state.messages.append({"role": "assistant", "content": notify})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

if st.session_state.srs_report:
    st.success(f"✅ User Story & SRS Report dispatched to {DEVELOPER_EMAIL}!")
    with st.expander("📄 Review Generated User Story & SRS Document", expanded=False):
        st.markdown(st.session_state.srs_report)

# Chat Input
user_input = st.chat_input("Enter your product name, user story, or reply to questions...")
if user_input:
    if not api_key:
        st.error("Please enter your API key in the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing requirements & user story gaps..."):
                try:
                    llm = get_llm(model_provider=provider, api_key=api_key)
                    agent = create_requirement_agent(llm)
                    reply = elicit_requirements(agent, st.session_state.messages[:-1], user_input)
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error: {e}")
