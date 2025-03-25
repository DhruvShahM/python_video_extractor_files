import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate(account_name):
    """
    Authenticates a specific Google account and stores its credentials separately.
    """
    creds_filename = f"token_{account_name}.json"  # Unique token file for each account

    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
    credentials = flow.run_local_server(port=8080, prompt="consent")

    # Save credentials for reuse
    with open(creds_filename, "w") as token_file:
        token_file.write(credentials.to_json())

    print(f"Authentication successful for {account_name}!")

# Manually select an account
account_choice = input("Enter account name (e.g., account1, account2): ").strip()
authenticate(account_choice)
