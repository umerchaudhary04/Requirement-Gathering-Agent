from crewai import Agent, Task, Crew, Process
from tools.requirement_tools import DomainChecklistTool, SRSStructureTool, SendEmailReportTool
from config.settings import get_developer_email, get_llm

CANDIDATE_GEMINI_MODELS = [
    "gemini/gemini-1.5-flash-latest",
    "gemini/gemini-2.0-flash",
    "gemini/gemini-3.5-flash",
    "gemini/gemini-1.5-pro-latest"
]

def create_requirement_agent(llm):
    """
    Creates the single CrewAI Requirement Gathering Agent equipped with domain checklist,
    SRS structure outline, and automatic email dispatch tools.
    """
    checklist_tool = DomainChecklistTool()
    srs_tool = SRSStructureTool()
    email_tool = SendEmailReportTool()
    target_email = get_developer_email()

    agent = Agent(
        role="Lead Software Requirements Architect & Business Analyst",
        goal=(
            "Engage users in English to discover their Product Name, core User Story, and technical "
            "requirements through focused dialogue. Proactively uncover hidden edge cases, and THE MOMENT "
            f"all requirements are sufficiently gathered, AUTOMATICALLY compile and email the final User Story + SRS "
            f"report directly to the development team at {target_email} without requiring manual button clicks."
        ),
        backstory=(
            f"You are an elite Lead Software Architect. You communicate strictly in English. "
            f"You ask 1-2 focused questions at a time. You strictly do NOT quote prices or estimate budgets. "
            f"CRITICAL INSTRUCTION: Once you have gathered sufficient requirements (or if the user indicates they have "
            f"shared all details), you MUST IMMEDIATELY and AUTOMATICALLY use your 'Direct Email Report Dispatcher' tool "
            f"to email the complete User Story & SRS document to {target_email}. Then notify the user in the chat that the "
            f"document has been automatically dispatched."
        ),
        tools=[checklist_tool, srs_tool, email_tool],
        llm=llm,
        verbose=True,
        memory=False
    )
    return agent

def run_task_with_fallback(task_description: str, expected_output: str, agent=None) -> str:
    """
    Executes a CrewAI task. If no pre-initialized agent is provided or if a 404 occurs,
    automatically tries candidate Gemini model aliases.
    """
    if agent:
        try:
            task = Task(description=task_description, expected_output=expected_output, agent=agent)
            crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
            return str(crew.kickoff())
        except Exception as e:
            err_str = str(e)
            if "404" not in err_str and "NOT_FOUND" not in err_str:
                raise e

    last_error = None
    for model_name in CANDIDATE_GEMINI_MODELS:
        try:
            llm = get_llm(model_name=model_name)
            fallback_agent = create_requirement_agent(llm)
            
            task = Task(description=task_description, expected_output=expected_output, agent=fallback_agent)
            crew = Crew(agents=[fallback_agent], tasks=[task], process=Process.sequential, verbose=True)
            return str(crew.kickoff())
        except Exception as e:
            err_str = str(e)
            last_error = e
            if "404" in err_str or "NOT_FOUND" in err_str:
                continue
            raise e
    raise last_error

def elicit_requirements(*args, **kwargs) -> str:
    """
    Flexible signature accepting:
    - elicit_requirements(conversation_history, latest_user_message)
    - elicit_requirements(agent, conversation_history, latest_user_message)
    - elicit_requirements(agent=agent, conversation_history=..., latest_user_message=...)
    """
    agent = kwargs.get("agent", None)
    conversation_history = kwargs.get("conversation_history", None)
    latest_user_message = kwargs.get("latest_user_message", None)

    if args:
        if len(args) == 3:
            agent, conversation_history, latest_user_message = args
        elif len(args) == 2:
            conversation_history, latest_user_message = args
        elif len(args) == 1 and conversation_history is None:
            conversation_history = args[0]

    conversation_history = conversation_history or []
    latest_user_message = latest_user_message or ""

    target_email = get_developer_email()
    history_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}" 
        for msg in conversation_history
    ])

    task_description = f"""
Analyze the ongoing software requirement gathering dialogue:

### Conversation History:
{history_text}

### Latest User Message:
{latest_user_message}

### Destination Developer Email:
{target_email}

### Critical Workflow & Rules:
1. **Language**: Communicate exclusively in clear, professional English.
2. **Budget & Cost Guardrail**:
   - If the user asks about price, cost, budget, or quotes:
     Politely clarify that your sole purpose is strictly software requirement elicitation.
     Explain that cost and timeline estimations will be accurately determined by the engineering team after reviewing the final SRS document.
3. **Step 1: Product Name & User Story**:
   - If the session just began, ensure you have the Product Name and the initial User Story (who is the primary user and what core problem does this solve).
4. **Step 2: Probing Missing Requirements**:
   - Use the 'Domain Checklist Inspector' tool to check which critical areas are still unanswered (e.g. user roles/permissions, functional flows, payments, third-party integrations, scalability, edge cases).
   - If key requirements are still missing, ask **only 1 or 2 targeted, concise questions**. Do NOT overwhelm the user with long lists.
5. **Step 3: AUTOMATIC EMAIL DISPATCH (When Requirements Are Complete)**:
   - Check if requirements are sufficiently gathered (e.g., product vision, user roles, core modules, key technical flows/integrations, and edge cases are identified, OR the user indicates they have answered everything / says 'that is all' / 'ready to finish').
   - **THE MOMENT REQUIREMENTS ARE COMPLETE**:
     a. Compile the complete document formatted in Markdown containing:
        - **Part 1: The User Story** (Narrative, Personas, Agile User Stories, Acceptance Criteria)
        - **Part 2: Software Requirements Specification (SRS)** (Executive Summary, RBAC, Functional Modules & Edge Cases, Non-Functional Requirements, Recommended Architecture & Tech Stack, Third-Party APIs)
     b. **CALL THE 'Direct Email Report Dispatcher' TOOL IMMEDIATELY** to send the report to {target_email} with subject: '[Software Requirements & User Story Report] Final Specifications'.
     c. In your chat response to the user, announce that all requirements have been successfully gathered and that the full User Story & SRS Report has been **automatically emailed to our development team at {target_email}**.
"""

    return run_task_with_fallback(
        task_description=task_description,
        expected_output="Either 1-2 targeted follow-up questions, OR automatic email dispatch of the completed SRS and user notification.",
        agent=agent
    )
