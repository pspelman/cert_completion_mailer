#!/usr/bin/env python3
"""
Google OAuth Token Generator
Run this script on your LOCAL machine (not in the dev container).

Prerequisites:
    pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client

Usage:
    cd /Users/phil/coding/certificate_mailer
    python3 generate_token_locally.py

This will open a browser for authentication. Sign in with the account
that has access to hart3s.com. The token will be saved to app/token.json
and will work for ~6 months before needing renewal.
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def main():
    flow = InstalledAppFlow.from_client_secrets_file('private/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    with open('app/token.json', 'w') as token:
        token.write(creds.to_json())
    
    print('✓ Token created at app/token.json')

if __name__ == '__main__':
    main()
