import smtplib
from dotenv import dotenv_values
import json
import getpass

config = dotenv_values("../.env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}

print(f"config: ", config)


# Setup Mailer
class Mailer:
    def __init__(self, **kwargs):
        self.login_user = config.get('EMAIL_LOGIN', None)
        self.__smtp_backend = config.get('SMTP_DOMAIN', None)
        self.__smtp_port = config.get('SMTP_PORT', None)
        self.__server = None

    @property
    def server(self):
        return self.__server or self.start_server()

    def start_server(self):
        if not self.__server:
            print(f"starting server for the first time | connecting to {self.__smtp_backend} : {self.__smtp_port}")
        s = smtplib.SMTP(self.__smtp_backend, self.__smtp_port)
        s.starttls()
        if not (login_pass := config.get('EMAIL_PASS', None)):
            login_pass = getpass.getpass("Input the login password: ", )
        s.login(self.login_user, login_pass)
        self.__server = s
        return self.__server

    def send_mail(self, message: str, email_to: str, attachments: list) -> None:
        print(f"trying to send email from {self.login_user} to {email_to} with {len(attachments)} attachments")
        self.server.sendmail(
            from_addr=self.login_user,
            to_addrs=email_to,
            msg=message
        )

    def __str__(self):
        return f"{self.login_user}"

    def __repr__(self):
        return f"Mailer({self.login_user})"
