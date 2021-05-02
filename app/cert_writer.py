import docx
import csv
import time
import zipfile
from docx2pdf import convert


# Cert writer
def create_certificate(attendee_name: str, training_date: str):
    print(f"trying to create cert for {attendee_name}")
    replace_text_fields = {"XXXCLIENTNAMEXXX": attendee_name,
                           "XXXMEETDATEXXX": training_date}
    base_docx_file = "../private/certificate_of_completion_template.docx"
    docx_output_dir = "./docx_temp"
    new_docx_file = f"{docx_output_dir}/hart3s_harm_reduction_certificate_{attendee_name.replace(' ', '_')}.docx"
    docx_template = zipfile.ZipFile(base_docx_file)

    new_docx = zipfile.ZipFile(new_docx_file, "w")  # X for exclusive create mode | a for append | w for write
    with open(docx_template.extract("word/document.xml", "./")) as tempXmlFile:
        xml_template_string = tempXmlFile.read()
        for key in replace_text_fields.keys():
            xml_template_string = xml_template_string.replace(str(key), str(replace_text_fields.get(key)))

    with open("./temp.xml", "w+") as tempXmlFile:
        tempXmlFile.write(xml_template_string)

        for file in docx_template.filelist:
            if not file.filename == "word/document.xml":
                new_docx.writestr(file.filename, docx_template.read(file))

    new_docx.write("./temp.xml", "word/document.xml")

    docx_template.close()
    new_docx.close()


def convert_to_pdf(path_to_convert: str, del_docx_after: bool = False):
    """ specify a local docx file to convert to PDF
    :param del_docx_after: boolean | delete the original docx file after conversion
    :param path_to_convert: str | name of the local docx file OR directory with files to be converted
    :return:
    """
    pdf_output_dir = "./pdf_certs/"
    # convert the certs_docx directory
    print(f"trying to convert {path_to_convert} to pdf")
    convert(path_to_convert, output_path=pdf_output_dir)


class AttendeeTracker:
    def __init__(self, training_date: str):
        self.training_date = training_date  # training date will be printed on the certificates (e.g., APRIL 2021)
        self._attendee_list = list()
        self.emails = set()

    def load_attendees(self):
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
                        if attendee_email in self.emails:  # Do not allow duplicate email addresses, each attendee should have a unique email
                            raise ValueError(f"{attendee_email} is being added for {attendee_name} but it is ALREADY in the list -- THIS IS A DUPLICATE -- check the data")
                        new_emails.add(attendee_email)
                        new_list.append(row)
                    except Exception as e:
                        print(f"Exception encountered when trying to process row: ", row, e)
                        if "y" not in input("Continue? (type Y or YES to continue, anything else to abort)").lower():
                            print(f"... Aborting loading")
                            return None

        self.emails = new_emails  # TODO: implement local storage of issued / sent certificates
        self._attendee_list = new_list
        print(f"final list: {len(self._attendee_list)} attendees")
        return self._attendee_list

    def make_certs(self, n_attendees=3):
        if not n_attendees:
            print(f"making certs for ALL the attendees")
            n_attendees = len(self.attendee_list)
        else:
            print(f"going to make certs for up to {n_attendees} attendees")

        for attendee in self.attendee_list[:n_attendees]:
            print(f"making cert for {attendee}")
            create_certificate(attendee[0], self.training_date)

    @property
    def attendee_list(self):
        return self._attendee_list or self.load_attendees()

    def __str__(self):
        return f"{self.training_date}"

    def __repr__(self):
        return f"AttendeeTracker({self.training_date})"


# training_date = time.strftime("%m/%d/%y", time.localtime(time.time()))
event_date = "APRIL 2021"
print(event_date)

tracker = AttendeeTracker(event_date)
tracker.make_certs()

# TODO: Convert docx to PDF
