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
    checklist_tool = DomainChecklistTool()
    srs_tool = SRSStructureTool()
    email_tool = SendEmailReportTool()
    target_email = get_developer_email()

    return Agent(
        role="Lead Software Requirements Architect & Business Analyst",
        goal=f"Engage users in English to discover their Product Name, core User Story, and technical requirements. Once complete, AUTOMATICALLY email the final User Story + SRS report directly to {target_email}.",
        backstory=f"You are an elite Lead Software Architect. You communicate strictly in English. You ask 1-2 focused questions at a time and strictly do NOT quote prices or budgets. When requirements are complete, immediately use 'Direct Email Report Dispatcher' to email the complete SRS document to {target_email}.",
        tools=[checklist_tool, srs_tool, email_tool],
        llm=llm,
        verbose=True,
        memory=False
    )

def run_task_with_fallback(task_description: str, expected_output: str) -> str:
    """Retries across candidate Gemini models if a 404 error occurs."""
    last_error = None
    for model_name in CANDIDATE_GEMINI_MODELS:
        try:
            llm = get_llm(model_name=model_name)
            agent = create_requirement_agent(llm)
            
            task = Task(description=task_description, expected_output=expected_output, agent=agent)
            crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
            return str(crew.kickoff())
        except Exception as e:
            err_str = str(e)
            last_error = e
            if "404" in err_str or "NOT_FOUND" in err_str:
                continue
            raise e
    raise last_error

def elicit_requirements(conversation_history: list, latest_user_message: str) -> str:
    target_email = get_developer_email()
    history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history])

    task_description = f"""
Analyze the requirement gathering dialogue:
History:
{history_text}
Latest Message:
{latest_user_message}

CRITICAL RULES:
1. Budget Guardrail: If user asks about cost/pricing, clarify that your mandate is strictly requirement gathering, and developers will quote cost after reviewing the SRS.
2. Step 1: Ensure Product Name & User Story are identified.
3. Probing: Ask 1-2 targeted questions at a time using 'Domain Checklist Inspector'.
4. AUTOMATIC EMAIL TRIGGER:
   - When requirements are complete (User Story, core roles, modules, edge cases covered, OR user says they are done):
     a. Compile the complete document (Part 1: The User Story, Part 2: SRS Report).
     b. CALL 'Direct Email Report Dispatcher' tool to email the report to {target_email}.
     c. Announce in your chat reply that all requirements are gathered and the report has been AUTOMATICALLY emailed to {target_email}.
"""

    return run_task_with_fallback(
        task_description=task_description,
        expected_output="Either 1-2 follow-up questions, OR automatic email dispatch of the completed SRS and user notification."
    )
