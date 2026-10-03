"""
CampusFix: Intelligent Campus Maintenance & Operations SaaS System
Streamlit Application File with Gemini Vision + Multi-Turn Chat + Resend Email API Dispatch
"""

import json
import os
import random
import time
from datetime import datetime

import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import resend
import streamlit as st

# Import prompt templates module
import prompts

# ---------------------------------------------------------
# Page Configuration & Custom SaaS CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="CampusFix | Campus Operations & Facilities Management",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject Premium Dark SaaS CSS Styling & Responsive Mobile Breakpoints
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Main Application Overrides */
    .stApp {
        background-color: #0b0f19;
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
        color: #f1f5f9;
        overflow-x: hidden !important;
    }
    
    /* Clean Chrome & Hide Default Clutter & Sidebar */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent; display: none !important;}
    section[data-testid="stSidebar"] {display: none !important;}
    
    /* Expand Main Container to Full Width */
    .stMainBlockContainer {
        padding-top: 1.2rem !important;
        max-width: 98% !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0b0f19;
    }
    ::-webkit-scrollbar-thumb {
        background: #1e293b;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }

    /* Top Navbar Wrapper */
    .top-navbar-wrapper {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 10px 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.35);
    }

    /* Horizontal Radio Group Top Navbar Styling */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 8px !important;
        flex-wrap: nowrap !important;
    }

    /* Hide Radio Dots/Circles */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }

    /* Horizontal Navbar Items */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-bottom: 3px solid transparent !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        margin: 0 !important;
        color: #94a3b8 !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
        word-break: keep-all !important;
    }

    /* Hover State */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:hover {
        background-color: #1e293b !important;
        color: #f8fafc !important;
    }

    /* Checked / Active Top Navbar Item State */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        background: rgba(2, 132, 199, 0.2) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-bottom: 3px solid #38bdf8 !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.2) !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"] {
        background: rgba(2, 132, 199, 0.2) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-bottom: 3px solid #38bdf8 !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }

    /* Popover Button Styling */
    div[data-testid="stPopover"] > button {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 4px 12px !important;
        font-size: 0.8rem !important;
        height: 34px !important;
    }

    .status-badge {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #0284c7;
        color: #38bdf8;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 2px 10px rgba(56, 189, 248, 0.15);
    }
    
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 10px #22c55e;
    }

    .pulse-dot-demo {
        width: 8px;
        height: 8px;
        background-color: #f59e0b;
        border-radius: 50%;
        box-shadow: 0 0 10px #f59e0b;
    }

    /* KPI Summary Cards */
    .kpi-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .kpi-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
    }

    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 2px;
    }

    .kpi-label {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
    }

    /* Workflow Step Cards */
    .step-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    .step-header {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.05rem;
        font-weight: 700;
        color: #38bdf8;
    }

    .step-num {
        background: #0284c7;
        color: #ffffff;
        min-width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        font-weight: 800;
    }

    /* Polished Triage Card */
    .triage-card-v2 {
        background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #38bdf8;
        border-radius: 16px;
        padding: 24px;
        margin-top: 20px;
        box-shadow: 0 10px 30px rgba(56, 189, 248, 0.12);
    }

    /* Action & Section Cards */
    .action-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    /* Urgency Badges */
    .badge-emergency {
        background-color: #450a0a;
        color: #fca5a5;
        border: 1px solid #ef4444;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.85rem;
    }
    .badge-high {
        background-color: #431407;
        color: #fdba74;
        border: 1px solid #f97316;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.85rem;
    }
    .badge-medium {
        background-color: #422006;
        color: #fde047;
        border: 1px solid #eab308;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.85rem;
    }
    .badge-low {
        background-color: #052e16;
        color: #86efac;
        border: 1px solid #22c55e;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.85rem;
    }

    /* Status Badges */
    .badge-status-pending {
        background-color: #431407;
        color: #fdba74;
        border: 1px solid #f97316;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .badge-status-inprog {
        background-color: #422006;
        color: #fde047;
        border: 1px solid #eab308;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .badge-status-resolved {
        background-color: #052e16;
        color: #86efac;
        border: 1px solid #22c55e;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.8rem;
    }

    /* Form & Input Styling Overrides */
    div[data-baseweb="input"] {
        background-color: #0f172a !important;
        border-color: #334155 !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: #0f172a !important;
        border-color: #334155 !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
    }

    textarea {
        background-color: #0f172a !important;
        border-color: #334155 !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
    }

    .stButton>button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        border: 1px solid #38bdf8 !important;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.3) !important;
    }

    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.4) !important;
        transform: translateY(-1px);
    }

    /* =========================================================
       RESPONSIVE MOBILE BREAKPOINTS (<= 768px & <= 480px)
       Desktop layout (>768px) remains completely untouched!
       ========================================================= */
    @media (max-width: 768px) {
        .stMainBlockContainer {
            padding-left: 10px !important;
            padding-right: 10px !important;
            padding-top: 0.8rem !important;
            max-width: 100% !important;
        }

        /* Responsive Top Navbar */
        div[data-testid="stRadio"] div[role="radiogroup"] {
            flex-wrap: wrap !important;
            justify-content: flex-start !important;
            gap: 6px !important;
        }

        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] {
            padding: 6px 12px !important;
            font-size: 0.82rem !important;
            white-space: nowrap !important;
            word-break: keep-all !important;
            flex-grow: 1 !important;
            text-align: center !important;
            justify-content: center !important;
        }

        /* KPI Cards 2x2 Grid on Mobile */
        .kpi-grid-wrapper > div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 10px !important;
        }

        .kpi-grid-wrapper > div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            width: 100% !important;
            min-width: 0 !important;
        }

        .kpi-card {
            padding: 12px 14px !important;
        }

        .kpi-value {
            font-size: 1.45rem !important;
        }

        .kpi-label {
            font-size: 0.7rem !important;
        }

        /* Report Form Ordering: 01 Details -> 02 Upload Evidence -> 03 Describe Issue */
        .report-workflow-grid > div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: column !important;
        }

        .step-box-1 { order: 1 !important; }
        .step-box-2 { order: 2 !important; margin-top: 14px; margin-bottom: 14px; }
        .step-box-3 { order: 3 !important; }

        /* Full Width Buttons on Mobile */
        .stButton > button {
            width: 100% !important;
        }

        /* Mobile Action Cards Padding */
        .action-card, .triage-card-v2, .step-card {
            padding: 16px !important;
            border-radius: 12px !important;
        }

        /* Responsive Chart Scaling */
        .js-plotly-plot, .plot-container {
            width: 100% !important;
            max-width: 100% !important;
        }
    }

    @media (max-width: 480px) {
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] {
            font-size: 0.78rem !important;
            padding: 5px 8px !important;
        }
        
        .kpi-value {
            font-size: 1.3rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Persistence & Session State Setup
# ---------------------------------------------------------
DATA_FILE = "tickets.json"

SAMPLE_TICKETS = [
    {
        "ticket_id": "CF-2026-1001",
        "timestamp": "2026-10-01 09:15:00",
        "reporter": "Alex Rivera",
        "reporter_email": "arivera@campus.edu",
        "building": "Science & Engineering Complex",
        "room": "Lab 304",
        "title": "Exposed Wiring Near Fume Hood",
        "description": "Loose high-voltage wiring dangling from ceiling electrical conduit above lab workbench 3.",
        "category": "Electrical & Lighting",
        "urgency": "Emergency / Immediate Hazard",
        "urgency_score": 9,
        "assigned_department": "Campus Electrical Services",
        "status": "In Progress",
        "summary": "Hazardous exposed electrical conductors dangling near water fixture.",
        "suggested_action_plan": ["Power off circuit breaker SEC-3B immediately", "Insulate bare wires", "Replace conduit junction cover"],
        "required_tools": ["Multimeter", "Insulated pliers", "Wire nuts", "Junction box cover"],
        "estimated_repair_time": "1-2 hours",
        "technician_notes": "Breaker isolated. Replacement box cover ordered."
    },
    {
        "ticket_id": "CF-2026-1002",
        "timestamp": "2026-10-02 11:30:00",
        "reporter": "Prof. Sarah Chen",
        "reporter_email": "schen@campus.edu",
        "building": "Student Union Center",
        "room": "2nd Floor Restroom",
        "title": "Severe Water Leak from Sink Pipe",
        "description": "Continuous water stream pooling across main walkway floor from sink #2 pipe joint.",
        "category": "Plumbing & Sanitation",
        "urgency": "High Priority",
        "urgency_score": 7,
        "assigned_department": "Plumbing & Utilities",
        "status": "Pending",
        "summary": "Active P-trap pipe leak causing floor flooding and potential slipping hazard.",
        "suggested_action_plan": ["Shut off supply valve below sink", "Replace worn rubber gasket", "Test pressure flow"],
        "required_tools": ["Pipe wrench", "Plumber's tape", "Replacement gasket"],
        "estimated_repair_time": "45 minutes",
        "technician_notes": ""
    },
    {
        "ticket_id": "CF-2026-1003",
        "timestamp": "2026-10-02 14:00:00",
        "reporter": "David Miller",
        "reporter_email": "dmiller@campus.edu",
        "building": "Central Library",
        "room": "Reading Room B",
        "title": "AC Unit Blowing Hot Air",
        "description": "Thermostat reads 82°F despite setting to 68°F. Room is uncomfortably hot.",
        "category": "HVAC & Climate Control",
        "urgency": "Medium Priority",
        "urgency_score": 5,
        "assigned_department": "Central HVAC Team",
        "status": "In Progress",
        "summary": "HVAC zone air handling unit cooling coil malfunction.",
        "suggested_action_plan": ["Inspect refrigerant pressure", "Check actuator valve", "Clean air filters"],
        "required_tools": ["Refrigerant gauge manifold", "Filter replacement"],
        "estimated_repair_time": "2-3 hours",
        "technician_notes": "Filter replaced, checking compressor pressure."
    }
]

def load_tickets():
    """Load tickets from JSON storage or initialize sample data."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return SAMPLE_TICKETS
    else:
        save_tickets(SAMPLE_TICKETS)
        return SAMPLE_TICKETS

def save_tickets(tickets):
    """Save tickets to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(tickets, f, indent=2)

if "tickets" not in st.session_state:
    st.session_state.tickets = load_tickets()

if "active_ticket" not in st.session_state:
    st.session_state.active_ticket = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------------
# API Credentials Helper Functions
# ---------------------------------------------------------
def get_api_key():
    """Retrieve Gemini API Key safely from Streamlit Secrets, environment, or sidebar input."""
    placeholders = ["your-gemini-api-key", "your_gemini_api_key", "your_google_gemini_api_key_here", "your_gemini_api_key_here", "YOUR_REAL_GEMINI_API_KEY", "YOUR_GEMINI_API_KEY", "your_real_gemini_api_key"]
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"] not in placeholders:
        return st.secrets["GEMINI_API_KEY"]
    if "google_api_key" in st.secrets and st.secrets["google_api_key"] not in placeholders:
        return st.secrets["google_api_key"]
    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if env_key:
        return env_key
    if "user_api_key" in st.session_state and st.session_state.user_api_key:
        return st.session_state.user_api_key
    return None

def send_maintenance_email(ticket):
    """
    Sends an official maintenance dispatch report using Resend Email API.
    Credentials come strictly from st.secrets (RESEND_API_KEY & MAINTENANCE_EMAIL).
    """
    resend_key = st.secrets.get("RESEND_API_KEY")
    recipient = st.secrets.get("MAINTENANCE_EMAIL")

    if not resend_key or resend_key in ["your_resend_api_key", "your-resend-api-key"]:
        return False, "Resend API Key missing in .streamlit/secrets.toml. Please configure RESEND_API_KEY."

    if not recipient or recipient in ["maintenance@example.com"]:
        return False, "MAINTENANCE_EMAIL missing or default placeholder in .streamlit/secrets.toml."

    try:
        resend.api_key = resend_key

        subject = f"CampusFix Maintenance Report - [{ticket.get('title', 'Campus Issue')}]"
        
        body = f"""CampusFix Official Facilities Maintenance Incident Report
----------------------------------------------------------------------
Ticket ID:           {ticket.get('ticket_id')}
Date & Time:         {ticket.get('timestamp')}
Reporter Name:       {ticket.get('reporter', 'Anonymous')}
Reporter Email:      {ticket.get('reporter_email', 'Not provided')}
Building Location:   {ticket.get('building')}
Room / Area:         {ticket.get('room')}
Category:            {ticket.get('category')}
Urgency Level:       {ticket.get('urgency')} (Score: {ticket.get('urgency_score')}/10)
Assigned Department: {ticket.get('assigned_department')}
Estimated Repair:    {ticket.get('estimated_repair_time')}

----------------------------------------------------------------------
ISSUE TITLE:
{ticket.get('title')}

ISSUE DESCRIPTION:
{ticket.get('description')}

----------------------------------------------------------------------
AI EXECUTIVE TRIAGE SUMMARY:
{ticket.get('summary')}

----------------------------------------------------------------------
SAFETY HAZARDS & PRECAUTIONS:
"""
        for hazard in ticket.get('safety_hazards', []):
            body += f"• {hazard}\n"
            
        body += "\nRECOMMENDED TECHNICIAN ACTION PLAN:\n"
        for i, step in enumerate(ticket.get('suggested_action_plan', []), 1):
            body += f"{i}. {step}\n"
            
        body += "\nREQUIRED TOOLS & EQUIPMENT:\n"
        body += ", ".join(ticket.get('required_tools', [])) + "\n"
        
        body += "\n----------------------------------------------------------------------\n"
        body += "Automated Facilities Dispatch generated by CampusFix System via Resend."

        params = {
            "from": "CampusFix Dispatch <onboarding@resend.dev>",
            "to": [recipient],
            "subject": subject,
            "text": body,
        }

        response = resend.Emails.send(params)
        
        if isinstance(response, dict) and "id" in response:
            return True, f"Maintenance report sent successfully via Resend (ID: {response['id']})."
        elif hasattr(response, "id"):
            return True, f"Maintenance report sent successfully via Resend (ID: {response.id})."
        else:
            return True, "Maintenance report sent successfully via Resend."
    except Exception as e:
        err_msg = str(e)
        if resend_key and resend_key in err_msg:
            err_msg = err_msg.replace(resend_key, "re_*****")
        return False, f"Resend API Error: {err_msg}"

# ---------------------------------------------------------
# Gemini AI Analysis & Chat Functions
# ---------------------------------------------------------
def sanitize_gemini_error(e, api_key=None):
    """Categorizes and sanitizes Gemini API errors without exposing secret API keys."""
    err_str = str(e)
    if api_key and api_key in err_str:
        err_str = err_str.replace(api_key, "AIza*****")
    
    err_lower = err_str.lower()
    if "503" in err_lower or "unavailable" in err_lower or "high demand" in err_lower:
        category = "503 Server Unavailable / High Demand"
    elif "api key not valid" in err_lower or ("400" in err_lower and "key" in err_lower) or "unauthorized" in err_lower or "401" in err_lower or "permission" in err_lower:
        category = "Authentication/Permission Error (Invalid API Key)"
    elif "404" in err_lower or "not found" in err_lower or "model" in err_lower:
        category = "Model Unavailable Error"
    elif "429" in err_lower or "quota" in err_lower or "rate" in err_lower or "resource_exhausted" in err_lower:
        category = "Quota/Rate-Limit Error"
    elif "connection" in err_lower or "network" in err_lower or "timeout" in err_lower:
        category = "Network Connection Error"
    else:
        category = "Invalid Request / API Error"
        
    return f"{category}: {err_str[:250]}"

def is_temporary_gemini_error(e):
    """Determines if a Gemini API exception is a temporary availability/capacity/network error (503, UNAVAILABLE, 429)."""
    err_str = str(e).lower()
    return any(term in err_str for term in [
        "503", "unavailable", "high demand", "temporary",
        "429", "resource_exhausted", "quota", "rate limit",
        "connection", "timeout", "econnreset"
    ])

def analyze_issue_with_gemini(api_key, text_description, building, room, image=None):
    """Call Google Gemini Vision API to triage incident. Returns (triage_dict, is_offline, error_msg)."""
    prompt_content = f"""
Building Location: {building}
Room / Area: {room}
Issue Description: {text_description}

Analyze this maintenance report according to your system instructions.
"""
    
    if not api_key:
        return generate_mock_triage_result(text_description, building, room), True, None

    # Try modern google-genai SDK with gemini-3.8-flash and 3-attempt exponential backoff on temporary 503 errors
    max_retries = 3
    delays = [2, 4, 8]
    
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        contents = [prompts.ISSUE_TRIAGE_SYSTEM_PROMPT, prompt_content]
        if image is not None:
            contents.append(image)
            
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=contents
                )
                cleaned_json = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                return json.loads(cleaned_json), False, None
            except Exception as e_attempt:
                if attempt < max_retries - 1 and is_temporary_gemini_error(e_attempt):
                    time.sleep(delays[attempt])
                else:
                    raise e_attempt
    except Exception as e_genai:
        err_diag = sanitize_gemini_error(e_genai, api_key)
        return None, True, err_diag

