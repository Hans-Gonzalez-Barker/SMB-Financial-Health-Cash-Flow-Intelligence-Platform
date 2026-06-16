import os
import requests
from dotenv import load_dotenv

# Load variables from the local .env file
load_dotenv()

# Put your Plaid credentials here
CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV_URL = "https://sandbox.plaid.com"

def generate_sandbox_token():
    print("Step 1: Requesting public token...")
    
    # 1. Create a public token
    public_token_url = f"{PLAID_ENV_URL}/sandbox/public_token/create"
    headers = {"Content-Type": "application/json"}
    payload = {
        "client_id": CLIENT_ID,
        "secret": SECRET,
        "institution_id": "ins_109508",
        "initial_products": ["transactions"]
    }
    
    response = requests.post(public_token_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        print(f"Error creating public token: {response.text}")
        return
        
    public_token = response.json().get("public_token")
    print(f"Success! Temporary Public Token: {public_token}")
    print("\nStep 2: Exchanging public token for access token...")
    
    # 2. Exchange public token for access token
    exchange_url = f"{PLAID_ENV_URL}/item/public_token/exchange"
    exchange_payload = {
        "client_id": CLIENT_ID,
        "secret": SECRET,
        "public_token": public_token
    }
    
    exchange_response = requests.post(exchange_url, headers=headers, json=exchange_payload)
    
    if exchange_response.status_code != 200:
        print(f"Error exchanging token: {exchange_response.text}")
        return
        
    access_token = exchange_response.json().get("access_token")
    print("\n==================================================")
    print("     YOUR SANDBOX ACCESS TOKEN (SAVE TO .ENV)     ")
    print("==================================================")
    print(access_token)
    print("==================================================")

if __name__ == "__main__":
    generate_sandbox_token()