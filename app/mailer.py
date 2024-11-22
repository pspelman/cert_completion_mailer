import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import mimetypes
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class Mailer:
    def __init__(self):
        self.service = self.get_gmail_service()
        self.send_as_email = "certificates@hart3s.com"
        self.display_name = "HaRT3S Certificates"

    def get_gmail_service(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "../private/credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return build("gmail", "v1", credentials=creds)

    def attach_file(self, message: MIMEMultipart, file_path: str):
        mime_type, _ = mimetypes.guess_type(file_path)
        print(f"trying to attach {file_path} | type: ", mime_type)
        if mime_type:
            mime_type, mime_subtype = mime_type.split("/")
        else:
            mime_type, mime_subtype = "application", "octet-stream"
        file_name = os.path.basename(file_path)
        print(f"file_name: ", file_name)

        with open(file_path, "rb") as file:
            attachment = MIMEApplication(file.read(), _subtype=mime_subtype)
        attachment.add_header("Content-Disposition", "attachment", filename=file_name)
        message.attach(attachment)

        return message

    def send_mail(
        self, email_body: str, subj: str, email_to: str, attachment_file: str = None
    ):
        try:
            message = MIMEMultipart()
            message["to"] = email_to
            message["subject"] = subj
            message["from"] = f"{self.display_name} <{self.send_as_email}>"

            msg = MIMEText(email_body)
            message.attach(msg)

            if attachment_file:
                self.attach_file(message, attachment_file)

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            send_message = (
                self.service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )
            print(f'Message Id: {send_message["id"]}')
            return True  # Note: returning True means message sent successfully
        except HttpError as error:
            print(f"An error occurred: {error}")
            if (
                error.resp.status == 403
                and "Gmail API has not been used in project" in str(error)
            ):
                print("Please enable the Gmail API for this project and try again.")
            return False  # Indicate failed send

    def __str__(self):
        return "Gmail API Mailer"

    def __repr__(self):
        return "Mailer(Gmail API)"