def generate_mock_triage_result(text_desc, building, room):
    """Generates an offline demo response clearly labeled [DEMO / OFFLINE MODE]."""
    text_lower = text_desc.lower()
    
    if any(k in text_lower for k in ["wire", "spark", "electric", "shock", "outlet", "voltage"]):
        cat = "Electrical & Lighting"
        urgency = "Emergency / Immediate Hazard"
        score = 9
        dept = "Campus Electrical Services"
        hazards = ["Shock hazard appears present", "Fire risk from exposed conductor"]
        tools = ["Multimeter", "Insulated Screwdriver", "Wire Strippers", "Electrical Tape"]
    elif any(k in text_lower for k in ["water", "leak", "pipe", "flood", "toilet", "drain", "sink"]):
        cat = "Plumbing & Sanitation"
        urgency = "High Priority"
        score = 8
        dept = "Plumbing & Utilities"
        hazards = ["Slipping hazard on floor", "Possible subfloor water damage"]
        tools = ["Pipe Wrench", "Plumber's Tape", "Drain Snake"]
    elif any(k in text_lower for k in ["ac", "heat", "hot", "cold", "hvac", "thermostat", "vent"]):
        cat = "HVAC & Climate Control"
        urgency = "Medium Priority"
        score = 5
        dept = "Central HVAC Team"
        hazards = ["Thermal discomfort for occupants"]
        tools = ["Temperature Probe", "Air Filter Unit", "Refrigerant Gauge"]
    elif any(k in text_lower for k in ["wifi", "internet", "network", "cable", "router", "server"]):
        cat = "IT & Network Infrastructure"
        urgency = "Medium Priority"
        score = 6
        dept = "IT Field Support"
        hazards = ["Disruption to academic network connectivity"]
        tools = ["Cat6 Tester", "Console Cable", "PoE Injector"]
    else:
        cat = "Furniture & Carpentry"
        urgency = "Low / Routine"
        score = 3
        dept = "Carpentry & Hardware"
        hazards = ["Minor mechanical pinch hazard"]
        tools = ["Cordless Drill", "Screws", "Level"]

    return {
        "category": cat,
        "urgency": urgency,
        "urgency_score": score,
        "assigned_department": dept,
        "summary": f"[DEMO / OFFLINE MODE] Triage analysis indicates a {cat.lower()} issue at {building} ({room}).",
        "detailed_analysis": f"[DEMO / OFFLINE MODE] Evaluated description: '{text_desc}'. Defect appears related to {cat}.",
        "safety_hazards": hazards,
        "suggested_action_plan": [
            f"Dispatch technician from {dept} to inspect {room} at {building}.",
            "Inspect physical hardware and isolate circuit or shutoff valve if necessary.",
            "Complete repair and record resolution in CampusFix log."
        ],
        "required_tools_equipment": tools,
        "estimated_repair_time": "1-2 hours",
        "student_notification": f"[DEMO / OFFLINE MODE] Thank you for reporting this issue at {building}. Campus Operations has dispatched {dept}."
    }

