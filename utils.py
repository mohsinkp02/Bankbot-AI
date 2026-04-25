import re
import requests
from datetime import datetime
import uuid
import json
import os
import random
import hashlib
import streamlit as st
import PyPDF2
import io
from ollama_integration import (
    get_ollama_response,
    stream_ollama_response,
    get_ai_response,
    stream_ai_response,
    get_active_backend,
    is_banking_query
)

USER_FILE = "users.json"
SESSION_FILE = "session.json"
HISTORY_FILE = "chat_history.json"
INTENTS_FILE = os.path.join("data", "intents.json")

@st.cache_data
def load_intents():
    if not os.path.exists(INTENTS_FILE):
        return {"intents": []}
    try:
        with open(INTENTS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading intents: {e}")
        return {"intents": []}

# Global intents data, initialized from cached function
intents_data = load_intents()

def persist_user(username, email, password):
    users = get_persisted_users()
    users[username] = {"email": email, "password": password}
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def get_persisted_users():
    if not os.path.exists(USER_FILE):
        return {}
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_active_session(username):
    with open(SESSION_FILE, "w") as f:
        json.dump({"username": username}, f)

def get_active_session():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
            return data.get("username")
    except:
        return None

# ─── Password Security ────────────────────────────────────────────────────────

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verifies a password against its hash."""
    return stored_password == hash_password(provided_password)

def migrate_plaintext_passwords():
    """Migrates any legacy plaintext passwords to SHA-256 hashes."""
    users = get_persisted_users()
    changed = False
    for username in users:
        password = users[username]["password"]
        # Check if it looks like a SHA-256 hash (64 hex chars)
        if not (len(password) == 64 and all(c in "0123456789abcdef" for c in password.lower())):
            users[username]["password"] = hash_password(password)
            changed = True
    
    if changed:
        with open(USER_FILE, "w") as f:
            json.dump(users, f, indent=4)

# ─── User Management ──────────────────────────────────────────────────────────

def is_admin(username):
    users = get_persisted_users()
    return users.get(username, {}).get("is_admin", False)

def create_admin_account(password):
    users = get_persisted_users()
    users["admin"] = {
        "email": "admin@centralbank.ai",
        "password": hash_password(password),
        "is_admin": True,
        "created_at": get_timestamp(),
        "balance": 1000000.0,
        "transactions": [],
        "language": "English"
    }
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def persist_user(username, email, password, is_admin=False):
    users = get_persisted_users()
    users[username] = {
        "email": email,
        "password": hash_password(password),
        "is_admin": is_admin,
        "created_at": get_timestamp(),
        "balance": 1000.0, # Starting balance
        "transactions": [],
        "language": "English"
    }
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def get_user_data(username):
    users = get_persisted_users()
    return users.get(username, {})

def update_user_data(username, data):
    users = get_persisted_users()
    if username in users:
        users[username].update(data)
        with open(USER_FILE, "w") as f:
            json.dump(users, f, indent=4)
        return True
    return False

# ─── Banking Simulation ───────────────────────────────────────────────────────

def get_balance(username):
    return get_user_data(username).get("balance", 0.0)

def update_balance(username, amount):
    user_data = get_user_data(username)
    if user_data:
        user_data["balance"] = amount
        update_user_data(username, user_data)
        return True
    return False

def add_transaction(username, type, amount, category, details=""):
    user_data = get_user_data(username)
    if user_data:
        transaction = {
            "id": str(uuid.uuid4()),
            "date": get_timestamp(),
            "type": type,
            "amount": amount,
            "category": category,
            "details": details
        }
        if "transactions" not in user_data:
            user_data["transactions"] = []
        user_data["transactions"].insert(0, transaction)
        update_user_data(username, user_data)
        return True
    return False

def get_transactions(username):
    return get_user_data(username).get("transactions", [])

def transfer_funds(sender, receiver_username, amount, category="Transfer", details=""):
    users = get_persisted_users()
    if receiver_username not in users:
        return False, "Receiver not found"
    
    sender_balance = get_balance(sender)
    if sender_balance < amount:
        return False, "Insufficient funds"
    
    # Deduct from sender
    update_balance(sender, sender_balance - amount)
    add_transaction(sender, "debit", amount, category, f"To: {receiver_username}")
    
    # Add to receiver
    receiver_balance = get_balance(receiver_username)
    update_balance(receiver_username, receiver_balance + amount)
    add_transaction(receiver_username, "credit", amount, category, f"From: {sender}")
    
    return True, "Transfer successful"

# ─── Fraud Detection ──────────────────────────────────────────────────────────

def check_fraud_alerts(username):
    """Analyzes transactions for suspicious activity."""
    transactions = get_transactions(username)
    alerts = []
    
    # 1. High amount transfer
    for txn in transactions:
        if txn["type"] == "debit" and txn["amount"] >= 50000:
            alerts.append({
                "severity": "high",
                "message": f"Large transaction of {format_currency(txn['amount'])} detected",
                "timestamp": txn["date"],
                "details": f"Category: {txn['category']}"
            })
    
    # 2. Rapid transactions (more than 3 in 1 hour - simplified check)
    # This is a mock implementation
    if len(transactions) >= 3:
        alerts.append({
            "severity": "medium",
            "message": "Multiple transactions in a short period",
            "timestamp": get_timestamp(),
            "details": "Please verify if these were initiated by you"
        })
        
    return alerts

def get_fraud_alerts_summary(username):
    alerts = check_fraud_alerts(username)
    return {
        "total": len(alerts),
        "high": len([a for a in alerts if a["severity"] == "high"]),
        "medium": len([a for a in alerts if a["severity"] == "medium"]),
        "alerts": alerts
    }

# ─── Data & File Utilities ────────────────────────────────────────────────────

def save_intents(data):
    """Saves updated intents to the JSON file."""
    try:
        os.makedirs(os.path.dirname(INTENTS_FILE), exist_ok=True)
        with open(INTENTS_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving intents: {e}")
        return False

def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file."""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return None

def clear_active_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def format_currency(amount):
    return f"₹{amount:,.2f}"

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_session_id():
    return str(uuid.uuid4())

def get_chat_preview(messages, max_length=50):
    if not messages:
        return "Empty chat"
    
    for msg in messages:
        if msg["role"] == "user":
            content = msg["content"]
            if len(content) > max_length:
                return content[:max_length] + "..."
            return content
    
    return "No user messages"

@st.cache_data(ttl=30)
def load_history_file():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_history_file(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def get_all_chat_sessions(username):
    history = load_history_file()
    return history.get(username, [])

def save_chat_session(username, session_state, messages, session_id=None):
    if not messages or len(messages) == 0:
        return None
    
    history = load_history_file()
    user_sessions = history.get(username, [])
    
    if session_id:
        # Update existing session
        found = False
        for session in user_sessions:
            if session["session_id"] == session_id:
                session["messages"] = messages
                session["preview"] = get_chat_preview(messages)
                session["timestamp"] = get_timestamp()
                found = True
                break
        
        # Also update in-memory session_state for immediate UI feedback
        for session in session_state.chat_sessions:
            if session["session_id"] == session_id:
                session["messages"] = messages
                session["preview"] = get_chat_preview(messages)
                session["timestamp"] = get_timestamp()
                break
    else:
        # Create new session
        session_id = generate_session_id()
        new_session = {
            "session_id": session_id,
            "timestamp": get_timestamp(),
            "messages": messages,
            "preview": get_chat_preview(messages)
        }
        user_sessions.insert(0, new_session)
        
        if "chat_sessions" not in session_state:
            session_state.chat_sessions = []
        session_state.chat_sessions.insert(0, new_session)

    history[username] = user_sessions
    save_history_file(history)
    return session_id

def load_chat_session(username, session_id):
    user_sessions = get_all_chat_sessions(username)
    for session in user_sessions:
        if session["session_id"] == session_id:
            return session["messages"]
    return None

def delete_chat_session(username, session_state, session_id):
    history = load_history_file()
    user_sessions = history.get(username, [])
    
    user_sessions = [s for s in user_sessions if s["session_id"] != session_id]
    history[username] = user_sessions
    save_history_file(history)
    
    if "chat_sessions" in session_state:
        session_state.chat_sessions = [s for s in session_state.chat_sessions if s["session_id"] != session_id]
    return True

def clear_all_chat_history(username, session_state):
    history = load_history_file()
    history[username] = []
    save_history_file(history)
    
    session_state.chat_sessions = []
    return True

@st.cache_data(ttl=10)
def check_ollama_connection():
    from ollama_integration import check_ollama_connection as _check
    return _check()

def get_faq_response(prompt, language="English"):
    """
    Checks if the user's prompt matches any common frequently asked questions
    using the structured intents.json data.
    """
    prompt_lower = prompt.lower().strip()
    
    if not intents_data or "intents" not in intents_data:
        return None

    # Iterate through intents to find a matching pattern
    for intent in intents_data["intents"]:
        for pattern in intent["patterns"]:
            p_lower = pattern.lower()
            # For short patterns (like 'hi'), use word boundary check
            if len(p_lower) <= 3:
                if re.search(rf"\b{re.escape(p_lower)}\b", prompt_lower):
                    return get_localized_response(intent, language)
            # For longer patterns, substring match is usually fine and more flexible
            elif p_lower in prompt_lower:
                return get_localized_response(intent, language)
            
    return None

def get_localized_response(intent, language):
    """Helper to pick a response in the requested language."""
    if language == "Hindi":
        responses = intent.get("responses_hi", intent.get("responses"))
    elif language == "Marathi":
        responses = intent.get("responses_mr", intent.get("responses"))
    else:
        responses = intent.get("responses")
    
    return random.choice(responses)

def calculate_loan_eligibility(monthly_income, existing_emis, tenure_years):
    """
    Calculates loan eligibility based on FOIR (Fixed Obligation to Income Ratio).
    Standard FOIR is usually 50% for most banks.
    """
    # Max EMI allowed (50% of income)
    max_emi_allowed = monthly_income * 0.5
    
    # Available EMI for new loan
    available_emi = max_emi_allowed - existing_emis
    
    if available_emi <= 0:
        return 0, 0
    
    # Reverse EMI calculation to find principal
    # EMI = [P x R x (1+R)^N]/[(1+R)^N-1]
    # P = EMI * [(1+R)^N-1] / [R * (1+R)^N]
    
    rate_annual = 0.09 # Assume 9% interest for eligibility check
    r = (rate_annual / 12)
    n = tenure_years * 12
    
    principal = available_emi * ((1 + r)**n - 1) / (r * (1 + r)**n)
    
    return round(principal, 2), round(available_emi, 2)
