import os
import json
import uuid
import datetime
import random
import requests
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# --- DATABASE CONFIG ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "smb_finance")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# --- API SANDBOX CONFIG ---
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
# Sandbox Environment is default
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox") 
PLAID_URL = f"https://{PLAID_ENV}.plaid.com"

QB_CLIENT_ID = os.getenv("QB_CLIENT_ID")
QB_CLIENT_SECRET = os.getenv("QB_CLIENT_SECRET")
QB_REALM_ID = os.getenv("QB_REALM_ID")  # Company ID for Sandbox
QB_REFRESH_TOKEN = os.getenv("QB_REFRESH_TOKEN")
QB_URL = "https://sandbox-quickbooks.api.intuit.com"


def get_db_connection():
    """Establishes and returns a connection to PostgreSQL."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# ==========================================
# 1. MOCK DATA GENERATOR (Fallback Engine)
# ==========================================

def generate_mock_plaid_data(company_id):
    """Generates mock JSON payloads matching Plaid's transactions endpoint."""
    categories = [
        ["Food and Drink", "Restaurants"],
        ["Transfer", "Payroll"],
        ["Shops", "Office Supplies"],
        ["Utilities", "Electric"],
        ["Business Services", "Software"]
    ]
    vendors = ["Uber Eats", "Gusto Payroll", "Staples", "AWS Cloud", "Landlord Corp", "Local Bakery"]
    
    transactions = []
    # Generate 50 realistic historical transactions
    for i in range(50):
        date = (datetime.date.today() - datetime.timedelta(days=i)).isoformat()
        category = random.choice(categories)
        vendor = random.choice(vendors)
        
        # Payroll is negative outflow or positive funding (We'll assume traditional negative out, positive in)
        if "Payroll" in category:
            amount = -4500.00 if i % 14 == 0 else -150.00
        elif "Software" in category:
            amount = -120.00
        else:
            amount = round(random.uniform(-500.00, -10.00), 2)
            
        transactions.append({
            "transaction_id": str(uuid.uuid4()),
            "account_id": "acc_392019",
            "amount": amount,
            "date": date,
            "name": vendor,
            "category": category,
            "payment_channel": "online",
            "merchant_name": vendor,
            "pending": False
        })
        
    # Standard Plaid envelope format
    return {
        "transactions": transactions,
        "total_transactions": len(transactions),
        "accounts": [{
            "account_id": "acc_392019",
            "name": "Business Checking",
            "balances": {
                "available": 24500.50,
                "current": 25000.00,
                "currency": "USD"
            },
            "type": "depository"
        }]
    }


def generate_mock_qb_data(company_id):
    """Generates mock JSON matching QuickBooks Invoices and Payments endpoints."""
    invoices = []
    payments = []
    
    for i in range(20):
        inv_id = str(random.randint(1000, 9999))
        cust_id = str(random.randint(1, 5))
        amount = round(random.uniform(500.00, 3500.00), 2)
        inv_date = (datetime.date.today() - datetime.timedelta(days=random.randint(5, 60)))
        due_date = (inv_date + datetime.timedelta(days=30))
        
        # Determine payment status
        paid = random.choice([True, False])
        
        invoices.append({
            "Id": inv_id,
            "TxnDate": inv_date.isoformat(),
            "DueDate": due_date.isoformat(),
            "TotalAmt": amount,
            "Balance": 0.00 if paid else amount,
            "CustomerRef": {"value": cust_id, "name": f"SMB Client {cust_id}"},
            "Line": [{
                "Amount": amount,
                "Description": "Professional Consulting Services",
                "DetailType": "SalesItemLineDetail"
            }]
        })
        
        if paid:
            pay_date = (inv_date + datetime.timedelta(days=random.randint(1, 15))).isoformat()
            payments.append({
                "Id": str(random.randint(5000, 9999)),
                "TxnDate": pay_date,
                "TotalAmt": amount,
                "CustomerRef": {"value": cust_id},
                "Line": [{
                    "Amount": amount,
                    "LinkedTxn": [{"TxnId": inv_id, "TxnType": "Invoice"}]
                }]
            })
            
    return invoices, payments


# ==========================================
# 2. REAL SANDBOX INTEGRATIONS
# ==========================================