def run_gemini_chat(api_key, ticket_context, user_message, chat_history):
    """
    Executes real multi-turn Gemini AI chat using full ticket context and chat trajectory.
    Does NOT return hardcoded mock responses.
    """
    if not api_key:
        return "⚠️ **Interactive AI Chat Unavailable**: Real multi-turn chat requires a valid Gemini API key. Please enter your API Key in the sidebar settings."

    system_prompt = prompts.INTERACTIVE_CHAT_SYSTEM_PROMPT.format(
        ticket_id=ticket_context.get("ticket_id", "N/A"),
        building=ticket_context.get("building", "N/A"),
        room=ticket_context.get("room", "N/A"),
        title=ticket_context.get("title", "N/A"),
        description=ticket_context.get("description", "N/A"),
        category=ticket_context.get("category", "N/A"),
        urgency=ticket_context.get("urgency", "N/A"),
        urgency_score=ticket_context.get("urgency_score", "N/A"),
        assigned_department=ticket_context.get("assigned_department", "N/A"),
        summary=ticket_context.get("summary", "N/A"),
        safety_hazards=", ".join(ticket_context.get("safety_hazards", [])),
        suggested_action_plan="; ".join(ticket_context.get("suggested_action_plan", []))
    )

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        contents = [system_prompt]
        for msg in chat_history:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            contents.append(f"{role_label}: {msg['content']}")
            
        contents.append(f"User: {user_message}\nAssistant:")
        
        max_retries = 3
        delays = [2, 4, 8]
        
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=contents
                )
                return response.text
            except Exception as e_attempt:
                if attempt < max_retries - 1 and is_temporary_gemini_error(e_attempt):
                    time.sleep(delays[attempt])
                else:
                    raise e_attempt
    except Exception as e_genai:
        err_diag = sanitize_gemini_error(e_genai, api_key)
        if is_temporary_gemini_error(e_genai):
            return f"⚠️ **Gemini Server High Demand**: Gemini API is temporarily experiencing high server demand after 3 retry attempts [{err_diag}]. Please try your question again in a moment."
        else:
            return f"❌ Error communicating with Gemini Chat [{err_diag}]"

