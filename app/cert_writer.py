import docx
import csv
import time
import zipfile


# Cert writer
def create_certificate(attendee_name: str, meet_date: str):
    print(f"trying to create cert for {attendee_name}")
    replace_text_fields = {"«FIRST» «LAST»": attendee_name,
                           "XXXMEETDATEXXX": meet_date}
    base_docx_file = "certificate_of_completion_cpy.docx"
    new_docx_file = f"hart3s_harm_reduction_certificate_{attendee_name.replace(' ', '_')}.docx"
    docx_template = zipfile.ZipFile(base_docx_file)

    new_docx = zipfile.ZipFile(new_docx_file, "x")  # X for exclusive create mode | a for append
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


class AttendeeTracker:
    def __init__(self, training_date: str):
        self.training_date = training_date  # training date will be printed on the certificates (e.g., APRIL 2021)
        self._attendee_list = list()
        self.emails = set()

    def load_attendees(self):
        # get the csv
        #
        certs_to_send_file = "../private/attendees_certs_todo.csv"
        new_emails = set()
        new_list = list()
        with open(certs_to_send_file, newline='') as csvfile:
            line_reader = csv.reader(csvfile)
            for n, row in enumerate(line_reader, 0):
                if n and row:  # skip blank rows
                    try:
                        print(row)
                        attendee_name = row[0]
                        attendee_email = row[1]
                        if attendee_email in self.emails:  # Do not allow duplicate email addresses, each attendee should have a unique email
                            raise ValueError(f"{attendee_email} is being added for {attendee_name} but it is ALREADY in the list -- THIS IS A DUPLICATE -- check the data")
                        new_emails.add(attendee_email)
                        new_list.append(row)
                    except Exception as e:
                        print(f"Exception encountered when trying to process row: ", row)
                        if "y" not in input("Continue? (type Y or YES to continue, anything else to abort)").lower():
                            print(f"... Aborting loading")
                            return None

        self.emails = new_emails  # TODO: implement local storage of issued / sent certificates
        self._attendee_list = new_list
        print(f"final list: {len(self._attendee_list)} attendees")
        return self._attendee_list

    def make_certs(self, n_attendees=3):
        print(f"going to make certs for up to {n_attendees} attendees")
        for attendee in self.attendee_list[:n_attendees]:
            print(f"making cert for {attendee}")


    @property
    def attendee_list(self):
        return self._attendee_list or self.load_attendees()

    def __str__(self):
        return f"{self.training_date}"

    def __repr__(self):
        return f"AttendeeTracker({self.training_date})"


# TODO: Load the base certificate of completion
# TODO: Create new docx files with each name
# TODO: Convert docx to PDF

# training_date = time.strftime("%m/%d/%y", time.localtime(time.time()))
training_date = "APRIL 2021"
print(training_date)

tracker = AttendeeTracker(training_date)
tracker.make_certs()


