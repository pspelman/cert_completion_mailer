import csv
import os
import subprocess
import time
import zipfile
import platform

from global_vars import BASE_DIR


# Cert writer
def create_certificate(attendee_name: str, training_month: str, documented_on_date: str, certificate_type: str = "completion"):
    print(f"trying to create cert for {attendee_name}")
    replace_text_fields = {"XXXCLIENTNAMEXXX": attendee_name,
                           "XXXMEETDATEXXX": training_month,
                           "XXXDOCUMENTEDDATEXXX": documented_on_date,
                           }
    if certificate_type == "CE".upper():
        print(f"creating a CE certificate")
        base_docx_file = f"{BASE_DIR}/private/ce_credit_template.docx"
    else:
        base_docx_file = f"{BASE_DIR}/private/certificate_of_completion_template.docx"
    # docx_output_dir = "./docx_temp"
    # docx_output_dir = "./certs_dir"
    docx_output_dir = f"{BASE_DIR}/app/certs_dir"

    new_docx_file = f"{docx_output_dir}/HaRT3S-harm-reduction-certificate-{attendee_name.replace(' ', '-')}.docx"
    docx_template = zipfile.ZipFile(base_docx_file)

    new_docx = zipfile.ZipFile(new_docx_file, "w")  # X for exclusive create mode | a for append | w for write
    with open(docx_template.extract("word/document.xml", "./")) as tempXmlFile:
        xml_template_string = tempXmlFile.read()
        for key in replace_text_fields.keys():
            print(f"replacing {key} with {replace_text_fields.get(key, 'n/a')}")
            print(f"FINDING in XML_TEMPLATE_STRING: ", xml_template_string.find(str(key)))
            xml_template_string = xml_template_string.replace(str(key), str(replace_text_fields.get(key)))

    with open("./temp.xml", "w+") as tempXmlFile:
        tempXmlFile.write(xml_template_string)

        for file in docx_template.filelist:
            if not file.filename == "word/document.xml":
                new_docx.writestr(file.filename, docx_template.read(file))

    new_docx.write("./temp.xml", "word/document.xml")

    docx_template.close()
    new_docx.close()
    return new_docx_file


# def docx_to_pdf(path_to_convert: str, pdf_output_dir: str = "./pdf_certs",
def docx_to_pdf(path_to_convert: str, pdf_output_dir: str = "./certs_dir",
                del_docx_after: bool = False):
    """ specify a local docx file to convert to PDF
    :param pdf_output_dir:
    :param del_docx_after: boolean | delete the original docx file after conversion
    :param path_to_convert: str | name of the local docx file OR directory with files to be converted
    :return:
    """
    from docx2pdf import convert
    # convert the certs_docx directory
    print(f"trying to convert {path_to_convert} to pdf")
    convert(path_to_convert, output_path=pdf_output_dir)
    new_pdf_path = f"{pdf_output_dir}/{path_to_convert.split('/')[-1].replace('.docx', '.pdf')}"  # need to remove the original dir
    print(f"wrote to: ", new_pdf_path)
    # TODO: Implement removing docx docs if del_docx_after is True
    return new_pdf_path


def doc2pdf_mac(path_to_convert: str):
    """
    convert a doc/docx document to pdf format (linux only, requires libreoffice)
    :param pdf_output_dir: 
    :param path_to_convert: path to document
    """
    print(f"calling libreoffice --convert-to pdf")
    os.chdir(f'{BASE_DIR}/app/certs_dir')  # change to the one directory for now
    cmd = f"/Applications/LibreOffice.app/Contents/MacOS/soffice --headless --invisible --nodefault --view --nolockcheck --nologo --norestore --nofirststartwizard --convert-to pdf".split() + [path_to_convert]
    print(f"CONVERSION CMD:\n", cmd)
    # cmd = 'libreoffice --convert-to pdf'.split() + [path_to_convert]
    try:
        p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p.wait(timeout=10)
        stdout, stderr = p.communicate()
        if stderr:
            raise subprocess.SubprocessError(stderr)
        new_file_name = path_to_convert.replace('.docx', '.pdf')  # make sure the new file name (PDF) is returned
        print(f"COMPLETE! created file: {new_file_name}")
    except Exception as e:
        print(f"Exception when trying to convert: ", e)
        raise RuntimeError("ERROR WHEN TRYING TO CONVERT")
    return new_file_name


