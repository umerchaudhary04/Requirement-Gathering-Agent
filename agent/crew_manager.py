from crewai import Agent, Task, Crew, Process
from tools.requirement_tools import SendEmailReportTool
from config.settings import get_developer_email, get_llm, get_secret

# Gemini 3 Model Series from Google AI Studio
CANDIDATE_GEMINI_MODELS = [
    get_secret("GEMINI_MODEL", "gemini/gemini-3.5-flash"),
    "gemini/gemini-3.5-flash",
    "gemini/gemini-3.5-flash-lite",
    "gemini/gemini-3.8-flash",
    "gemini/gemini-3.7-flash",
    "gemini/gemini-3.6-flash"
]

def create_requirement_agent(llm):
    email_tool = SendEmailReportTool()
    target_email = get_developer_email()

    return Agent(
        role="Lead Software Requirements Architect & Business Analyst",
        goal=f"Quickly engage the user to discover their Product Name, core User Story, and technical requirements. The moment requirements are complete, automatically email the final User Story + SRS report directly to {target_email}.",
        backstory=f"You are an elite Senior Software Architect. You comprehend user input in English, Urdu, or Roman Urdu, and ALWAYS respond immediately in clear, professional English. You ask 1-2 sharp questions at a time and strictly do NOT quote prices. For regular questions, respond directly without calling any tools. ONLY call the email tool when all requirements are fully gathered.",
        tools=[email_tool],
        llm=llm,
        max_iter=2,
        verbose=False,
        memory=False
    )

def run_task_with_fallback(task_description: str, expected_output: str, agent=None) -> str:
    if agent:
        try:
            task = Task(description=task_description, expected_output=expected_output, agent=agent)
            crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
            return str(crew.kickoff())
        except Exception as e:
            err_str = str(e)
            if "404" not in err_str and "NOT_FOUND" not in err_str:
                raise e

    last_error = None
    seen = set()
    models_to_try = [m for m in CANDIDATE_GEMINI_MODELS if m and not (m in seen or seen.add(m))]

    for model_name in models_to_try:
        try:
            llm = get_llm(model_name=model_name)
            fallback_agent = create_requirement_agent(llm)
            task = Task(description=task_description, expected_output=expected_output, agent=fallback_agent)
            crew = Crew(agents=[fallback_agent], tasks=[task], process=Process.sequential, verbose=False)
            return str(crew.kickoff())
        except Exception as e:
            err_str = str(e)
            last_error = e
            if "404" in err_str or "NOT_FOUND" in err_str:
                continue
            raise e
    raise last_error

def elicit_requirements(*args, **kwargs) -> str:
    agent = kwargs.get("agent", None)
    conversation_history = kwargs.get("conversation_history", None)
    latest_user_message = kwargs.get("latest_user_message", None)

    if args:
        if len(args) == 3: agent, conversation_history, latest_user_message = args
        elif len(args) == 2: conversation_history, latest_user_message = args
        elif len(args) == 1 and conversation_history is None: conversation_history = args[0]

    conversation_history = conversation_history or []
    latest_user_message = latest_user_message or ""

    target_email = get_developer_email()
    history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history])

    task_description = f"""
### Ongoing Dialogue History:
{history_text}

### Latest User Message:
{latest_user_message}

### Destination Email:
{target_email}

### Instructions:
1. Comprehend user input in English, Urdu, or Roman Urdu (e.g. food delivery app for 'White Chillies') and respond immediately in professional, friendly English.
2. Budget Guardrail: If user asks about cost/pricing, clarify that your mandate is strictly requirement gathering; pricing will be estimated by developers from the final SRS.
3. Fast Elicitation: Acknowledge their restaurant app idea and ask 1 or 2 targeted, high-impact questions (e.g., dedicated delivery riders vs third-party couriers, payment methods like Cash on Delivery or card). Do NOT call any tool for routine chat.
4. Automatic Email Dispatch: ONLY when all requirements are gathered or user says 'finalize', compile the full User Story + SRS report, call 'Direct Email Report Dispatcher' to send to {target_email}, and notify the user in chat.
"""

    return run_task_with_fallback(
        task_description=task_description,
        expected_output="1-2 targeted requirement questions in English, OR final email dispatch notification.",
        agent=agent
    )