def generate_ai_insights(api_key, tickets_df):
    """Generate strategic executive maintenance report using Gemini."""
    if not api_key:
        return """### 📊 [DEMO / OFFLINE MODE] Campus Infrastructure Health Summary
- **Top Issue Category**: Electrical & Lighting and Plumbing account for 60% of current reports.
- **Hotspot Location**: Science & Engineering Complex shows highest incident frequency.
- **Preventive Recommendation**: Schedule quarterly electrical conduit audits and plumbing pressure tests in academic labs.
- **Resource Allocation**: Deploy additional technicians to Campus Electrical Services during peak hours.
"""
    try:
        summary_text = tickets_df[["ticket_id", "building", "category", "urgency", "status"]].to_string()
        prompt = f"{prompts.ANALYTICS_INSIGHTS_PROMPT}\n\nRecent ticket dataset:\n{summary_text}"
        
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        err_diag = sanitize_gemini_error(e, api_key)
        return f"Unable to generate live AI insights [{err_diag}]."

# ---------------------------------------------------------
# TOP HORIZONTAL NAVBAR & BRANDING
# ---------------------------------------------------------
NAV_REPORT = "📝 Report Issue"
NAV_TRACKING = "🎫 Tickets"
NAV_WORKSTATION = "🔧 Technician"
NAV_ANALYTICS = "📊 Analytics"
NAV_KNOWLEDGE = "📚 Knowledge"

has_api = bool(get_api_key())
dot_class = "pulse-dot" if has_api else "pulse-dot-demo"
ai_status_text = "AI Online" if has_api else "AI Offline Demo"

nav_col1, nav_col2, nav_col3 = st.columns([1.3, 3.2, 1.3], gap="small")