def doc2pdf_linux(path_to_convert: str):
    """
    convert a doc/docx document to pdf format (linux only, requires libreoffice)
    :param pdf_output_dir:
    :param path_to_convert: path to document
    """
    print(f"calling libreoffice --convert-to pdf | path_to_convert: {path_to_convert}")
    cmd = 'libreoffice --convert-to pdf'.split() + [path_to_convert]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    p.wait(timeout=10)
    stdout, stderr = p.communicate()
    if stderr:
        raise subprocess.SubprocessError(stderr)
    new_file_name = path_to_convert.replace('/certs_dir', '').replace('.docx', '.pdf')

    print(f"COMPLETE! created file: {new_file_name}")
    return new_file_name


class AttendeeTracker:
    def __init__(self, training_date: str, documented_on_date: str, certificate_type: str = "completion"):
        self.documented_on_date = documented_on_date
        self.training_date = training_date  # training date will be printed on the certificates (e.g., APRIL 2021)
        self._attendee_list = list()
        self.certificate_type = certificate_type
        self.emails = set()

    def load_attendees(self) -> list:
        certs_to_send_file = "../private/attendees_certs_todo.csv"  # attendees file each line after line 0 should be [NAME, EMAIL]
        new_emails = set()
        new_list = list()
        with open(certs_to_send_file, newline='') as csvfile:
            line_reader = csv.reader(csvfile)
            for n, row in enumerate(line_reader, 0):
                if n and row:  # skip blank rows
                    try:
                        attendee_name = row[0]
                        attendee_email = row[1]
                        if attendee_email in self.emails or attendee_email in new_emails:  # Do not allow duplicate email addresses, each attendee should have a unique email
                            raise ValueError(f"\n\n\n{attendee_email} is being added for {attendee_name} but it is ALREADY in the list -- THIS IS A DUPLICATE -- check the data")
                        new_emails.add(attendee_email)
                        new_list.append(row)
                    except ValueError as e:
                        print(f"ISSUE WITH THE NAME!", row, e)
                        print("\n\n\n")
                        break
                    except Exception as e:
                        print(f"Exception encountered when trying to process row: ", row, e)
                        if "y" not in input("Continue? (type Y or YES to continue, anything else to abort)").lower():
                            print(f"... Aborting loading")
                            return []

        self.emails = new_emails  # TODO: implement local storage of issued / sent certificates
        self._attendee_list = new_list
        print(f"final list: {len(self._attendee_list)} attendees")
        return self._attendee_list

    def make_certs(self, n_attendees=3):
        """
        :param n_attendees:
        :return: returns a list of created cert pdfs by email
            Ex: [["someone@somewhere.com", "pdf_certs/certificate_for_someone_somehwere.pdf"]]
        """
        if not n_attendees:
            print(f"making certs for ALL the attendees")
            n_attendees = len(self.attendee_list)
        else:
            print(f"going to make certs for up to {n_attendees} attendees")

        new_files = []
        example = {'email': 'something@something', 'name': 'Phil Spelman', 'cert_file': './cert_file_path.pdf'}
        for attendee in self.attendee_list[:n_attendees]:
            print(f"making cert for {attendee}")
            attendee_name = attendee[0]
            attendee_email = attendee[1]
            docx_file = create_certificate(attendee_name, self.training_date, self.documented_on_date, self.certificate_type)
            print(f"{attendee} | created file {docx_file} --> NOW CONVERTING TO PDF")
            try:
                if platform.system() == "Linux":  # if on linux, use libreoffice
                    new_pdf_path = doc2pdf_linux(docx_file)
                else:
                    new_pdf_path = doc2pdf_mac(docx_file)
                    # new_pdf_path = docx_to_pdf(docx_file)
                # new_entry = [attendee, f'./pdf_certs/HaRT3s_harm_reduction_certificate_{attendee}.pdf']
                new_entry = {'email': attendee_email,
                             'name': attendee_name,
                             'cert_file': new_pdf_path}
                # new_entry = [attendee_email, new_pdf_path]
                print(f"new entry: ", new_entry)
                new_files.append(new_entry)
            except Exception as e:
                print(f"Exception encountered when converting to PDF! ", e)

        print(f"created {len(new_files)} new files")
        return new_files

    @property
    def attendee_list(self):
        return self._attendee_list or self.load_attendees()

    def __str__(self):
        return f"{self.training_date}"

    def __repr__(self):
        return f"AttendeeTracker({self.training_date})"

# training_date = time.strftime("%m/%d/%y", time.localtime(time.time()))
# event_date = "APRIL 2021"
# print(event_date)
# 
# tracker = AttendeeTracker(event_date)
# tracker.make_certs()

# TODO: Convert docx to PDF
