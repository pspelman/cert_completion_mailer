# Certificate of Completion Emailer
### generate and send out PDF versions of a certificate of completion for your training or event


## How to Use
- Placeholder for now
- basically the way to use this project is to have a Word docx doc that you want to re-use to create certificates of completion
- by using your own CSV file of names and emails you will be able to create the certificates of completion and send them out to each attendee's respective email address as a PDF


## Dev setup
- for now you just need python >= 3.8

## Authentication Setup (One-Time)
Before running the app for the first time, you need to generate a Google OAuth token **on your local machine** (not in the dev container):

1. Install required packages on your Mac:
   ```bash
   pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. Navigate to the project directory:
   ```bash
   cd /Users/phil/coding/certificate_mailer
   ```

3. Run the authentication script:
   ```bash
   python3 generate_token_locally.py
   ```

4. A browser window will open automatically. Sign in with the **info@hart3s.com** account.

5. After successful authentication, the token will be saved to `app/token.json` and will be accessible in the dev container.

**Note:** The token is valid for ~6 months. If you encounter authentication errors, re-run this script to refresh the token.

## Run Locally
- Open project in VS Code
- Reopen in dev container
- navigate to the app directory: `cd app`
- run `python main.py`
- enter "Y" or "YES" at the prompts
- copy the successfully sent list and send that to whoever is keeping track 

## Issues
- No packages
  - you may need to run `pip install -r requirements.txt` in the container to get the packages installed
- Creates PDFs but reports Errno 2 No such file or directory when trying to process cert entry
  - Turns out something changed and the libreoffice command would no longer honor the output destination, so I updated the code to track the file from where the process decided to output the PDFs 
  
## How to create a new round of certs
- CSV file
    - add a csv file with NAME,EMAIL column headers
    ```csv
    NAME,EMAIL
    fake name,fake_name@gmail.com
  ```
- At the container base directory navigate to `workspaces/certificate_mailer/app`
  - `python -i main.py`

## Deprecated Authentication Methods
**Note:** The following method is deprecated and no longer supported by Google.

- Less Secure Apps (deprecated)
  - Google automatically turns off less secure access if it isn't used after a period of time
  - Go to [less secure access](https://myaccount.google.com/u/3/lesssecureapps)
    - use the info@hart3s.com account (since this is the account we send from)
    - toggle the `Allow less secure apps:` option to `ON`
    - update the setting to allow before re-running the tool
  - **This method is no longer recommended. Use the OAuth token method described in the Authentication Setup section instead.**