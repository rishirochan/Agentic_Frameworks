import os
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content


class SendEmailInput(BaseModel):
    """Input schema for SendEmailTool."""
    subject: str = Field(..., description="The subject line of the email")
    html_body: str = Field(..., description="The HTML body content of the email")


class SendEmailTool(BaseTool):
    name: str = "send_email"
    description: str = (
        "Sends an HTML email to the configured recipient. "
        "Use this tool when you need to deliver the email campaign. "
        "Provide the email subject line and the full HTML body content."
    )
    args_schema: Type[BaseModel] = SendEmailInput

    def _run(self, subject: str, html_body: str) -> str:
        """Send an HTML email using SendGrid API."""
        try:
            sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            
            from_email = Email(os.environ.get('SENDGRID_FROM_EMAIL'))  
            to_email = To(os.environ.get('SENDGRID_TO_EMAIL')) 

            content = Content("text/html", html_body)
            mail = Mail(from_email, to_email, subject, content).get()
            
            response = sg.client.mail.send.post(request_body=mail)
            
            return f"Email sent successfully! Subject: '{subject}'"
        
        except Exception as e:
            return f"Failed to send email: {str(e)}"