def fetch_plaid_real(client_id, secret, access_token):
    """Hits Plaid API to fetch transaction records."""
    url = f"{PLAID_URL}/transactions/sync"
    headers = {"Content-Type": "application/json"}
    payload = {
        "client_id": client_id,
        "secret": secret,
        "access_token": access_token,
        "count": 100
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Plaid Error: {response.text}")
    return response.json()


def get_qb_access_token(client_id, client_secret, refresh_token):
    """Refreshes the Intuit OAuth access token."""
    url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret))
    if response.status_code != 200:
        raise Exception(f"QuickBooks Token Exchange Error: {response.text}")
    return response.json()["access_token"]


def fetch_qb_entity(entity_name, access_token, realm_id):
    """Queries any QuickBooks API entity list."""
    # QB uses an SQL-like syntax in its query endpoints
    query = f"SELECT * FROM {entity_name}"
    url = f"{QB_URL}/v3/company/{realm_id}/query?query={query}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/text"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"QuickBooks API Error: {response.text}")
    return response.json().get("QueryResponse", {})


# ==========================================
# 3. CORE ETL CONTROL LAYER
# ==========================================

def run_pipeline():
    company_id = "test_smb_01"  # Unique company ID tracking
    print("--- Starting SMB Ingestion Pipeline ---")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if credentials are present
    has_plaid_creds = bool(PLAID_CLIENT_ID and PLAID_SECRET)
    has_qb_creds = bool(QB_CLIENT_ID and QB_CLIENT_SECRET and QB_REALM_ID and QB_REFRESH_TOKEN)
    
    # 1. PLAID DATA EXTRACTION & LIFT
    if has_plaid_creds:
        print("[Plaid] Running in production/sandbox credential mode...")
        # In actual Plaid sandbox integration, you would exchange a public token for an access token
        access_token = os.getenv("PLAID_ACCESS_TOKEN", "mock_access_token")
        try:
            plaid_data = fetch_plaid_real(PLAID_CLIENT_ID, PLAID_SECRET, access_token)
        except Exception as e:
            print(f"[Plaid API Error]: {e}. Falling back to sandbox generator...")
            plaid_data = generate_mock_plaid_data(company_id)
    else:
        print("[Plaid] No client credentials found in environment. Bootstrapping Sandbox mock payload...")
        plaid_data = generate_mock_plaid_data(company_id)

    # 2. QUICKBOOKS DATA EXTRACTION & LIFT
    if has_qb_creds:
        print("[QuickBooks] Running in oauth integration mode...")
        try:
            acc_token = get_qb_access_token(QB_CLIENT_ID, QB_CLIENT_SECRET, QB_REFRESH_TOKEN)
            qb_invoices = fetch_qb_entity("Invoice", acc_token, QB_REALM_ID).get("Invoice", [])
            qb_payments = fetch_qb_entity("Payment", acc_token, QB_REALM_ID).get("Payment", [])
        except Exception as e:
            print(f"[QuickBooks API Error]: {e}. Falling back to sandbox generator...")
            qb_invoices, qb_payments = generate_mock_qb_data(company_id)
    else:
        print("[QuickBooks] Credentials not provided. Bootstrapping Sandbox mock payloads...")
        qb_invoices, qb_payments = generate_mock_qb_data(company_id)

    # 3. LOCAL DATABASE WRITING (LOAD)
    try:
        print(f"[LOAD] Writing Plaid transactions raw records to Postgres...")
        cursor.execute(
            "INSERT INTO raw_stage.plaid_transactions (company_id, payload) VALUES (%s, %s)",
            (company_id, Json(plaid_data))
        )
        
        print(f"[LOAD] Writing {len(qb_invoices)} QuickBooks invoices raw records to Postgres...")
        for invoice in qb_invoices:
            cursor.execute(
                "INSERT INTO raw_stage.quickbooks_invoices (company_id, payload) VALUES (%s, %s)",
                (company_id, Json(invoice))
            )
            
        print(f"[LOAD] Writing {len(qb_payments)} QuickBooks payments raw records to Postgres...")
        for payment in qb_payments:
            cursor.execute(
                "INSERT INTO raw_stage.quickbooks_payments (company_id, payload) VALUES (%s, %s)",
                (company_id, Json(payment))
            )
            
        conn.commit()
        print("[PIPELINE SUCCESS] Extracted and loaded operational raw financial states successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"[PIPELINE FAILED] Rolled back transactions due to error: {e}")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_pipeline()