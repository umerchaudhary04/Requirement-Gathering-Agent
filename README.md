<div align="center">

#  AI Software Requirement Gathering Assistant
### *Autonomous Software Requirements Specification (SRS) & User Story Elicitation Powered by Google Gemini & CrewAI*

</div>

---

##  Overview

During traditional software development and client onboarding, a major bottleneck is **incomplete or vague requirements**. Clients frequently overlook critical details—such as user roles, third-party API rate limits, payment edge cases, authentication methods, data retention, and security compliance. Later during engineering, these missing specifications lead to scope creep, inaccurate cost estimates, and delayed deadlines.

The **AI Software Requirement Gathering Assistant** is an autonomous, conversational agent built with **CrewAI** and **Google Gemini 1.5 Flash**. It acts as a Senior Software Architect and Business Analyst:
1. Engages the user in a natural, 1-on-1 dialogue starting with the **Product Name** and initial **User Story**.
2. Proactively inspects industry checklists to ask **1 or 2 targeted, high-impact questions at a time**.
3. Enforces strict scope boundaries (clarifies that it strictly gathers requirements and does not estimate budgets or cost quotes).
4. **Automatically dispatches** a complete, professional two-part specification (**Part 1: The User Story** + **Part 2: Software Requirements Specification (SRS)**) directly to the development team's pre-configured email (`umerasgharkpr123@gmail.com`) the moment all requirements are gathered.

---

##  Key Features

- **Conversational Requirement Elicitation**: Probes for edge cases without overwhelming users with giant questionnaires.
- **Clean, Full-Width Interface**: No technical sidebars or API key inputs exposed to the end-user. Runs as a distraction-free, modern chat interface.
- **Automated Direct Email Handoff**: No manual copy-pasting required. The agent automatically triggers an SMTP dispatch of the finalized SRS and User Story report to the pre-configured developer address (`umerasgharkpr123@gmail.com`).
- **Cost & Budget Guardrail**: Firmly declines quoting prices or estimating budgets, clarifying that estimations are calculated by engineering teams after analyzing the generated SRS.
- **100% Free & Open Source**: Powered by Google AI Studio's free tier (`gemini-1.5-flash`), taking advantage of its massive **1-Million token context window** to remember extensive project dialogue.
- **Production-Ready Architecture**: Clean GitHub repository layout optimized for instant deployment on **Streamlit Community Cloud**.

---

##  Repository Structure

```text
requirement-gathering-agent/
├── .streamlit/
│   └── config.toml           # Streamlit theme, headless server & unredacted logging
├── agent/
│   ├── __init__.py
│   └── crew_manager.py       # CrewAI Agent, Task definitions & auto-dispatch logic
├── config/
│   ├── __init__.py
│   └── settings.py           # Auto secret loaders (Streamlit Secrets / .env) & email setup
├── tools/
│   ├── __init__.py
│   └── requirement_tools.py  # Domain inspection, SRS outline & email dispatch tools
├── .env.example              # Template for environment variables
├── .gitignore                # Git ignore rules for Python & Streamlit
├── app.py                    # Streamlit full-width conversational application
├── LICENSE                   # MIT Open-Source License
├── README.md                 # Complete project documentation
└── requirements.txt          # Python dependencies

```
### How It Works
graph TD
    A[User Enters Product Name & User Story] --> B[CrewAI Senior Architect Agent]
    B --> C[Domain Checklist Tool]
    C -->|Identify Missing Scope| B
    B -->|Ask 1-2 Focused Questions| D[User Answers in Chat]
    D --> B
    B -->|Check Completion Status| E{Requirements Complete?}
    E -->|No| B
    E -->|Yes| F[Synthesize User Story + SRS Document]
    F --> G[Direct Email Report Dispatcher Tool]
    G -->|Automated SMTP Dispatch| H[Email sent to umerasgharkpr123@gmail.com]
    H --> I[Notify User in Chat Interface]

### Deployment on Streamlit Community Cloud (Free)
1. Push your code to GitHub
2. Go to share.streamlit.io and click "New app".
3. Select your repository, branch (main), and set Main file path to app.py.
4. Click Advanced settings...:
 * Python version: Select 3.11.
 * Secrets: Paste the following TOML configuration:
```
GEMINI_API_KEY = "AIzaSy...your_gemini_key_here"
DEVELOPER_EMAIL = "umerasgharkpr123@gmail.com"

# Optional: For live outgoing email delivery
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@gmail.com"
SMTP_PASSWORD = "your_gmail_app_password"
```
5. Click Deploy!. Your app will be live and ready for clients to use.

### Modifying Developer Email in Code
If you ever wish to change the recipient email address where reports are dispatched, open config/settings.py and modify:
```
DEFAULT_DEVELOPER_EMAIL = "umerasgharkpr123@gmail.com"
```
