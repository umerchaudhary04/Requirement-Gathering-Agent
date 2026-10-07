import sys
import os
from pathlib import Path

# 1. Immediately import streamlit
import streamlit as st

# 2. Add project root to sys.path so submodules load seamlessly
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 3. Streamlit Page Configuration MUST be the first Streamlit command
st.set_page_config(
    page_title="Software Requirement Gathering Agent",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 4. Custom Styling: Hide sidebar completely, clean full-width chat
st.markdown("""
<style>
    /* Hide Streamlit Sidebar completely */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    .welcome-card {
        background-color: #1E293B;
        border-left: 4px solid #3B82F6;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 24px;
        color: #F8FAFC;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 600;
        border-radius: 9999px;
        background-color: #2563EB;
        color: white;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 5. Safe configuration and secrets loading
try:
    from config.settings import get_llm, get_developer_email, get_secret
    DEVELOPER_EMAIL = get_developer_email()
except Exception as e:
    st.error(f"Configuration load error: {str(e)}")
    DEVELOPER_EMAIL = "umerasgharkpr123@gmail.com"

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Top Header Layout (Title + Clean Reset Button)
col_title, col_btn = st.columns([5, 1])

with col_title:
    st.title("Software Requirement Gathering Agent")
    st.caption("Powered by Google Gemini & CrewAI | Automated Discovery & Direct Developer Handoff")

with col_btn:
    st.write("")
    if st.button("New Chat", help="Clear conversation and start over", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.divider()

# Welcome Banner for new chat sessions
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <span class="badge">Requirement Discovery Agent</span>
        <h4 style="margin-top: 8px; margin-bottom: 12px;"> Welcome! Let's define your software requirements.</h4>
        <p>I am your AI Requirements Architect. I help you build a complete specification without missing any critical edge cases, user roles, security, or third-party integrations.</p>
        <p><b>How this works:</b></p>
        <ol style="margin-bottom: 8px;">
            <li>Share your <b>Product Name</b> and your <b>Initial User Story</b> (e.g. <i>"I want to build an on-demand medical delivery app where clinics can order lab specimen couriers with real-time temperature tracking."</i>).</li>
            <li>I will ask you <b>1 or 2 targeted questions at a time</b> to uncover overlooked features, workflows, and technical details.</li>
            <li><i>Note: This assistant strictly gathers requirements and does not estimate budgets or cost quotes.</i></li>
            <li><b>Automatic Handoff:</b> The moment all requirements are gathered, I will <b>automatically compile and email the complete User Story & SRS Report</b> directly to the development team!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Secret Verification
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    try:
        from config.settings import get_secret
        gemini_key = get_secret("GEMINI_API_KEY")
    except Exception:
        pass

if not gemini_key:
    st.warning(" **System Configuration Required**: Please set `GEMINI_API_KEY` in Streamlit Cloud Secrets (Advanced Settings > Secrets).")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
user_input = st.chat_input("Enter your product name, user story, or reply to questions...")

if user_input:
    if not gemini_key:
        st.error("Cannot proceed: `GEMINI_API_KEY` is not configured in Streamlit Secrets.")
    else:
        # 1. Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. Run CrewAI Agent
        with st.chat_message("assistant"):
            with st.spinner("Analyzing requirements & user story gaps..."):
                try:
                    from agent.crew_manager import create_requirement_agent, elicit_requirements
                    
                    llm = get_llm()
                    agent = create_requirement_agent(llm)
                    
                    response_text = elicit_requirements(
                        agent=agent,
                        conversation_history=st.session_state.messages[:-1],
                        latest_user_message=user_input
                    )
                    
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    error_msg = f" An error occurred: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
