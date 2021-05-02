import json
from copy import deepcopy

from cert_writer import AttendeeTracker
from mailer import Mailer
import os

print(f"WORKING DIR: ", os.getcwd())


def process_and_email_certs(mail_handler):
    try:
        mail_handler.start_server()
        mail_body = "Thank you for attending the HaRT3S training evidence-based training on harm-reduction. " \
                    "Attached to this email is a certificate for completing this training."
        email_subject = "HaRT3S - Your Harm-Reduction Training Certificate"
        for cert_entry in attendee_cert_files:
            print(f"unpack cert_entry: ", cert_entry)
            email_recipient = cert_entry[0]
            pdf_attachment = cert_entry[1]
            print(f"trying to create new message for {email_recipient}")
            if "y" in input("Continue? (type Y or YES to continue, anything else to abort)").lower():
                mail_handler.send_mail(mail_body, email_subject, email_recipient, pdf_attachment)
    except Exception as e:
        print(f"Exception encountered when trying to send stuff: ", e)
    finally:
        print(f"closing connection")
        mail_handler.server.quit()


NAME_SEARCH_STRING = "XXXCLIENTNAMEXXX"


def replace_namestring(msg_text, replace_str, replace_with):
    if replace_str in msg_text:
        return msg_text.replace(replace_str, replace_with)


if __name__ == '__main__':
    # Create and send the certificates
    limit_to = 3
    tracker = AttendeeTracker('APRIL 2021')
    tracker.load_attendees()
    attendee_cert_files = tracker.make_certs(limit_to)
    print(f"going to send certs to the following attendees: ", attendee_cert_files)
    # get all the cert files or email one by one
    if "y" in input("Continue? (type Y or YES to continue, anything else to abort)").lower():
        print(f"continuing")

    # TODO: Keep track of SENT certs (so we don't re-send)
    # Send the certs and record SENT certs and timestamp
    try:
        mail_body = ""
        with open('email_message_template.txt', 'r') as message_template:
            msg_txt = message_template.readlines()
            for block in msg_txt:
                mail_body += block
            input("press return to continue")
    except Exception as e:
        print(f"Exception encountered when trying to load the email_message_template.txt file: ", e)
        mail_body = "Thank you for attending the HaRT3S training on harm-reduction. " \
                    "Attached to this email is a certificate of completion."

    mailer = Mailer()
    sent_certs = set()
    failed_list = list()
    try:
        mailer.start_server()
        email_subject = "HaRT3S - Harm-Reduction Training Certificate"
        for cert_entry in attendee_cert_files:
            try:
                first_name = cert_entry['name'].split(' ')[0]
                personalized_mail_body = replace_namestring(deepcopy(mail_body), NAME_SEARCH_STRING, first_name)
                print(f"MAIL WILL BE SENT WITH :\n", personalized_mail_body)
                if "y" in input("\n\nREADY TO SEND NEXT EMAIL? ---> (type Y or YES to continue, anything else to abort)").lower():
                    email_recipient = cert_entry['email']
                    pdf_attachment = cert_entry['cert_file']
                    # email_recipient = cert_entry[0]
                    # pdf_attachment = cert_entry[1]
                    print(f"trying to create new message for {email_recipient}")
                    mailer.send_mail(mail_body, email_subject, email_recipient, pdf_attachment)
                    sent_certs.add(email_recipient)
            except Exception as e:
                print(f"Exception encountered when trying to process cert entry: {cert_entry}: ", e)
                failed_list.append(cert_entry)
    except Exception as e:
        print(f"Exception encountered when trying to send stuff: ", e)
    finally:
        print(f"closing connection")
        mailer.server.quit()
        print("SENT CERTS TO: ", json.dumps(list(sent_certs), indent=4, sort_keys=True))
