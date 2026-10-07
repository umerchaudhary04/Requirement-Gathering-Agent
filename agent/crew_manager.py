from crewai import Agent, Task, Crew, Process
from tools.requirement_tools import DomainChecklistTool, SRSStructureTool, SendEmailReportTool
from config.settings import get_developer_email

def create_requirement_agent(llm):
    checklist_tool = DomainChecklistTool()
    srs_tool = SRSStructureTool()
    email_tool = SendEmailReportTool()
    target_email = get_developer_email()

    return Agent(
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

def elicit_requirements(agent, conversation_history: list, latest_user_message: str) -> str:
    target_email = get_developer_email()
    history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history])

    task = Task(
        description=f"""
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
""",
        expected_output="Either 1-2 follow-up questions, OR automatic email dispatch of the completed SRS and user notification.",
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    return str(crew.kickoff())
