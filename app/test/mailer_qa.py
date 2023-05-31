from dotenv import dotenv_values

from app.mailer import Mailer


config = dotenv_values("../../.env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}

def run_mailer():
    mailer = Mailer(config=config)
    mailer.start_server()

run_mailer()