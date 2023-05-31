import smtplib
from dotenv import dotenv_values
import json
import getpass
from email.message import EmailMessage
import mimetypes
import time

config = dotenv_values("../.env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}

print(f"config: ", config)


def login_pwd():
    if not (login_pass := config.get('EMAIL_PASS', None)):
        login_pass = getpass.getpass("Input the login password: ", )
    return login_pass


def attach_file(message: EmailMessage, file_path: str):
    mime_type, _ = mimetypes.guess_type(file_path)
    print(f"trying to attach {file_path} | type: ", mime_type)
    mime_type, mime_subtype = mime_type.split('/')
    file_name = file_path.split("/")[-1]
    print(f"file_name: ", file_name)

    with open(file_path, 'rb') as file:
        message.add_attachment(
            file.read(),
            maintype=mime_type,
            subtype=mime_subtype,
            filename=file_name
        )

    return message


class Mailer:

    def __init__(self, **kwargs):
        global config
        if (cfg := kwargs.get('config', False)):
            config = cfg
            self.login_user = config.get('EMAIL_LOGIN', None)
            self.__smtp_backend = config.get('SMTP_DOMAIN', None)
            self.__smtp_port = config.get('SMTP_PORT', None)
        else:
            self.login_user = config.get('EMAIL_LOGIN', None)
            self.__smtp_backend = config.get('SMTP_DOMAIN', None)
            self.__smtp_port = config.get('SMTP_PORT', None)
        # self.__smtp_port = config.get('SMTP_TLS_PORT', None)  # sending mail uses 587 for gmail
        self.__server = None

    @property
    def server(self):
        return self.__server or self.start_server()

    def start_server(self):
        if not self.__server:
            print(f">> starting new mail server connection | connecting to {self.__smtp_backend} : {self.__smtp_port}")
        # s = smtplib.SMTP(self.__smtp_backend, self.__smtp_port)  # This is another option for connecting
        # s.starttls()
        s = smtplib.SMTP_SSL(self.__smtp_backend)
        s.set_debuglevel(0)  # Note: add some debugging with 1
        s.ehlo()
        password = login_pwd()
        print(f"trying to login with {self.login_user} | p: {password}")
        s.login(self.login_user, password)
        self.__server = s
        return self.__server

    def send_mail(self, email_body: str, subj: str,
                  email_to: str, attachment_file: str = None, close_after_send: bool = True) -> None:
        message = EmailMessage()
        message['From'] = self.login_user
        message['To'] = email_to
        message['Subject'] = subj
        message.set_content(email_body)
        if attachment_file:
            attach_file(message, attachment_file)

        print(f"trying to send email from {self.login_user} to {email_to} {'with attachment' if attachment_file else ''}")
        self.server.send_message(message)
        seconds_between_messages = 2
        print(f"... waiting for {seconds_between_messages}s before moving to the next message")
        time.sleep(seconds_between_messages)
        if close_after_send:
            print(f"QUITTING THE MAIL SERVER")
            self.server.quit()
            self.__server = None

    def __str__(self):
        return f"{self.login_user}"

    def __repr__(self):
        return f"Mailer({self.login_user})"