with nav_col1:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; padding: 2px 0;">
        <span style="font-size: 1.8rem; line-height: 1;">🛠️</span>
        <div>
            <div style="font-size: 1.3rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em; line-height: 1.1;">CampusFix</div>
            <div style="font-size: 0.75rem; font-weight: 600; color: #38bdf8; margin-top: 1px;">See it. Report it. Fix it.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with nav_col2:
    navigation = st.radio(
        "Top Navigation",
        [
            NAV_REPORT,
            NAV_TRACKING,
            NAV_WORKSTATION,
            NAV_ANALYTICS,
            NAV_KNOWLEDGE
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

with nav_col3:
    status_col_a, status_col_b = st.columns([1.2, 1])
    with status_col_a:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; align-items: center; height: 38px;">
            <div class="status-badge" style="padding: 6px 12px; font-size: 0.78rem;">
                <span class="{dot_class}"></span>
                <span>{ai_status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with status_col_b:
        api_key_val = get_api_key()
        with st.popover("⚡ Status"):
            st.markdown("#### ⚡ Service Credentials Status")
            if api_key_val:
                st.success("✅ Gemini API Connected")
            else:
                st.warning("⚠️ No Gemini API Key set (DEMO Mode)")
                
            user_key_input = st.text_input("Enter Gemini API Key:", type="password", key="key_input_box")
            if user_key_input:
                st.session_state.user_api_key = user_key_input
                st.rerun()

            st.divider()
            st.caption("📧 Resend Email API Status:")
            resend_key = st.secrets.get("RESEND_API_KEY")
            maint_email = st.secrets.get("MAINTENANCE_EMAIL")
            if resend_key and resend_key not in ["your_resend_api_key", "your-resend-api-key"]:
                st.success("✅ Resend Connected")
                st.caption(f"Recipient: {maint_email}")
            else:
                st.info("ℹ️ Resend Key not set in secrets.toml")

# ---------------------------------------------------------
# DASHBOARD SUMMARY KPI CARDS (2x2 Grid on Mobile)
# ---------------------------------------------------------
total_tickets = len(st.session_state.tickets)
high_priority_count = sum(1 for t in st.session_state.tickets if any(term in str(t.get("urgency", "")).lower() for term in ["emergency", "high"]) or t.get("urgency_score", 0) >= 7)
pending_count = sum(1 for t in st.session_state.tickets if t.get("status") == "Pending")
ai_indicator = "Online" if has_api else "Demo Mode"
ai_color = "#22c55e" if has_api else "#f59e0b"

st.markdown('<div class="kpi-grid-wrapper">', unsafe_allow_html=True)
kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
with kpi_c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">TOTAL TICKETS</div>
        <div class="kpi-value">{total_tickets}</div>
        <div style="font-size: 0.75rem; color: #64748b;">Active campus records</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">HIGH PRIORITY</div>
        <div class="kpi-value" style="color: #ef4444;">{high_priority_count}</div>
        <div style="font-size: 0.75rem; color: #64748b;">Urgent / Emergency</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">PENDING</div>
        <div class="kpi-value" style="color: #f59e0b;">{pending_count}</div>
        <div style="font-size: 0.75rem; color: #64748b;">Awaiting dispatch</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">AI STATUS</div>
        <div class="kpi-value" style="color: {ai_color}; font-size: 1.5rem; margin-top: 4px;">{ai_indicator}</div>
        <div style="font-size: 0.75rem; color: #64748b;">{"gemini-3.8-flash" if has_api else "Offline Triage"}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.write("")

# ---------------------------------------------------------
# TAB 1: REPORT NEW ISSUE
# ---------------------------------------------------------
if navigation == NAV_REPORT:
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.subheader("📝 Report Campus Maintenance Issue")
        st.caption("Complete the 3-step visual workflow below to submit an incident for AI visual triage and dispatch.")
    with head_col2:
        if st.button("🔄 Start New Report", use_container_width=True):
            st.session_state.active_ticket = None
            st.session_state.chat_history = []
            if "pending_chat_prompt" in st.session_state:
                del st.session_state.pending_chat_prompt
            if "created_ticket_id" in st.session_state:
                del st.session_state.created_ticket_id
            st.session_state.reporter_name_key = ""
            st.session_state.reporter_email_key = ""
            st.session_state.room_key = ""
            st.session_state.title_key = ""
            st.session_state.desc_key = ""
            if "file_key" in st.session_state:
                del st.session_state["file_key"]
            if "cam_key" in st.session_state:
                del st.session_state["cam_key"]
            st.rerun()

    # 3-Step Visual Workflow Layout (Desktop 2-Col / Mobile Single Column 01 -> 02 -> 03)
    st.markdown('<div class="report-workflow-grid">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown('<div class="step-box-1">', unsafe_allow_html=True)
        st.markdown("""
        <div class="step-card">
            <div class="step-header">
                <span class="step-num">01</span> Reporter Details & Location
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        reporter_name = st.text_input("Your Name", placeholder="e.g. Alex Rivera", key="reporter_name_key")
        reporter_email = st.text_input("Your Email Address", placeholder="e.g. arivera@campus.edu", key="reporter_email_key")
        building = st.selectbox(
            "Building Location",
            [
                "Science & Engineering Complex",
                "Student Union Center",
                "Central Library",
                "Oak Hall Dormitory",
                "Maple Hall Dormitory",
                "Humanities Hall",
                "Athletics & Recreation Center",
                "Arts & Design Building",
                "Campus Dining Hall"
            ]
        )
        room = st.text_input("Room Number / Specific Area", placeholder="e.g. Room 304, 2nd Floor Restroom", key="room_key")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="step-box-3">', unsafe_allow_html=True)
        st.markdown("""
        <div class="step-card" style="margin-top: 20px;">
            <div class="step-header">
                <span class="step-num">03</span> Describe Issue
            </div>
        </div>
        """, unsafe_allow_html=True)
        issue_title = st.text_input("Issue Title", placeholder="e.g. Broken water pipe leaking on floor", key="title_key")
        description = st.text_area("Detailed Description of Problem", placeholder="Describe what you observed, sound, smell, or safety concerns...", height=120, key="desc_key")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="step-box-2">', unsafe_allow_html=True)
        st.markdown("""
        <div class="step-card">
            <div class="step-header">
                <span class="step-num">02</span> Upload Evidence
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        img_source = st.radio("Image Input Mode", ["Upload Image File", "Use Camera"], horizontal=True)
        uploaded_img = None
        
        if img_source == "Upload Image File":
            uploaded_file = st.file_uploader("Choose an issue image...", type=["jpg", "jpeg", "png", "webp"], key="file_key")
            if uploaded_file:
                uploaded_img = Image.open(uploaded_file)
                st.image(uploaded_img, caption="Uploaded Image Preview", use_container_width=True)
        else:
            camera_file = st.camera_input("Take a photo of the maintenance issue", key="cam_key")
            if camera_file:
                uploaded_img = Image.open(camera_file)
                st.image(uploaded_img, caption="Captured Image Preview", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    submit_btn = st.button("✨ Analyze & Submit with AI", type="primary", use_container_width=True)
    
    if submit_btn:
        if not issue_title or not description or not room:
            st.error("⚠️ Please fill out the room number, issue title, and description before submitting.")
        else:
            with st.spinner("🔍 Gemini AI is analyzing image & text, scoring safety hazards, and assigning department..."):
                triage_res, is_offline, err_msg = analyze_issue_with_gemini(get_api_key(), f"{issue_title} - {description}", building, room, uploaded_img)
                
                if triage_res is not None:
                    new_id = f"CF-2026-{random.randint(1000, 9999)}"
                    new_ticket = {
                        "ticket_id": new_id,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "reporter": reporter_name if reporter_name else "Anonymous Campus Occupant",
                        "reporter_email": reporter_email if reporter_email else "not-provided@campus.edu",
                        "building": building,
                        "room": room,
                        "title": issue_title,
                        "description": description,
                        "category": triage_res.get("category", "Other Facilities Issue"),
                        "urgency": triage_res.get("urgency", "Medium Priority"),
                        "urgency_score": triage_res.get("urgency_score", 5),
                        "assigned_department": triage_res.get("assigned_department", "Facilities Operations"),
                        "status": "Pending",
                        "summary": triage_res.get("summary", "Issue reported."),
                        "safety_hazards": triage_res.get("safety_hazards", []),
                        "suggested_action_plan": triage_res.get("suggested_action_plan", []),
                        "required_tools": triage_res.get("required_tools_equipment", []),
                        "estimated_repair_time": triage_res.get("estimated_repair_time", "1-2 hours"),
                        "technician_notes": ""
                    }
                    
                    st.session_state.tickets.insert(0, new_ticket)
                    save_tickets(st.session_state.tickets)
                    st.session_state.active_ticket = new_ticket
                    st.session_state.chat_history = []
                    st.session_state.created_ticket_id = new_id
                else:
                    # Clear any stale session state on failure
                    st.session_state.active_ticket = None
                    st.session_state.chat_history = []
                    if "created_ticket_id" in st.session_state:
                        del st.session_state.created_ticket_id
                        
                    if err_msg and ("503" in err_msg or "unavailable" in err_msg.lower() or "high demand" in err_msg.lower()):
                        st.warning("⚠️ **Gemini AI is temporarily unavailable due to high server demand.** Please try clicking Analyze & Submit again in a moment.")
                    else:
                        st.error("❌ **Gemini AI Request Failed.** Please verify network/credentials and try again.")
                    
                    if err_msg:
                        st.caption(f"Technical Diagnostic: {err_msg}")

    # Render Triage Results & Interactive Chat if active ticket exists
    current_ticket = st.session_state.active_ticket
    if current_ticket:
        if "created_ticket_id" in st.session_state and st.session_state.created_ticket_id == current_ticket["ticket_id"]:
            st.success(f"🎉 Ticket Created! Ticket ID: **{st.session_state.created_ticket_id}**")
            
        st.divider()
        urg = current_ticket.get("urgency", "Medium Priority")
        badge_class = "badge-medium"
        badge_label = "MEDIUM"
        if "Emergency" in urg:
            badge_class = "badge-emergency"
            badge_label = "🔴 EMERGENCY"
        elif "High" in urg:
            badge_class = "badge-high"
            badge_label = "🔴 HIGH"
        elif "Low" in urg:
            badge_class = "badge-low"
            badge_label = "🟢 LOW"

        st.markdown(f"""
        <div class="triage-card-v2">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">
                <h3 style="margin: 0; color: #f8fafc; font-size: 1.4rem; display: flex; align-items: center; gap: 8px;">
                    🤖 AI Incident Triage
                </h3>
                <span style="font-family: monospace; background: #0f172a; border: 1px solid #38bdf8; color: #38bdf8; padding: 4px 12px; border-radius: 8px; font-weight: 700; font-size: 0.9rem;">
                    Ticket ID: {current_ticket['ticket_id']}
                </span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px;">
                <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 10px; border: 1px solid #334155; text-align: center;">
                    <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Priority</div>
                    <div style="margin-top: 6px;"><span class="{badge_class}">{badge_label}</span></div>
                </div>
                <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 10px; border: 1px solid #334155; text-align: center;">
                    <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Urgency Score</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #38bdf8; margin-top: 2px;">{current_ticket.get('urgency_score', 5)}/10</div>
                </div>
                <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 10px; border: 1px solid #334155; text-align: center;">
                    <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Category</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #f8fafc; margin-top: 4px;">{current_ticket.get('category')}</div>
                </div>
                <div style="background: rgba(15,23,42,0.6); padding: 12px; border-radius: 10px; border: 1px solid #334155; text-align: center;">
                    <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Est. Repair Time</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #38bdf8; margin-top: 4px;">{current_ticket.get('estimated_repair_time')}</div>
                </div>
            </div>
            <div style="margin-bottom: 16px;">
                <h4 style="color: #38bdf8; margin: 0 0 6px 0;">AI Executive Summary</h4>
                <p style="color: #e2e8f0; line-height: 1.5; margin: 0;">{current_ticket.get('summary')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            <div class="action-card">
                <h4 style="color: #fca5a5; margin-top: 0;">⚠️ Safety Hazards & Precautions</h4>
            </div>
            """, unsafe_allow_html=True)
            for h in current_ticket.get("safety_hazards", ["No immediate safety hazard detected."]):
                st.warning(f"• {h}")
        with col_b:
            st.markdown("""
            <div class="action-card">
                <h4 style="color: #38bdf8; margin-top: 0;">🛠️ Recommended Technician Action Plan</h4>
            </div>
            """, unsafe_allow_html=True)
            for act in current_ticket.get("suggested_action_plan", []):
                st.info(f"• {act}")

        st.caption("* Disclaimer: AI triage recommendations are generated to assist facilities operations and do not replace official emergency response procedures.")
                
        # -----------------------------------------------------
        # 📧 EMAIL DISPATCH SECTION
        # -----------------------------------------------------
        st.markdown("""
        <div class="action-card">
            <h4 style="color: #f8fafc; margin: 0 0 6px 0;">📧 Dispatch Official Maintenance Report</h4>
            <p style="color: #94a3b8; font-size: 0.9rem; margin: 0;">
                Send an official facilities dispatch report via Resend Email API directly to campus operations staff.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        email_btn_col1, email_btn_col2 = st.columns([1, 2])
        with email_btn_col1:
            if st.button("📧 Send Maintenance Report", type="primary", use_container_width=True):
                with st.spinner("Dispatching email via Resend API..."):
                    success, email_msg = send_maintenance_email(current_ticket)
                    if success:
                        st.success(f"✅ {email_msg}")
                    else:
                        st.error(f"❌ Email sending failed: {email_msg}")

        # -----------------------------------------------------
        # 💬 REAL GEMINI MULTI-TURN CHAT SECTION
        # -----------------------------------------------------
        st.markdown("""
        <div class="action-card">
            <h4 style="color: #38bdf8; margin: 0 0 4px 0;">💬 CampusFix AI Assistant</h4>
            <p style="color: #94a3b8; font-size: 0.9rem; margin: 0;">Ask questions about this incident. The AI retains full context of the defect details, triage diagnosis, and safety findings.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")

        # Preset suggestion chips
        st.write("**Quick Actions:**")
        q_col1, q_col2, q_col3, q_col4 = st.columns(4)
        with q_col1:
            if st.button("❓ Is this dangerous?", use_container_width=True):
                st.session_state.pending_chat_prompt = "Is this dangerous?"
        with q_col2:
            if st.button("🏷️ Why this category?", use_container_width=True):
                st.session_state.pending_chat_prompt = f"Why did you classify this as {current_ticket.get('category')}?"
        with q_col3:
            if st.button("📄 Formal Complaint", use_container_width=True):
                st.session_state.pending_chat_prompt = "Make the complaint more formal for campus management."
        with q_col4:
            if st.button("🔎 Missing Information?", use_container_width=True):
                st.session_state.pending_chat_prompt = "What information is missing from this incident report?"

        # Display conversation history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Process user chat input
        user_prompt = st.chat_input("Ask CampusFix AI follow-up questions about this maintenance issue...")
        if "pending_chat_prompt" in st.session_state and st.session_state.pending_chat_prompt:
            user_prompt = st.session_state.pending_chat_prompt
            del st.session_state.pending_chat_prompt

        if user_prompt:
            with st.chat_message("user"):
                st.markdown(user_prompt)
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})

            with st.chat_message("assistant"):
                with st.spinner("Gemini AI is analyzing your question..."):
                    ai_reply = run_gemini_chat(get_api_key(), current_ticket, user_prompt, st.session_state.chat_history[:-1])
                    st.markdown(ai_reply)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})

# ---------------------------------------------------------
# TAB 2: TICKET TRACKING
# ---------------------------------------------------------
elif navigation == NAV_TRACKING:
    st.subheader("📋 Ticket Tracking & Campus Search")
    st.caption("Filter, monitor, and dispatch campus maintenance tickets across all campus facilities.")
    
    search_col, filter_col = st.columns([2, 1])
    with search_col:
        search_query = st.text_input("🔍 Search by Ticket ID, Building, or Keywords", placeholder="e.g. CF-2026-1001 or Library")
    with filter_col:
        status_filter = st.selectbox("Filter Status", ["All Statuses", "Pending", "In Progress", "Resolved"])
        
    filtered_tickets = st.session_state.tickets
    if status_filter != "All Statuses":
        filtered_tickets = [t for t in filtered_tickets if t.get("status") == status_filter]
    if search_query:
        sq = search_query.lower()
        filtered_tickets = [
            t for t in filtered_tickets
            if sq in t["ticket_id"].lower() or sq in t["building"].lower() or sq in t["title"].lower() or sq in t["category"].lower()
        ]
        
    st.write(f"Displaying **{len(filtered_tickets)}** ticket(s):")
    
    for t in filtered_tickets:
        urg = t.get("urgency", "Medium Priority")
        urg_badge = "🔴 HIGH" if any(k in urg for k in ["Emergency", "High"]) else ("🟡 MEDIUM" if "Medium" in urg else "🟢 LOW")
        status_curr = t.get("status", "Pending")
        status_color = "badge-status-pending" if status_curr == "Pending" else ("badge-status-inprog" if status_curr == "In Progress" else "badge-status-resolved")
        
        with st.expander(f"[{t['ticket_id']}] {t['title']} — {t['building']} ({t['status']})"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Ticket ID:** `{t['ticket_id']}`")
                st.write(f"**Reporter:** {t.get('reporter')}")
                st.write(f"**Email:** {t.get('reporter_email', 'N/A')}")
                st.write(f"**Date:** {t.get('timestamp')}")
            with c2:
                st.write(f"**Location:** {t.get('building')} ({t.get('room')})")
                st.write(f"**Category:** {t.get('category')}")
                st.write(f"**Priority:** {urg_badge}")
                st.write(f"**Assigned Dept:** {t.get('assigned_department')}")
            with c3:
                st.write(f"**Status:** <span class='{status_color}'>{status_curr}</span>", unsafe_allow_html=True)
                st.write(f"**Est. Repair:** {t.get('estimated_repair_time')}")
                
            st.divider()
            st.write(f"**Description:** {t.get('description')}")
            st.write(f"**AI Executive Summary:** {t.get('summary')}")
            
            if t.get("suggested_action_plan"):
                st.write("**Suggested Action Steps:**")
                for step in t["suggested_action_plan"]:
                    st.write(f"- {step}")
            if t.get("technician_notes"):
                st.info(f"🛠️ **Technician Log Note:** {t['technician_notes']}")
                
            if st.button(f"📧 Dispatch Email Report for {t['ticket_id']}", key=f"email_{t['ticket_id']}"):
                with st.spinner("Dispatching email..."):
                    ok, res_msg = send_maintenance_email(t)
                    if ok:
                        st.success(f"✅ {res_msg}")
                    else:
                        st.error(f"❌ Email sending failed: {res_msg}")

# ---------------------------------------------------------
# TAB 3: TECHNICIAN WORKSTATION
# ---------------------------------------------------------
elif navigation == NAV_WORKSTATION:
    st.subheader("🛠️ Technician Workstation & Dispatch Operations")
    st.caption("Facilities maintenance operations console to update resolution status and consult AI technical diagnostics.")
    
    pending_count = sum(1 for t in st.session_state.tickets if t.get("status") == "Pending")
    in_prog_count = sum(1 for t in st.session_state.tickets if t.get("status") == "In Progress")
    resolved_count = sum(1 for t in st.session_state.tickets if t.get("status") == "Resolved")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.markdown(f'<div class="kpi-card"><div class="kpi-label">PENDING DISPATCH</div><div class="kpi-value" style="color:#f97316;">{pending_count}</div></div>', unsafe_allow_html=True)
    col_m2.markdown(f'<div class="kpi-card"><div class="kpi-label">IN PROGRESS</div><div class="kpi-value" style="color:#f59e0b;">{in_prog_count}</div></div>', unsafe_allow_html=True)
    col_m3.markdown(f'<div class="kpi-card"><div class="kpi-label">RESOLVED / CLOSED</div><div class="kpi-value" style="color:#22c55e;">{resolved_count}</div></div>', unsafe_allow_html=True)
    
    st.write("")
    
    ticket_ids = [f"{t['ticket_id']} - {t['title']} ({t['building']})" for t in st.session_state.tickets]
    selected_ticket_str = st.selectbox("Select Active Ticket to Manage", ticket_ids)
    
    if selected_ticket_str:
        sel_id = selected_ticket_str.split(" - ")[0]
        ticket = next((t for t in st.session_state.tickets if t["ticket_id"] == sel_id), None)
        
        if ticket:
            st.markdown(f"""
            <div class="triage-card-v2" style="margin-top: 10px;">
                <h3 style="margin:0; color:#f8fafc;">Workstation Console: Ticket {ticket['ticket_id']}</h3>
                <p style="color:#94a3b8; margin-top:4px;">Location: <strong>{ticket['building']} - {ticket['room']}</strong> | Category: <strong>{ticket['category']}</strong> | Est. Repair: <strong>{ticket.get('estimated_repair_time')}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            
            c_edit1, c_edit2 = st.columns([1, 1], gap="large")
            with c_edit1:
                st.markdown("#### 📝 Update Status & Technician Notes")
                new_status = st.selectbox("Status Update", ["Pending", "In Progress", "Resolved"], index=["Pending", "In Progress", "Resolved"].index(ticket.get("status", "Pending")))
                tech_note = st.text_area("Technician Log Notes", value=ticket.get("technician_notes", ""), placeholder="Enter parts used, work completed, or next steps...", height=120)
                
                if st.button("💾 Save Status & Notes", type="primary", use_container_width=True):
                    ticket["status"] = new_status
                    ticket["technician_notes"] = tech_note
                    save_tickets(st.session_state.tickets)
                    st.success("✅ Ticket record updated successfully!")
                    st.rerun()

            with c_edit2:
                st.markdown("#### 🤖 AI Technical Diagnostic Assistant")
                st.caption("Ask Gemini AI for step-by-step repair guidance or tool recommendations for this specific ticket.")
                tech_query = st.text_input("Ask Technical Question", placeholder="e.g., What is the safest way to isolate this breaker?")
                
                if st.button("💡 Ask AI Technical Advisor", use_container_width=True):
                    if not tech_query:
                        st.warning("Please type a question for the technician assistant.")
                    else:
                        with st.spinner("Consulting AI Technical Knowledge Base..."):
                            api_key = get_api_key()
                            if api_key:
                                try:
                                    prompt = prompts.TECHNICIAN_ASSISTANT_PROMPT.format(
                                        category=ticket["category"],
                                        title=ticket["title"],
                                        location=f"{ticket['building']} {ticket['room']}",
                                        summary=ticket["summary"],
                                        query=tech_query
                                    )
                                    from google import genai
                                    client = genai.Client(api_key=api_key)
                                    res = client.models.generate_content(model="gemini-3.8-flash", contents=[prompt])
                                    st.markdown(res.text)
                                except Exception as e:
                                    st.error(f"Error querying Gemini [{sanitize_gemini_error(e, api_key)}]")
                            else:
                                st.info(f"💡 **Offline Tech Advisory:** For {ticket['category']} at {ticket['building']}, verify main power/water isolation, consult standard maintenance SOP #402, and wear mandatory PPE before proceeding.")

# ---------------------------------------------------------
# TAB 4: ANALYTICS & AI INSIGHTS
# ---------------------------------------------------------
elif navigation == NAV_ANALYTICS:
    st.subheader("📊 Analytics & AI Insights Dashboard")
    st.caption("Operational analytics, priority distribution, and strategic AI maintenance health insights.")
    
    df = pd.DataFrame(st.session_state.tickets)
    
    if not df.empty:
        col_g1, col_g2 = st.columns(2, gap="large")
        
        with col_g1:
            st.markdown("""
            <div class="action-card">
                <h4 style="margin: 0 0 10px 0; color: #f8fafc;">Operational Overview: Issues by Category</h4>
            </div>
            """, unsafe_allow_html=True)
            fig_cat = px.pie(df, names="category", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_cat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc", margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_cat, use_container_width=True)
            
        with col_g2:
            st.markdown("""
            <div class="action-card">
                <h4 style="margin: 0 0 10px 0; color: #f8fafc;">Incident Volume by Campus Building</h4>
            </div>
            """, unsafe_allow_html=True)
            building_counts = df["building"].value_counts().reset_index()
            building_counts.columns = ["building", "count"]
            fig_bldg = px.bar(building_counts, x="count", y="building", orientation='h', color="count", color_continuous_scale="Viridis")
            fig_bldg.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc", yaxis={'categoryorder':'total ascending'}, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_bldg, use_container_width=True)

        st.write("")
        st.markdown("""
        <div class="action-card">
            <h4 style="color: #38bdf8; margin: 0 0 6px 0;">🧠 AI Infrastructure Insights</h4>
            <p style="color: #94a3b8; font-size: 0.9rem; margin: 0;">Generate an executive strategic summary of campus incident trends using Gemini AI.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        if st.button("✨ Generate AI Infrastructure Health Insights", type="primary", use_container_width=True):
            with st.spinner("Analyzing historical ticket patterns with Gemini AI..."):
                report_md = generate_ai_insights(get_api_key(), df)
                st.markdown(report_md)

# ---------------------------------------------------------
# TAB 5: SELF-HELP KNOWLEDGE BASE
# ---------------------------------------------------------
elif navigation == NAV_KNOWLEDGE:
    st.subheader("💡 Self-Help Knowledge Base")
    st.caption("Searchable facilities self-help cards and standard campus troubleshooting protocols.")
    
    st.write("")
    
    kb_col1, kb_col2 = st.columns(2, gap="large")
    
    with kb_col1:
        with st.expander("🔌 Electrical & Lighting Safety Protocols"):
            st.write("""
            • **Tripped Breaker**: Check if outlets in lab or dorm room tripped. Reset wall GFCI outlet buttons before filing report.
            • **Exposed Wiring**: Do NOT touch bare wires under any circumstances. Clear immediate area and report via high priority triage.
            • **Flickering Overhead Fixture**: Fixtures on emergency circuits may flicker during generator self-tests on Monday mornings.
            """)

        with st.expander("💧 Plumbing & Water Leak Response"):
            st.write("""
            • **Active Flooding**: Locate wall shutoff valve under sink or behind toilet and turn clockwise to stop main flow.
            • **Clogged Drain**: Avoid hazardous chemical drain cleaners in campus dorms; report to plumbing team for mechanical snake clearing.
            """)

        with st.expander("🌐 Network & Campus Connectivity"):
            st.write("""
            • **Wi-Fi Re-authentication**: Forget 'eduroam' network in Wi-Fi settings and re-login with full campus email.
            • **Ethernet Wall Jack**: Verify CAT6 cable clip is securely seated until audible click is heard.
            """)

        with st.expander("🪑 Furniture & Fixture Care"):
            st.write("""
            • **Desk/Chair Adjustment**: Use under-seat tension knob to adjust hydraulic desk chair height safely.
            • **Loose Bolts**: File routine carpenter ticket for wobbling bedframes or study desks.
            """)

    with kb_col2:
        with st.expander("🧹 Cleaning & Sanitation Services"):
            st.write("""
            • **Spill Cleanup**: Custodial services provide immediate response for biohazard or large liquids in public walkways.
            • **Trash Overflow**: Main waste receptacles in hallways are cleared twice daily at 08:00 and 16:00.
            """)

        with st.expander("🏗️ Infrastructure & Facilities Support"):
            st.write("""
            • **Elevator Maintenance**: For unresponsive elevator doors, push alarm button to alert campus security immediately.
            • **Door Lock & Access**: Keycard reader red light indicates low internal battery. Contact Housing Office Ext 4400.
            """)

        with st.expander("🛡️ Campus Safety & Emergency Numbers"):
            st.write("""
            • **Campus Police Dispatch**: Ext 911 / (555) 019-2831
            • **Facilities Operations Hotline**: Ext 4400
            • **Environmental Health & Safety (EHS)**: Ext 4420
            """)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.82rem; padding: 10px 0;">
    <strong>CampusFix Platform</strong> • "See it. Report it. Fix it." • Powered by Streamlit & Google Gemini AI
</div>
""", unsafe_allow_html=True)
