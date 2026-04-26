import streamlit as st

st.set_page_config(
    page_title="Central Bank AI",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)
import pandas as pd
import plotly.express as px
import time
import json
from utils import (
    validate_email, 
    validate_password_strength, 
    format_currency,
    get_timestamp,
    save_chat_session,
    load_chat_session,
    delete_chat_session,
    clear_all_chat_history,
    persist_user,
    get_persisted_users,
    save_active_session,
    get_active_session,
    clear_active_session,
    get_ai_response,
    stream_ai_response,
    check_ollama_connection,
    get_active_backend,
    get_all_chat_sessions,
    get_faq_response,
    is_banking_query,
    hash_password,
    verify_password,
    is_admin,
    create_admin_account,
    get_user_data,
    update_user_data,
    get_balance,
    update_balance,
    add_transaction,
    get_transactions,
    transfer_funds,
    migrate_plaintext_passwords,
    check_fraud_alerts,
    get_fraud_alerts_summary,
    extract_text_from_pdf,
    load_intents,
    save_intents,
    calculate_loan_eligibility
)

# ─── Multi-Language Support Code ───────────────────────────────────────────────────
TRANSLATIONS = {
    "English": {
        "dashboard": "📊 Dashboard",
        "assistant": "💬 Banking Assistant",
        "calculators": "🧮 Calculators",
        "admin_panel": "⚙️ Admin Panel",
        "logout": "Logout",
        "language": "Language",
        "navigation": "Navigation",
        "recent_chats": "Recent Chats",
        "new_chat": "➕ New Chat",
        "clear_all": "🗑️ Clear All",
        "balance": "Account Balance",
        "interest_rate": "Interest Rate",
        "active_loans": "Active Loans",
        "health_score": "🟢 Financial Health Score",
        "insights": "💡 Smart Insights",
        "net_worth": "💎 Net Worth",
        "upcoming_payments": "📅 Upcoming Payments",
        "fund_transfer": "💸 Fund Transfer",
        "recipient": "Recipient Username",
        "amount": "Amount (₹)",
        "description": "Description",
        "transfer_btn": "🚀 Transfer Funds",
        "history": "📝 Recent Transaction History",
        "chat_input": "Ask about your finances or banking services...",
        "popular_questions": "Popular Questions:",
        "upload_statement": "📂 Upload Bank Statement (PDF)",
        "analyzing": "Analyzing document...",
        "btn_balance": "💰 Balance?",
        "btn_interest": "📈 Interest?",
        "btn_support": "📞 Support",
        "btn_hours": "🕒 Hours",
        "btn_min_bal": "🏦 Min Bal",
        "btn_fd_rates": "📋 FD Rates"
    },
    "Hindi": {
        "dashboard": "📊 डैशबोर्ड",
        "assistant": "💬 बैंकिंग सहायक",
        "calculators": "🧮 कैलकुलेटर",
        "admin_panel": "⚙️ एडमिन पैनल",
        "logout": "लॉगआउट",
        "language": "भाषा",
        "navigation": "नेविगेशन",
        "recent_chats": "हालिया चैट",
        "new_chat": "➕ नई चैट",
        "clear_all": "🗑️ सभी हटाएं",
        "balance": "खाता शेष",
        "interest_rate": "ब्याज दर",
        "active_loans": "सक्रिय ऋण",
        "health_score": "🟢 वित्तीय स्वास्थ्य स्कोर",
        "insights": "💡 स्मार्ट अंतर्दृष्टि",
        "net_worth": "💎 कुल संपत्ति",
        "upcoming_payments": "📅 आगामी भुगतान",
        "fund_transfer": "💸 फंड ट्रांसफर",
        "recipient": "प्राप्तकर्ता उपयोगकर्ता नाम",
        "amount": "राशि (₹)",
        "description": "विवरण",
        "transfer_btn": "🚀 फंड ट्रांसफर करें",
        "history": "📝 हालिया लेनदेन इतिहास",
        "chat_input": "अपने वित्त या बैंकिंग सेवाओं के बारे में पूछें...",
        "popular_questions": "लोकप्रिय प्रश्न:",
        "upload_statement": "📂 बैंक स्टेटमेंट अपलोड करें (PDF)",
        "analyzing": "दस्तावेज़ का विश्लेषण किया जा रहा है...",
        "btn_balance": "💰 बैलेंस?",
        "btn_interest": "📈 ब्याज?",
        "btn_support": "📞 सहायता",
        "btn_hours": "🕒 समय",
        "btn_min_bal": "🏦 न्यून. शेष",
        "btn_fd_rates": "📋 FD दरें"
    },
    "Marathi": {
        "dashboard": "📊 डॅशबोर्ड",
        "assistant": "💬 बँकिंग सहाय्यक",
        "calculators": "🧮 कॅल्क्युलेटर",
        "admin_panel": "⚙️ ॲडमिन पॅनल",
        "logout": "लॉगआउट",
        "language": "भाषा",
        "navigation": "नेविगेशन",
        "recent_chats": "अलीकडील चॅट्स",
        "new_chat": "➕ नवीन चॅट",
        "clear_all": "🗑️ सर्व पुसून टाका",
        "balance": "खाते शिल्लक",
        "interest_rate": "व्याज दर",
        "active_loans": "सक्रिय कर्ज",
        "health_score": "🟢 वित्तीय आरोग्य स्कोर",
        "insights": "💡 स्मार्ट अंतर्दृष्टी",
        "net_worth": "💎 एकूण संपत्ती",
        "upcoming_payments": "📅 आगामी देयके",
        "fund_transfer": "💸 फंड ट्रान्सफर",
        "recipient": "प्राप्तकर्ता वापरकर्तानाव",
        "amount": "रक्कम (₹)",
        "description": "वर्णन",
        "transfer_btn": "🚀 फंड ट्रान्सफर करा",
        "history": "📝 अलीकडील व्यवहार इतिहास",
        "chat_input": "तुमच्या वित्ताबद्दल किंवा बँकिंग सेवांबद्दल विचारा...",
        "popular_questions": "लोकप्रिय प्रश्न:",
        "upload_statement": "📂 बँक स्टेटमेंट अपलोड करा (PDF)",
        "analyzing": "दस्तऐवजाचे विश्लेषण केले जात आहे...",
        "btn_balance": "💰 शिल्लक?",
        "btn_interest": "📈 व्याज?",
        "btn_support": "📞 समर्थन",
        "btn_hours": "🕒 वेळ",
        "btn_min_bal": "🏦 किमान शिल्लक",
        "btn_fd_rates": "📋 FD दर"
    }
}

