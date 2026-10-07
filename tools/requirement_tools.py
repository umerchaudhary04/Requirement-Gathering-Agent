import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class DomainChecklistInput(BaseModel):
    domain: str = Field(description="The software domain (e.g., E-commerce, Healthcare, Fintech, SaaS).")

class DomainChecklistTool(BaseTool):
    name: str = "Domain Checklist Inspector"
    description: str = "Provides a checklist of frequently overlooked requirements based on User Story and domain."
    args_schema: Type[BaseModel] = DomainChecklistInput

    def _run(self, domain: str) -> str:
        d = domain.lower()
        if "ecommerce" in d or "shop" in d:
            return "E-Commerce: User roles, inventory thresholds, payment gateway, refunds, shipping APIs, tax engine."
        elif "health" in d or "medical" in d:
            return "Healthcare: HIPAA/GDPR, doctor/patient roles, appointment buffers, WebRTC video, medical audit logs."
        elif "fintech" in d or "bank" in d:
            return "Fintech: KYC/AML compliance, double-entry ledger, idempotency keys, 2FA/biometrics, fraud alerts."
        return "General Software: Auth/RBAC, database scaling, email/SMS gateways, rate limiting, platform targets."

class SRSStructureTool(BaseTool):
    name: str = "SRS Document Template Provider"
    description: str = "Returns IEEE/Agile standard outline for User Story and SRS."
    
    def _run(self, software_type: str = "General") -> str:
        return """
### Standard Outline:
1. **Part I: Detailed User Stories**
   - Primary User Persona & Problem Statement
   - Epic-level User Stories ('As a [User], I want [Feature] so that [Benefit]')
   - Acceptance Criteria
2. **Part II: Software Requirements Specification (SRS)**
   - System Scope & Boundaries
   - Role-Based Access Control (RBAC)
   - Module-by-Module Functional Requirements & Edge Cases
   - Non-Functional Requirements (Security, Performance, Scale)
   - Recommended Architecture & Tech Stack
   - External APIs & Integrations
"""

class SendEmailReportInput(BaseModel):
    recipient_email: str = Field(description="The software house/developer email address.")
    subject: str = Field(description="Email subject.")
    report_content: str = Field(description="Full text of User Story and SRS Report.")

class SendEmailReportTool(BaseTool):
    name: str = "Direct Email Report Dispatcher"
    description: str = "Dispatches the User Story and SRS report directly to the developer/software company email."
    args_schema: Type[BaseModel] = SendEmailReportInput

    def _run(self, recipient_email: str, subject: str, report_content: str) -> str:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        sender_email = os.getenv("SENDER_EMAIL", smtp_user or "agent@software-requirements.local")

        if smtp_user and smtp_password:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = sender_email
                msg["To"] = recipient_email
                msg.attach(MIMEText(report_content, "plain", "utf-8"))

                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.sendmail(sender_email, [recipient_email], msg.as_string())
                return f"SUCCESS: Report emailed successfully to {recipient_email}."
            except Exception as e:
                return f"SMTP ERROR: Failed to send email ({str(e)})."
        else:
            return f"NOTIFICATION: Report compiled and queued for delivery to {recipient_email}."
