# Certificate of Completion Emailer
### generate and send out PDF versions of a certificate of completion for your training or event


## How to Use
- Placeholder for now
- basically the way to use this project is to have a Word docx doc that you want to re-use to create certificates of completion
- by using your own CSV file of names and emails you will be able to create the certificates of completion and send them out to each attendee's respective email address as a PDF


## Dev setup
- for now you just need python >= 3.8

## Run Locally
- Open project in VS Code
- Reopne in dev container
- run `python main.py`
- enter "Y" or "YES" at the prompts
- copy the successfully sent list and send that to whoever is keeping track 

## Issues
- sometimes there is an error about logging in
  - Google automatically turns off less secure access if it isn't used after a period of time
  - Go to [less secure access](https://myaccount.google.com/u/3/lesssecureapps)
    - update the setting to allow before re-running the tool
  
## How to create a new round of certs
- CSV file
    - add a csv file with NAME,EMAIL column headers
    ```csv
    NAME,EMAIL
    fake name, fake_name@gmail.com
  ```