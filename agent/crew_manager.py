from crewai import Agent, Task, Crew, Process
from tools.requirement_tools import DomainChecklistTool, SRSStructureTool, SendEmailReportTool
from config.settings import get_developer_email

def create_requirement_agent(llm):
    return Agent(
        role="Lead Software Requirements Architect & Business Analyst",
        goal="Discover Product Names, User Stories, and exhaustive technical requirements through dialogue, strictly avoiding budget estimation, and dispatching the final SRS directly to developers.",
        backstory="You are a seasoned Senior Software Architect. You communicate strictly in English. You ask only 1-2 focused questions at a time. You do not quote prices or estimate budgets; your sole mandate is technical requirement elicitation.",
        tools=[DomainChecklistTool(), SRSStructureTool(), SendEmailReportTool()],
        llm=llm,
        verbose=True
    )

def elicit_requirements(agent, conversation_history: list, latest_user_message: str) -> str:
    history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history])

    task = Task(
        description=f"""
Analyze the ongoing requirement elicitation dialogue:
History:
{history_text}
Latest User Input:
{latest_user_message}

Guidelines:
1. Language: Communicate exclusively in clear, professional English.
2. Budget Guardrail: If the user asks about price, cost, or budget, politely clarify that your sole purpose is requirement gathering and developers will estimate cost from the final SRS.
3. User Story: Ensure you understand the Product Name and initial User Story (who is the user and what problem is solved).
4. Probing: Ask 1-2 targeted questions at a time based on the Domain Checklist.
5. If requirements are sufficiently clear, summarize and invite the user to click 'Email SRS'.
""",
        expected_output="1-2 targeted follow-up requirement questions in English.",
        agent=agent
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    return str(crew.kickoff())

def generate_and_email_report(agent, conversation_history: list, project_name: str, recipient_email: str = None) -> dict:
    target_email = recipient_email or get_developer_email()
    history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in conversation_history])

    task = Task(
        description=f"""
1. Compile a comprehensive two-part document in English for '{project_name}':
   - Part 1: The User Story (Narrative, personas, Agile user stories, acceptance criteria).
   - Part 2: Software Requirements Specification (SRS) (Scope, RBAC, modules, edge cases, NFRs, architecture & tech stack, integrations).
2. Use the 'Direct Email Report Dispatcher' tool to email this report directly to: {target_email}.
3. Return the complete Markdown report text along with a confirmation that it was sent to {target_email}.

Conversation History:
{history_text}
""",
        expected_output="Compiled User Story + SRS report and confirmation of email dispatch.",
        agent=agent
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential)
    result = str(crew.kickoff())
    return {"report": result, "recipient": target_email}
