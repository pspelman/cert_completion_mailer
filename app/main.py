import json
from copy import deepcopy

from global_vars import BASE_DIR
from cert_writer import AttendeeTracker
from mailer import Mailer
import os


def process_and_email_certs(mail_handler):
    try:
        mail_handler.start_server()
        mail_body = (
            "Thank you for attending the HaRT3S training evidence-based training on harm-reduction. "
            "Attached to this email is a certificate for completing this training."
        )
        email_subject = "HaRT3S - Your Harm-Reduction Training Certificate"
        for cert_entry in attendee_cert_files:
            print(f"unpack cert_entry: ", cert_entry)
            email_recipient = cert_entry[0]
            pdf_attachment = cert_entry[1]
            print(f"trying to create new message for {email_recipient}")
            mail_handler.send_mail(
                mail_body,
                email_subject,
                email_recipient,
                pdf_attachment,
                close_after_send=False,
            )
    except Exception as e:
        print(f"Exception encountered when trying to send stuff: ", e)
    finally:
        print(f"closing connection")
        mail_handler.server.quit()


NAME_SEARCH_STRING = "XXXCLIENTNAMEXXX"


def replace_namestring(msg_text, replace_str, replace_with):
    if replace_str in msg_text:
        return msg_text.replace(replace_str, replace_with)


DEFAULT_CERTIFICATE_TYPE = "completion"

if __name__ == "__main__":
    # Create and send the certificates
    limit_to = 0
    certificate_type = input(
        "input type of certificate ('CE' for continuing education) "
    ).upper()
    if not certificate_type:
        print(f"\n\nDEFAULT CERTIFICATE TYPE WILL BE USED\n\n")
    else:
        print(f"\n\nENTERED CERTIFICATE TYPE: {certificate_type}\n\n")
    day = input("input the DAY of the 'documented on' date (e.g., 17) ").upper()
    month = input("input the MONTH of the training (e.g., MAY) ").upper()
    year = input("input the YEAR of the training (e.g., 2021): ").upper()
    if (
        not "y"
        in input(
            f"\n\nProceed with date: \t{month} {year} | documented on {month} {day}, {year} \n\t(Y or YES): "
        ).lower()
    ):
        raise Exception("Operation Aborted by User")
    print(f"continuing")

    tracker = AttendeeTracker(
        f"{month} {year}", f"{month} {day}, {year}", certificate_type
    )
    tracker.load_attendees()
    attendee_cert_files = tracker.make_certs(limit_to)
    print(f"going to send certs to the following attendees: ", attendee_cert_files)
    # get all the cert files or email one by one
    if (
        "y"
        in input(
            "Continue? (type Y or YES to continue, anything else to abort): "
        ).lower()
    ):
        print(f"continuing")
    else:
        raise Exception("Operation Aborted by User")

    # TODO: Keep track of SENT certs (so we don't re-send)
    # Send the certs and record SENT certs and timestamp
    try:
        mail_body = ""
        with open(
            f"{BASE_DIR}/app/email_message_template.txt", "r"
        ) as message_template:
            msg_txt = message_template.readlines()
            for block in msg_txt:
                mail_body += block
    except Exception as e:
        print(
            f"Exception encountered when trying to load the email_message_template.txt file: ",
            e,
        )
        mail_body = (
            "Thank you for attending the HaRT3S training on harm-reduction. "
            "Attached to this email is a certificate of completion."
        )

    mailer = Mailer()
    sent_certs = set()
    failed_list = list()
    try:
        mailer.start_server()
        email_subject = "HaRT3S - Harm-Reduction Training Certificate"
        for cert_entry in attendee_cert_files:
            try:
                first_name = cert_entry["name"].split(" ")[0]
                personalized_mail_body = replace_namestring(
                    deepcopy(mail_body), NAME_SEARCH_STRING, first_name
                )
                print(f"MAIL WILL BE SENT WITH :\n", personalized_mail_body)
                email_recipient = cert_entry["email"]
                pdf_attachment = cert_entry["cert_file"]
                # email_recipient = cert_entry[0]
                # pdf_attachment = cert_entry[1]
                print(f"trying to create new message for {email_recipient}")
                # note: EMAIL IS ABOUT TO BE SENT
                mailer.send_mail(
                    personalized_mail_body,
                    email_subject,
                    email_recipient,
                    pdf_attachment,
                )
                sent_certs.add(email_recipient)
                # if "y" in input("\n\nREADY TO SEND NEXT EMAIL? ---> (type Y or YES to continue, anything else to abort)").lower():
                #     mailer.send_mail(personalized_mail_body, email_subject, email_recipient, pdf_attachment)
                #     sent_certs.add(email_recipient)
                # else:
                #     raise Exception("Operation Aborted by User")
            except Exception as e:
                print(
                    f"Exception encountered when trying to process cert entry: {cert_entry}: ",
                    e,
                )
                failed_list.append(cert_entry)
    except Exception as e:
        print(f"Exception encountered when trying to send stuff: ", e)
    finally:
        print(f"closing connection")
        mailer.server.quit()
        print(
            f"SENT CERTS [{len(list(sent_certs))} total]: ",
            json.dumps(list(sent_certs), indent=4, sort_keys=True),
        )
        print(f"FAILED LIST [{len(list(failed_list))} total]: : ", failed_list)