def t(key):
    """Translation helper function."""
    lang = st.session_state.get("language", "English")
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"]).get(key, key)



def apply_custom_style(theme="dark"):
    # Define color palette based on theme
    if theme == "dark":
        colors = {
            "bg": "#0B1220",
            "card_bg": "#111827",
            "text": "#f1f5f9",
            "text_secondary": "#94a3b8",
            "primary": "#2563EB",
            "secondary": "#0ea5e9",
            "border": "#1F2937",
            "input_bg": "rgba(30, 41, 59, 0.8)",
            "shadow": "rgba(0, 0, 0, 0.4)",
            "success": "#10B981",
            "warning": "#f59e0b",
            "danger": "#EF4444",
            "sidebar_bg": "#0F172A",
            "hover": "rgba(255, 255, 255, 0.05)"
        }
    else:
        colors = {
            "bg": "#F8FAFC",
            "card_bg": "#FFFFFF",
            "text": "#0F172A",
            "text_secondary": "#64748B",
            "primary": "#1E40AF",
            "secondary": "#2563EB",
            "border": "#E2E8F0",
            "input_bg": "#F8FAFC",
            "shadow": "rgba(0, 0, 0, 0.04)",
            "success": "#10B981",
            "warning": "#d97706",
            "danger": "#EF4444",
            "sidebar_bg": "#F1F5F9",
            "hover": "#EFF6FF"
        }

    st.session_state.colors = colors

    st.markdown(f"""
    <style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@500;600;700&display=swap');
    
    /* Global Reset & Typography */
    .stApp {{
        font-family: 'Inter', sans-serif;
        color: {colors['text']};
        background-color: {colors['bg']};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: {colors['text']};
        margin-bottom: 0.5rem;
    }}
    
    h1 {{ font-size: 32px !important; }}
    h2 {{ font-size: 24px !important; }}
    h3 {{ font-size: 18px !important; }}
    
    /* Layout Logic */
    .main .block-container {{
        padding-top: 5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px;
        margin: 0 auto;
    }}
    
    header[data-testid="stHeader"] {{
        background: transparent !important;
        box-shadow: none !important;
        height: 0 !important;
    }}
    
    [data-testid="stAppToolbar"] {{
        display: none !important;
    }}
    
    [data-testid="stSidebarCollapseButton"] {{
        visibility: hidden !important;
        opacity: 0 !important;
    }}

    /* Footer still hidden */
    footer {{
        display: none !important;
    }}

    /* Global Sidebar Styling */
    /* Global Sidebar Styling - Force visibility and width */
    section[data-testid="stSidebar"] {{
        background: {colors.get('sidebar_bg', '#F1F5F9')} !important;
        border-right: 1px solid {colors['border']} !important;
        min-width: 320px !important;
        width: 320px !important;
        visibility: visible !important;
        display: block !important;
    }}
    
    /* Ensure child containers allow visibility */
    [data-testid="stSidebarContent"] {{
        visibility: visible !important;
    }}
    
    /* Hide the 'collapsed' hamburger icon in the top left if it appears */
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}

    /* Remove default sidebar top padding */
    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 2rem !important;
    }}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {colors['border']};
        border-radius: 10px;
    }}

    /* Section Titles */
    .section-title {{
        font-size: 11px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 8px;
        margin-top: 24px;
    }}

    /* User Card */
    .user-card {{
        background: {colors['card_bg']};
        padding: 14px;
        border-radius: 12px;
        border: 1px solid {colors['border']};
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.2s ease;
    }}
    .user-card:hover {{
        transform: translateX(2px);
        background: {colors.get('hover', 'rgba(255,255,255,0.05)')};
    }}
    .user-avatar {{
        background: {colors['primary']};
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }}
    .user-name {{
        font-weight: 600;
        font-size: 14px;
        color: {colors['text']};
    }}
    .user-email {{
        font-size: 12px;
        color: {colors['text_secondary']};
    }}

    /* Navigation / Sidebar Buttons */
    .sidebar-btn {{
        padding: 10px 14px;
        border-radius: 8px;
        color: #cbd5e1;
        transition: all 0.2s ease;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
    }}
    .sidebar-btn:hover {{
        background-color: {colors.get('hover', 'rgba(255,255,255,0.05)')};
        color: white;
        transform: translateX(2px);
    }}
    .sidebar-active {{
        background-color: rgba(37, 99, 235, 0.15);
        border-left: 3px solid {colors['primary']};
        color: white;
        border-radius: 0 8px 8px 0;
    }}

    /* Chat History */
    .chat-history-container {{
        max-height: 250px;
        overflow-y: auto;
        margin-bottom: 24px;
        padding-right: 4px;
    }}
    .chat-item {{
        padding: 8px 10px;
        border-radius: 8px;
        color: #cbd5e1;
        transition: all 0.2s ease;
        font-size: 0.9rem;
        margin-bottom: 4px;
        cursor: pointer;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .chat-item:hover {{
        background: {colors.get('hover', 'rgba(255,255,255,0.05)')};
        color: white;
        transform: translateX(2px);
    }}

    /* Logout Button */
    .logout-btn button {{
        background: transparent !important;
        border: 1px solid {colors['danger']} !important;
        color: {colors['danger']} !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        width: 100%;
        padding: 8px !important;
    }}
    .logout-btn button:hover {{
        background: {colors['danger']} !important;
        color: white !important;
    }}

    /* AI Status Badge */
    .status-badge {{
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 8px;
        border: 1px solid {colors['border']};
    }}
    
    .status-online {{
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border-color: rgba(16, 185, 129, 0.2);
    }}
    
    .status-offline {{
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border-color: rgba(239, 68, 68, 0.2);
    }}
    
    /* Card Component */
    .bank-card {{
        background-color: {colors['card_bg']};
        border: 1px solid {colors['border']};
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 4px 15px {colors['shadow']};
        margin-bottom: 16px;
    }}
    
    /* Primary Buttons */
    .stButton>button {{
        border-radius: 8px;
        transition: 0.3s ease;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
    }}
    
    /* Chat Interface Styling */
    .user-bubble {{
        background: {colors['primary']};
        color: white;
        padding: 12px 20px;
        border-radius: 20px 20px 4px 20px;
        margin-bottom: 12px;
        max-width: 85%;
        margin-left: auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        font-size: 0.95rem;
        line-height: 1.5;
    }}
    
    .ai-bubble {{
        background: {colors['card_bg']};
        color: {colors['text']};
        padding: 12px 20px;
        border-radius: 20px 20px 20px 4px;
        margin-bottom: 12px;
        max-width: 85%;
        border: 1px solid {colors['border']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        font-size: 0.95rem;
        line-height: 1.5;
    }}

    /* Modern Chat Input Styling */
    section[data-testid="stChatInput"] {{
        padding-bottom: 2rem !important;
    }}
    
    section[data-testid="stChatInput"] > div {{
        background-color: transparent !important;
    }}

    section[data-testid="stChatInput"] textarea {{
        background-color: {colors['input_bg']} !important;
        border: 1px solid {colors['border']} !important;
        border-radius: 25px !important;
        padding: 12px 20px !important;
        color: {colors['text']} !important;
        box-shadow: 0 4px 12px {colors['shadow']} !important;
        transition: all 0.3s ease;
    }}

    section[data-testid="stChatInput"] textarea:focus {{
        border-color: {colors['primary']} !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }}
    
    /* Disable default Streamlit fading on rapid updates */
    div[data-testid="stVerticalBlock"] > div,
    div[data-testid="stVerticalBlock"],
    div.element-container, 
    div.stMarkdown, 
    div[data-testid="stMarkdownContainer"],
    div[data-testid="stChatMessage"] {{
        transition: none !important;
        animation: none !important;
        opacity: 1 !important;
    }}
    
    * {{
        animation: none !important;
    }}

    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    if "users" not in st.session_state:
        st.session_state.users = get_persisted_users()
    
    if "logged_in" not in st.session_state:
        last_user = get_active_session()
        if last_user and last_user in st.session_state.users:
            st.session_state.logged_in = True
            st.session_state.username = last_user
            st.session_state.email = st.session_state.users[last_user]["email"]
            st.session_state.is_admin = is_admin(last_user)
            # Fetch fresh data for the user
            refresh_user_data(last_user)
        else:
            st.session_state.logged_in = False
    
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    
    apply_custom_style(st.session_state.theme)
            
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"
    if "chat_sessions" not in st.session_state:
        if st.session_state.logged_in and st.session_state.username:
            st.session_state.chat_sessions = get_all_chat_sessions(st.session_state.username)
        else:
            st.session_state.chat_sessions = []
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

def refresh_user_data(username):
    """Refreshes session state with fresh data from the backend."""
    user_data = get_user_data(username)
    st.session_state.balance = user_data.get("balance", 0.0)
    st.session_state.interest_rate = user_data.get("interest_rate", 6.5)
    st.session_state.accrued_interest = user_data.get("accrued_interest", 0.0)
    st.session_state.active_loans = len([l for l in user_data.get("transactions", []) if l.get("category") == "Loan"])
    st.session_state.total_loan_amount = user_data.get("total_loan_amount", 0.0)
    st.session_state.language = user_data.get("language", "English")

init_session_state()

def login(username, password):
    users = get_persisted_users()
    if username in users:
        if verify_password(users[username]["password"], password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.email = users[username]["email"]
            st.session_state.is_admin = is_admin(username)
            # Ensure fresh data is loaded
            refresh_user_data(username)
            st.session_state.current_page = "dashboard"
            st.session_state.chat_sessions = get_all_chat_sessions(username)
            save_active_session(username)
            return True
    return False

def signup(username, email, password):
    users = get_persisted_users()
    if username in users:
        return False, "Username already exists"
    
    persist_user(username, email, password)
    return True, "Account created successfully!"

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.current_page = "login"
    st.session_state.messages = []
    st.session_state.current_chat_id = None
    clear_active_session()

def get_user_transactions_df(username):
    """Builds a dashboard-friendly DataFrame from stored user transactions."""
    transactions = get_transactions(username)
    if not transactions:
        return pd.DataFrame(columns=["Date", "Category", "Type", "Amount", "Details", "Direction"])

    rows = []
    for txn in transactions:
        raw_type = str(txn.get("type", "")).lower()
        rows.append({
            "Date": pd.to_datetime(txn.get("date"), errors="coerce"),
            "Category": txn.get("category", "Other") or "Other",
            "Type": "Income" if raw_type == "credit" else "Expense",
            "Amount": float(txn.get("amount", 0) or 0),
            "Details": txn.get("details", ""),
            "Direction": raw_type.title() if raw_type else "Unknown"
        })

    df = pd.DataFrame(rows)
    df["Date"] = df["Date"].fillna(pd.Timestamp.now())
    return df.sort_values(by="Date", ascending=False).reset_index(drop=True)

def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Central Bank AI")
        st.subheader("Login")
        st.divider()
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submit:
                if login(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.divider()
        if st.button("Don't have an account? Sign Up", use_container_width=True):
            st.session_state.current_page = "signup"
            st.rerun()

def show_signup_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏦 Central Bank AI")
        st.subheader("Create Account")
        st.divider()
        
        with st.form("signup_form"):
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
            submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if submit:
                if not username or not email or not password or not confirm_password:
                    st.error("All fields are required")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, msg = signup(username, email, password)
                    if success:
                        st.success(msg)
                        st.info("Please login with your credentials")
                        st.session_state.current_page = "login"
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
        
        st.divider()
        if st.button("Already have an account? Login", use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()

def show_dashboard():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 0 0 1rem 0; text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏦</div>
            <h2 style="margin: 0; font-size: 1.3rem !important; font-family: 'Poppins', sans-serif;">Central Bank AI</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # User Info Section (New CSS Class)
        st.markdown(f"""
        <div class="user-card">
            <div class="user-avatar">
                {st.session_state.username[0].upper() if st.session_state.username else 'U'}
            </div>
            <div>
                <div class="user-name">{st.session_state.username}</div>
                <div class="user-email">{st.session_state.email}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if "current_tab" not in st.session_state:
            st.session_state.current_tab = "Dashboard"

        st.markdown("<div class='section-title'>Navigation</div>", unsafe_allow_html=True)
        
        nav_btn_style1 = "primary" if st.session_state.current_tab == "Dashboard" else "secondary"
        if st.button(t("dashboard"), use_container_width=True, type=nav_btn_style1):
            st.session_state.current_tab = "Dashboard"
            st.rerun()
            
        nav_btn_style2 = "primary" if st.session_state.current_tab == "Banking Assistant" else "secondary"
        if st.button(t("assistant"), use_container_width=True, type=nav_btn_style2):
            st.session_state.current_tab = "Banking Assistant"
            st.rerun()

        nav_btn_style_calc = "primary" if st.session_state.current_tab == "Calculators" else "secondary"
        if st.button(t("calculators"), use_container_width=True, type=nav_btn_style_calc):
            st.session_state.current_tab = "Calculators"
            st.rerun()

        if st.session_state.is_admin:
            nav_btn_style_admin = "primary" if st.session_state.current_tab == "Admin Panel" else "secondary"
            if st.button(t("admin_panel"), use_container_width=True, type=nav_btn_style_admin):
                st.session_state.current_tab = "Admin Panel"
                st.rerun()
        
        st.markdown(f"<div class='section-title'>{t('language')}</div>", unsafe_allow_html=True)
        language_options = ["English", "Hindi", "Marathi"]
        selected_language = st.selectbox(
            "Select Language",
            language_options,
            index=language_options.index(st.session_state.get("language", "English")),
            label_visibility="collapsed"
        )
        if selected_language != st.session_state.get("language", "English"):
            st.session_state.language = selected_language
            user_data = get_user_data(st.session_state.username)
            user_data["language"] = selected_language
            update_user_data(st.session_state.username, user_data)
            st.rerun()
            
        page = st.session_state.current_tab
        
        st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

        st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
        if st.button(t("logout"), use_container_width=True):
            logout()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Push Chat History to the bottom
        st.markdown("<div style='flex-grow: 1; min-height: 40px;'></div>", unsafe_allow_html=True) 
        
        st.markdown(f"<div class='section-title'>{t('recent_chats')}</div>", unsafe_allow_html=True)
        
        new_col, clear_col = st.columns([1, 1])
        with new_col:
            if st.button(t("new_chat"), use_container_width=True):
                st.session_state.messages = []
                st.session_state.current_chat_id = None
                st.rerun()
        with clear_col:
            if st.session_state.chat_sessions and st.button(t("clear_all"), use_container_width=True):
                clear_all_chat_history(st.session_state.username, st.session_state)
                st.session_state.messages = []
                st.session_state.current_chat_id = None
                st.rerun()

        # Chat Sessions
        st.markdown("<div class='chat-history-container'>", unsafe_allow_html=True)
        if st.session_state.chat_sessions:
            # Display only top 5 initially, or all if "show_all_chats" is True
            if "show_all_chats" not in st.session_state:
                st.session_state.show_all_chats = False
            
            display_chats = st.session_state.chat_sessions if st.session_state.show_all_chats else st.session_state.chat_sessions[:5]
            
            for chat in display_chats:
                preview = chat.get('preview', 'No messages')
                chat_id = chat['session_id']
                
                chat_col1, chat_col2 = st.columns([4, 1])
                with chat_col1:
                    if st.button(f"📄 {preview}", key=f"chat_{chat_id}", use_container_width=True):
                        st.session_state.messages = chat['messages']
                        st.session_state.current_chat_id = chat_id
                        st.rerun()
                with chat_col2:
                    if st.button("❌", key=f"del_{chat_id}", use_container_width=True):
                        delete_chat_session(st.session_state.username, st.session_state, chat_id)
                        if st.session_state.current_chat_id == chat_id:
                            st.session_state.messages = []
                            st.session_state.current_chat_id = None
                        st.rerun()
            
            # Show "See all" button if there are more than 5 chats
            if len(st.session_state.chat_sessions) > 5:
                if st.session_state.show_all_chats:
                    if st.button("See Less", use_container_width=True):
                        st.session_state.show_all_chats = False
                        st.rerun()
                else:
                    if st.button(f"See All ({len(st.session_state.chat_sessions)})", use_container_width=True):
                        st.session_state.show_all_chats = True
                        st.rerun()
        else:
            st.caption("No recent chats")
        st.markdown("</div>", unsafe_allow_html=True)

    st.title("Dashboard" if page == "Dashboard" else t("assistant") if page == "Banking Assistant" else t("calculators") if page == "Calculators" else t("admin_panel"))
    
    if page == "Dashboard":
        st.markdown("## 📊 Dashboard Overview")
        
        # Custom Metric Cards
        st.markdown(f"""
        <div style="display: flex; gap: 20px; margin-bottom: 2rem;">
            <div class="bank-card" style="flex: 1; text-align: center;">
                <div style="color: {st.session_state.colors['text_secondary']}; font-size: 0.9rem; margin-bottom: 8px;">{t('balance')}</div>
                <div style="font-size: 1.8rem; font-weight: 700;">{format_currency(st.session_state.balance)}</div>
            </div>
            <div class="bank-card" style="flex: 1; text-align: center;">
                <div style="color: {st.session_state.colors['text_secondary']}; font-size: 0.9rem; margin-bottom: 8px;">{t('interest_rate')}</div>
                <div style="font-size: 1.8rem; font-weight: 700;">{st.session_state.interest_rate}%</div>
            </div>
            <div class="bank-card" style="flex: 1; text-align: center;">
                <div style="color: {st.session_state.colors['text_secondary']}; font-size: 0.9rem; margin-bottom: 8px;">{t('active_loans')}</div>
                <div style="font-size: 1.8rem; font-size: 1.8rem; font-weight: 700;">{st.session_state.active_loans}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

        # 2 & 3. Insights & Health Score
        col_health, col_insights = st.columns(2)
        with col_health:
            st.markdown(f"""
            <div class="bank-card" style="height: 100%;">
                <h3 style="margin-top:0;">{t('health_score')}</h3>
                <div style="font-size: 2.5rem; font-weight: 700; color: {st.session_state.colors['primary']};">78 <span style="font-size: 1rem; color: {st.session_state.colors['text_secondary']};">/ 100</span></div>
                <div style="margin-top: 10px; font-size: 0.95rem; color: {st.session_state.colors['text_secondary']};">
                    <div style="margin-bottom: 4px;">✓ Good savings ratio</div>
                    <div style="margin-bottom: 4px;">✓ Low EMI burden</div>
                    <div>✓ Stable spending</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_insights:
            st.markdown(f"""
            <div class="bank-card" style="height: 100%;">
                <h3 style="margin-top:0;">{t('insights')}</h3>
                <div style="margin-top: 15px; font-size: 0.95rem; line-height: 1.6;">
                    <div style="margin-bottom: 8px;">📈 This month your spending increased by <b>12%</b> compared to last month.</div>
                    <div style="margin-bottom: 8px;">🛍️ Most spending category: <b>Shopping</b>.</div>
                    <div>⚠️ EMI due in <b>5 days</b>.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
            
        # 4 & 5. Net Worth & Upcoming Dues
        col_nw, col_dues = st.columns(2)
        with col_nw:
            st.markdown(f"""
            <div class="bank-card" style="height: 100%;">
                <h3 style="margin-top:0;">{t('net_worth')}</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 1rem;">
                    <span style="color: {st.session_state.colors['text_secondary']};">Assets (Savings + FD + Investments)</span>
                    <span style="font-weight: 600; color: {st.session_state.colors['success']};">{format_currency(st.session_state.balance + 3500000)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 16px; border-bottom: 1px solid {st.session_state.colors['border']}; padding-bottom: 12px; font-size: 1rem;">
                    <span style="color: {st.session_state.colors['text_secondary']};">Liabilities (Loans + Credit Dues)</span>
                    <span style="font-weight: 600; color: {st.session_state.colors['danger']};">{format_currency(st.session_state.total_loan_amount)}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 600; font-size: 1.1rem;">Total Net Worth</span>
                    <span style="font-size: 1.5rem; font-weight: 700; color: {st.session_state.colors['primary']};">{format_currency(st.session_state.balance + 3500000 - st.session_state.total_loan_amount)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_dues:
            st.markdown(f"""
            <div class="bank-card" style="height: 100%;">
                <h3 style="margin-top:0;">{t('upcoming_payments')}</h3>
                <div style="margin-top: 15px; font-size: 1rem; line-height: 1.6;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span>Home Loan EMI</span>
                        <div><span style="font-weight: 600;">₹12,000</span> <span style="font-size: 0.85rem; color: {st.session_state.colors['text_secondary']};">due 5 Mar</span></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <span>Credit Card Bill</span>
                        <div><span style="font-weight: 600;">₹8,400</span> <span style="font-size: 0.85rem; color: {st.session_state.colors['text_secondary']};">due 9 Mar</span></div>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Electricity Bill</span>
                        <div><span style="font-weight: 600;">₹1,500</span> <span style="font-size: 0.85rem; color: {st.session_state.colors['text_secondary']};">due 2 Mar</span></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 6. Fraud Alerts & Fund Transfer
        col_alerts, col_transfer = st.columns(2)
        with col_alerts:
            st.markdown(f"### 🚨 Security Alerts")
            alerts_summary = get_fraud_alerts_summary(st.session_state.username)
            if alerts_summary["total"] > 0:
                for alert in alerts_summary["alerts"]:
                    severity_color = st.session_state.colors['danger'] if alert['severity'] == 'high' else st.session_state.colors['warning']
                    st.markdown(f"""
                    <div class="bank-card" style="border-left: 4px solid {severity_color}; padding: 12px; margin-bottom: 8px;">
                        <div style="font-weight: 600; font-size: 0.9rem;">{alert['message']}</div>
                        <div style="font-size: 0.75rem; color: {st.session_state.colors['text_secondary']};">{alert['timestamp']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("Your account is secure. No suspicious activity detected.")

        with col_transfer:
            st.markdown(f"### {t('fund_transfer')}")
            with st.form("transfer_form", clear_on_submit=True):
                recipient = st.text_input(t("recipient"))
                amount = st.number_input(t("amount"), min_value=1.0, max_value=float(st.session_state.balance) if st.session_state.balance > 1.0 else 1.0, step=100.0)
                desc = st.text_input(t("description"), placeholder="Optional")
                submit_transfer = st.form_submit_button(t("transfer_btn"), use_container_width=True, type="primary")
                
                if submit_transfer:
                    if not recipient:
                        st.error("Recipient username is required")
                    elif recipient == st.session_state.username:
                        st.error("Cannot transfer to yourself")
                    else:
                        success, msg = transfer_funds(st.session_state.username, recipient, amount, category="Transfer", details=desc)
                        if success:
                            st.success(msg)
                            refresh_user_data(st.session_state.username)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(msg)

        st.divider()
        
        # Visualizations
        col_left, col_right = st.columns([2, 1])
        df = get_user_transactions_df(st.session_state.username)
        
        with col_left:
            st.write("### 📉 Income vs Expenses")
            if df.empty:
                st.info("No transactions yet. Make a transfer or add account activity to see your trends.")
            else:
                daily_data = df.groupby([pd.Grouper(key="Date", freq="D"), "Type"])["Amount"].sum().reset_index()
                fig_bar = px.bar(
                    daily_data,
                    x='Date',
                    y='Amount',
                    color='Type',
                    barmode='group',
                    color_discrete_map={"Income": st.session_state.colors['success'], "Expense": st.session_state.colors['danger']}
                )
                fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                if st.session_state.theme == "dark":
                    fig_bar.update_layout(font_color="white")
                else:
                    fig_bar.update_layout(font_color="black")
                st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_right:
            st.write("### 🍰 Expenses Breakdown")
            expense_df = df[df['Type'] == 'Expense']
            if expense_df.empty:
                st.info("No expense transactions recorded yet.")
            else:
                category_data = expense_df.groupby('Category')['Amount'].sum().reset_index()
                fig = px.pie(
                    category_data, 
                    values='Amount', 
                    names='Category',
                    hole=0.4,
                    color_discrete_sequence=[st.session_state.colors['primary'], st.session_state.colors['secondary'], '#38bdf8', '#818cf8', '#a78bfa', '#f472b6']
                )
                fig.update_layout(
                    margin=dict(t=0, b=0, l=0, r=0), 
                    height=300,
                    showlegend=False
                )
                # Ensure transparent background for the chart
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                if st.session_state.theme == "dark":
                    fig.update_layout(font_color="white")
                else:
                    fig.update_layout(font_color="black")
                    
                st.plotly_chart(fig, use_container_width=True)

        st.divider()
        
        # Consolidated Transactions
        st.markdown("### 📝 Recent Transaction History")
        if df.empty:
            st.info("Your transaction history will appear here after your first account activity.")
        else:
            history_df = df.copy()
            history_df["Date"] = history_df["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
            history_df["Amount"] = history_df["Amount"].map(format_currency)
            st.dataframe(
                history_df[["Date", "Direction", "Type", "Category", "Amount", "Details"]],
                use_container_width=True,
                hide_index=True
            )

    elif page == "Banking Assistant":
        is_connected = check_ollama_connection()
        col_h1, col_h2 = st.columns([4, 1])
        with col_h2:
            backend = get_active_backend()
            if is_connected:
                label = "☁️ Groq AI" if backend == "groq" else "🟢 Ollama"
                st.markdown(f'<div class="status-badge status-online"><span>●</span> {label}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-badge status-offline"><span>○</span> Offline</div>', unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        
        # FAQ Suggestions
        st.markdown(f"<div style='margin-bottom: 10px; font-size: 0.9rem; color: #64748b;'><strong>{t('popular_questions')}</strong></div>", unsafe_allow_html=True)
        
        faq_row1_col1, faq_row1_col2, faq_row1_col3 = st.columns(3)
        with faq_row1_col1:
            if st.button(t("btn_balance"), use_container_width=True):
                st.session_state.faq_trigger = "What is my balance?"
                st.rerun()
        with faq_row1_col2:
            if st.button(t("btn_interest"), use_container_width=True):
                st.session_state.faq_trigger = "What are the current interest rates?"
                st.rerun()
        with faq_row1_col3:
            if st.button(t("btn_support"), use_container_width=True):
                st.session_state.faq_trigger = "How do I contact customer care?"
                st.rerun()
        
        faq_row2_col1, faq_row2_col2, faq_row2_col3 = st.columns(3)
        with faq_row2_col1:
            if st.button(t("btn_hours"), use_container_width=True):
                st.session_state.faq_trigger = "What are the working hours?"
                st.rerun()
        with faq_row2_col2:
            if st.button(t("btn_min_bal"), use_container_width=True):
                st.session_state.faq_trigger = "What is the minimum balance?"
                st.rerun()
        with faq_row2_col3:
            if st.button(t("btn_fd_rates"), use_container_width=True):
                st.session_state.faq_trigger = "What are the FD rates?"
                st.rerun()
            
        st.markdown(f"<div style='margin-bottom: 10px; font-size: 0.9rem; color: #64748b;'><strong>{t('upload_statement')}</strong></div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(t("upload_statement"), type=["pdf"], label_visibility="collapsed")
        if uploaded_file:
            if st.button("Analyze Statement", type="primary"):
                with st.spinner(t("analyzing")):
                    text, error = extract_text_from_pdf(uploaded_file)
                    if text:
                        st.session_state.faq_trigger = "I have uploaded a bank statement. Please summarize it: " + text[:1500]
                        st.session_state.faq_display = "I have uploaded a bank statement. Please summarize it."
                    else:
                        st.error(f"Failed to extract text from PDF: {error}")
        
        # 🎙️ Voice Support UI

            
        chat_container = st.container(height=400, border=False)
        
        with chat_container:
            for message in st.session_state.messages:
                role = message["role"]
                display_content = message.get("display_content", message["content"])
                if role == "user":
                    st.markdown(f'<div class="user-bubble">{display_content}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="ai-bubble">{display_content}</div>', unsafe_allow_html=True)

        prompt = st.chat_input(t("chat_input"))
        
        display_prompt = prompt
        is_pdf_analysis = False
        if getattr(st.session_state, 'faq_trigger', None):
            prompt = st.session_state.faq_trigger
            display_prompt = getattr(st.session_state, 'faq_display', None) or prompt
            is_pdf_analysis = (st.session_state.get('faq_display') or '').startswith("I have uploaded")
            st.session_state.faq_trigger = None
            st.session_state.faq_display = None
            
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt, "display_content": display_prompt})
            
            with chat_container:
                st.markdown(f'<div class="user-bubble">{display_prompt}</div>', unsafe_allow_html=True)
                
                # Skip FAQ for PDF analysis — send directly to AI
                faq_response = None if is_pdf_analysis else get_faq_response(prompt, language=st.session_state.get("language", "English"))
                
                res_box = st.empty()
                full_response = ""
                
                if faq_response:
                    full_response = faq_response
                    res_box.markdown(f'<div class="ai-bubble">{full_response}</div>', unsafe_allow_html=True)
                elif is_pdf_analysis or is_banking_query(prompt):
                    if check_ollama_connection():
                        last_update_time = time.time()
                        for chunk in stream_ai_response(prompt, history=st.session_state.messages[:-1]):
                            if chunk:
                                full_response += chunk
                                current_time = time.time()
                                if current_time - last_update_time > 0.05:
                                    res_box.markdown(f'<div class="ai-bubble">{full_response}▌</div>', unsafe_allow_html=True)
                                    last_update_time = current_time
                        
                        res_box.markdown(f'<div class="ai-bubble">{full_response}</div>', unsafe_allow_html=True)
                    else:
                        full_response = "I'm having trouble reaching the AI engine right now. However, I can still help with basic queries like your balance or interest rates. How can I assist you?"
                        res_box.markdown(f'<div class="ai-bubble">{full_response}</div>', unsafe_allow_html=True)
                else:
                    # Non-banking refusal
                    full_response = "I am a banking assistant and can only answer banking-related queries. Please feel free to ask about accounts, loans, cards, or other financial services."
                    res_box.markdown(f'<div class="ai-bubble">{full_response}</div>', unsafe_allow_html=True)
            
            if not full_response:
                full_response = "I'm having trouble reaching the main AI engine right now. However, I can still help with basic queries like your balance or interest rates. How can I assist you?"
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # 🔊 Handle Text-to-Speech
            # Voice input and TTS removed
            # Save using the persistent utility
            new_id = save_chat_session(st.session_state.username, st.session_state, st.session_state.messages, st.session_state.current_chat_id)
            if not st.session_state.current_chat_id:
                st.session_state.current_chat_id = new_id
            
            st.rerun()

    elif page == "Calculators":
        calc_tab1, calc_tab2, calc_tab3 = st.tabs(["EMI Calculator", "FD Calculator", "RD Calculator"])
        
        with calc_tab1:
            st.markdown("### EMI Calculator")
            p = st.number_input("Principal Amount (₹)", min_value=1000, max_value=100000000, value=100000, step=1000)
            r = st.number_input("Annual Interest Rate (%)", min_value=1.0, max_value=30.0, value=8.5, step=0.1)
            n = st.number_input("Loan Tenure (Years)", min_value=1, max_value=30, value=5, step=1)
            if st.button("Calculate EMI"):
                r_monthly = (r / 12) / 100
                n_months = n * 12
                emi = (p * r_monthly * (1 + r_monthly)**n_months) / ((1 + r_monthly)**n_months - 1)
                st.success(f"Your Monthly EMI is: {format_currency(emi)}")
                st.info(f"Total Amount Payable: {format_currency(emi * n_months)}")
                st.info(f"Total Interest: {format_currency((emi * n_months) - p)}")
        
        with calc_tab2:
            st.markdown("### Fixed Deposit (FD) Calculator")
            p_fd = st.number_input("Deposit Amount (₹)", min_value=1000, max_value=100000000, value=100000, step=1000, key="fd_p")
            r_fd = st.number_input("Annual Interest Rate (%)", min_value=1.0, max_value=15.0, value=7.0, step=0.1, key="fd_r")
            n_fd = st.number_input("Time Period (Years)", min_value=1, max_value=20, value=1, step=1, key="fd_n")
            if st.button("Calculate FD Maturity"):
                amount = p_fd * (1 + (r_fd/100)/4)**(4*n_fd)
                st.success(f"Maturity Amount: {format_currency(amount)}")
                st.info(f"Wealth Gained: {format_currency(amount - p_fd)}")
                
        with calc_tab3:
            st.markdown("### Recurring Deposit (RD) Calculator")
            p_rd = st.number_input("Monthly Investment (₹)", min_value=100, max_value=1000000, value=1000, step=100, key="rd_p")
            r_rd = st.number_input("Annual Interest Rate (%)", min_value=1.0, max_value=15.0, value=6.5, step=0.1, key="rd_r")
            n_rd = st.number_input("Time Period (Years)", min_value=1, max_value=20, value=1, step=1, key="rd_n")
            if st.button("Calculate RD Maturity"):
                months = n_rd * 12
                i = (r_rd / 100) / 12
                amount = p_rd * (((1+i)**months - 1) / i) * (1+i)
                total_invested = p_rd * months
                st.success(f"Maturity Amount: {format_currency(amount)}")
                st.info(f"Total Invested: {format_currency(total_invested)}")
                st.info(f"Wealth Gained: {format_currency(amount - total_invested)}")
        
        with st.expander("🚀 Loan Eligibility Calculator"):
            st.markdown("### Check Your Loan Eligibility")
            monthly_income = st.number_input("Your Monthly Income (₹)", min_value=5000, value=50000, step=1000)
            existing_emis = st.number_input("Existing Monthly EMIs (₹)", min_value=0, value=0, step=500)
            tenure_elig = st.slider("Loan Tenure (Years)", 1, 30, 5)
            
            if st.button("Check Eligibility"):
                max_p, possible_emi = calculate_loan_eligibility(monthly_income, existing_emis, tenure_elig)
                if max_p > 0:
                    st.success(f"You are eligible for a loan up to: **{format_currency(max_p)}**")
                    st.info(f"Estimated Monthly EMI: {format_currency(possible_emi)}")
                else:
                    st.error("Based on your current income and EMIs, you may not be eligible for a new loan at this time.")

    elif page == "Admin Panel" and st.session_state.is_admin:
        st.write("Welcome to the Admin Dashboard.")
        
        users = get_persisted_users()
        
        st.markdown("### 👥 User Management")
        user_data_list = []
        for uname, udata in users.items():
            user_data_list.append({
                "Username": uname,
                "Email": udata.get("email", ""),
                "Admin": udata.get("is_admin", False),
                "Balance": udata.get("balance", 0.0),
                "Language": udata.get("language", "English")
            })
        if user_data_list:
            st.dataframe(pd.DataFrame(user_data_list), use_container_width=True)
        
        st.markdown("### 🚨 Fraud Alerts Overview")
        all_alerts = []
        for uname in users:
            alerts = check_fraud_alerts(uname)
            for a in alerts:
                a['username'] = uname
                all_alerts.append(a)
                
        if all_alerts:
            for alert in all_alerts:
                if alert['severity'] == 'high':
                    st.error(f"**{alert['username']}**: {alert['message']} ({alert['timestamp']})")
                else:
                    st.warning(f"**{alert['username']}**: {alert['message']} ({alert['timestamp']})")
        else:
            st.success("No fraud alerts at the moment.")

        st.markdown("### 📚 Knowledge Base (Intents)")
        intents = load_intents()
        if intents:
            with st.expander("Edit Intents JSON"):
                intents_json = st.text_area("Intents JSON", value=json.dumps(intents, indent=4), height=300)
                if st.button("Save Intents"):
                    try:
                        new_intents = json.loads(intents_json)
                        if save_intents(new_intents):
                            st.success("Intents updated successfully!")
                            st.cache_data.clear()
                        else:
                            st.error("Failed to save intents")
                    except Exception as e:
                        st.error(f"Invalid JSON: {e}")

if not st.session_state.logged_in:
    if st.session_state.current_page == "login":
        show_login_page()
    elif st.session_state.current_page == "signup":
        show_signup_page()
else:
    show_dashboard()
