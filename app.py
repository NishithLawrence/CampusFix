"""
CampusFix-AI: Intelligent Campus Maintenance & Triage System
Main Streamlit Application File with Gemini Vision + Multi-Turn Chat + Resend Email API Dispatch
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
# Page Configuration & Custom CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="CampusFix-AI | Infrastructure & Maintenance Triage",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Modern Dark UI CSS Styling
st.markdown("""
<style>
    /* Main Theme Overrides */
    .stApp {
        background-color: #0e1117;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #1e2640 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .header-title {
        color: #f8fafc;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 6px;
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
    }

    /* Urgency Badges */
    .badge-emergency {
        background-color: #7f1d1d;
        color: #fca5a5;
        border: 1px solid #ef4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-high {
        background-color: #7c2d12;
        color: #fdba74;
        border: 1px solid #f97316;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-medium {
        background-color: #713f12;
        color: #fde047;
        border: 1px solid #eab308;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-low {
        background-color: #14532d;
        color: #86efac;
        border: 1px solid #22c55e;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    
    /* Analysis Result Card */
    .triage-card {
        background-color: #0f172a;
        border: 1px solid #38bdf8;
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
    }
    
    .demo-tag {
        background-color: #b45309;
        color: #fef08a;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
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
        
        body = f"""CampusFix-AI Official Facilities Maintenance Incident Report
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
        body += "Automated Facilities Dispatch generated by CampusFix-AI System via Resend."

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
# Sidebar Navigation & Settings
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/school.png", width=70)
    st.title("CampusFix-AI")
    st.caption("Smart Campus Operations Triage")
    
    st.divider()
    
    navigation = st.radio(
        "Navigation Menu",
        [
            "📝 Report New Issue",
            "📋 Ticket Tracking & Search",
            "🛠️ Technician Workstation",
            "📊 Analytics & AI Insights",
            "💡 Self-Help Knowledge Base"
        ]
    )
    
    st.divider()
    
    # API & Secret Status Panel
    api_key_val = get_api_key()
    with st.expander("🔑 Service Credentials Status", expanded=not bool(api_key_val)):
        if api_key_val:
            st.success("✅ Gemini API Key Connected")
        else:
            st.warning("⚠️ No Gemini API Key set. (Running in DEMO / OFFLINE MODE)")
            
        user_key_input = st.text_input("Enter Gemini API Key:", type="password", key="key_input_box")
        if user_key_input:
            st.session_state.user_api_key = user_key_input
            st.rerun()

        st.divider()
        st.caption("📧 Resend Email API Status:")
        resend_key = st.secrets.get("RESEND_API_KEY")
        maint_email = st.secrets.get("MAINTENANCE_EMAIL")
        if resend_key and resend_key not in ["your_resend_api_key", "your-resend-api-key"]:
            st.success("✅ Resend API Key Connected")
            st.caption(f"Default Recipient: {maint_email}")
        else:
            st.info("ℹ️ Resend API Key not set in .streamlit/secrets.toml")

# ---------------------------------------------------------
# Header Banner
# ---------------------------------------------------------
st.markdown("""
<div class="header-banner">
    <div class="header-title">
        <span>🏫</span> CampusFix-AI Triage System
    </div>
    <div class="header-subtitle">
        AI-Powered Multimodal Incident Triage, Interactive Gemini Chat & Automated Facilities Dispatch
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 1: REPORT NEW ISSUE
# ---------------------------------------------------------
if navigation == "📝 Report New Issue":
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.subheader("📝 Report Campus Maintenance or Safety Issue")
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

    st.write("Upload a photo or enter details of the physical defect. CampusFix-AI will analyze safety hazards, triage the incident, launch an interactive follow-up chat, and dispatch an official email report.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
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
        issue_title = st.text_input("Issue Title", placeholder="e.g. Broken water pipe leaking on floor", key="title_key")
        description = st.text_area("Detailed Description of Problem", placeholder="Describe what you observed, sound, smell, or safety concerns...", height=120, key="desc_key")
        
    with col2:
        st.write("📷 **Upload or Capture Image (Optional)**")
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

    submit_btn = st.button("🚀 Analyze & Submit with AI Triage", type="primary", use_container_width=True)
    
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
    if current_ticket:
        st.divider()
        urg = current_ticket.get("urgency", "Medium Priority")
        badge_class = "badge-medium"
        if "Emergency" in urg:
            badge_class = "badge-emergency"
        elif "High" in urg:
            badge_class = "badge-high"
        elif "Low" in urg:
            badge_class = "badge-low"

        st.markdown(f"""
        <div class="triage-card">
            <h3>🤖 Gemini AI Incident Triage Result [{current_ticket['ticket_id']}]</h3>
            <div style="display: flex; gap: 15px; align-items: center; margin-bottom: 15px; flex-wrap: wrap;">
                <span class="{badge_class}">{urg}</span>
                <span style="color: #94a3b8;">Urgency Score: <strong>{current_ticket.get('urgency_score', 5)}/10</strong></span>
                <span style="color: #38bdf8;">Assigned: <strong>{current_ticket.get('assigned_department')}</strong></span>
            </div>
            <p><strong>Executive Summary:</strong> {current_ticket.get('summary')}</p>
            <p><strong>Estimated Repair Time:</strong> {current_ticket.get('estimated_repair_time')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("⚠️ **Safety Hazards & Precautions:**")
            for h in current_ticket.get("safety_hazards", ["None reported."]):
                st.info(f"• {h}")
        with col_b:
            st.write("🛠️ **Recommended Technician Action Plan:**")
            for act in current_ticket.get("suggested_action_plan", []):
                st.write(f"• {act}")
                
        # -----------------------------------------------------
        # 📧 EMAIL DISPATCH SECTION
        # -----------------------------------------------------
        st.divider()
        st.subheader("📧 Dispatch Official Maintenance Email")
        st.write("Click below to send an official maintenance dispatch report via Resend Email API to campus facilities staff.")
        
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
        st.divider()
        st.subheader("💬 Interactive Gemini AI Follow-up Chat")
        st.write("Ask follow-up questions about this incident. The AI retains full context of the uploaded image, triage diagnosis, and safety findings.")

        # Preset suggestion chips
        st.write("**Quick Example Prompts:**")
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
            if st.button("🔍 Missing Info?", use_container_width=True):
                st.session_state.pending_chat_prompt = "What information is missing from this incident report?"

        # Display conversation history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Process user chat input
        user_prompt = st.chat_input("Ask Gemini follow-up questions about this maintenance issue...")
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
# TAB 2: TICKET TRACKING & SEARCH
# ---------------------------------------------------------
elif navigation == "📋 Ticket Tracking & Search":
    st.subheader("📋 Campus Ticket Search & Lifecycle Tracker")
    
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
        
    st.write(f"Showing **{len(filtered_tickets)}** ticket(s):")
    
    for t in filtered_tickets:
        urg = t.get("urgency", "Medium Priority")
        urg_color = "🔴" if "Emergency" in urg else ("🟠" if "High" in urg else ("🟡" if "Medium" in urg else "🟢"))
        
        with st.expander(f"{urg_color} [{t['ticket_id']}] {t['title']} — {t['building']} ({t['status']})"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Reporter:** {t.get('reporter')}")
                st.write(f"**Email:** {t.get('reporter_email', 'N/A')}")
                st.write(f"**Date/Time:** {t.get('timestamp')}")
                st.write(f"**Building/Room:** {t.get('building')} - {t.get('room')}")
            with c2:
                st.write(f"**Category:** {t.get('category')}")
                st.write(f"**Urgency:** {t.get('urgency')} (Score: {t.get('urgency_score')}/10)")
                st.write(f"**Assigned Department:** {t.get('assigned_department')}")
            with c3:
                st.write(f"**Status:** {t.get('status')}")
                st.write(f"**Est. Repair Time:** {t.get('estimated_repair_time')}")
                
            st.divider()
            st.write(f"**Description:** {t.get('description')}")
            st.write(f"**AI Executive Summary:** {t.get('summary')}")
            
            if t.get("suggested_action_plan"):
                st.write("**Suggested Action Steps:**")
                for step in t["suggested_action_plan"]:
                    st.write(f"- {step}")
            if t.get("technician_notes"):
                st.info(f"🛠️ **Technician Log Note:** {t['technician_notes']}")
                
            if st.button(f"📧 Send Email Report for {t['ticket_id']}", key=f"email_{t['ticket_id']}"):
                with st.spinner("Dispatching email..."):
                    ok, res_msg = send_maintenance_email(t)
                    if ok:
                        st.success(f"✅ {res_msg}")
                    else:
                        st.error(f"❌ Email sending failed: {res_msg}")

# ---------------------------------------------------------
# TAB 3: TECHNICIAN WORKSTATION
# ---------------------------------------------------------
elif navigation == "🛠️ Technician Workstation":
    st.subheader("🛠️ Facilities Maintenance Dispatch & Task Control")
    st.write("Manage active tickets, update resolution status, and request real-time Gemini AI diagnostic guidance.")
    
    pending_count = sum(1 for t in st.session_state.tickets if t.get("status") == "Pending")
    in_prog_count = sum(1 for t in st.session_state.tickets if t.get("status") == "In Progress")
    resolved_count = sum(1 for t in st.session_state.tickets if t.get("status") == "Resolved")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#f97316;">{pending_count}</div><div class="metric-label">Pending Dispatch</div></div>', unsafe_allow_html=True)
    col_m2.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#eab308;">{in_prog_count}</div><div class="metric-label">In Progress</div></div>', unsafe_allow_html=True)
    col_m3.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#22c55e;">{resolved_count}</div><div class="metric-label">Completed / Resolved</div></div>', unsafe_allow_html=True)
    
    st.divider()
    
    ticket_ids = [f"{t['ticket_id']} - {t['title']} ({t['building']})" for t in st.session_state.tickets]
    selected_ticket_str = st.selectbox("Select Ticket to Manage", ticket_ids)
    
    if selected_ticket_str:
        sel_id = selected_ticket_str.split(" - ")[0]
        ticket = next((t for t in st.session_state.tickets if t["ticket_id"] == sel_id), None)
        
        if ticket:
            st.markdown(f"### Ticket Details: **{ticket['ticket_id']}**")
            
            c_edit1, c_edit2 = st.columns([1, 1])
            with c_edit1:
                new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Resolved"], index=["Pending", "In Progress", "Resolved"].index(ticket.get("status", "Pending")))
                tech_note = st.text_area("Technician Log Notes", value=ticket.get("technician_notes", ""), placeholder="Enter parts used, work completed, or next steps...")
                
                if st.button("💾 Save Status & Notes", type="primary"):
                    ticket["status"] = new_status
                    ticket["technician_notes"] = tech_note
                    save_tickets(st.session_state.tickets)
                    st.success("✅ Ticket record updated successfully!")
                    st.rerun()

            with c_edit2:
                st.write("🤖 **AI Technical Diagnostic Assistant**")
                st.caption("Ask Gemini AI for step-by-step repair guidance or tool recommendations for this specific ticket.")
                tech_query = st.text_input("Ask Technical Question", placeholder="e.g., What is the safest way to isolate this breaker?")
                
                if st.button("💡 Ask AI Technical Advisor"):
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
elif navigation == "📊 Analytics & AI Insights":
    st.subheader("📊 Campus Infrastructure Analytics & Operations Insights")
    
    df = pd.DataFrame(st.session_state.tickets)
    
    if not df.empty:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.write("📈 **Issues by Department Category**")
            fig_cat = px.pie(df, names="category", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_cat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
            st.plotly_chart(fig_cat, use_container_width=True)
            
        with col_g2:
            st.write("🏢 **Incident Volume by Campus Building**")
            building_counts = df["building"].value_counts().reset_index()
            building_counts.columns = ["building", "count"]
            fig_bldg = px.bar(building_counts, x="count", y="building", orientation='h', color="count", color_continuous_scale="Viridis")
            fig_bldg.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bldg, use_container_width=True)

        st.divider()
        
        st.subheader("🧠 Executive AI Strategic Maintenance Report")
        if st.button("✨ Generate AI Infrastructure Health Insights", type="primary"):
            with st.spinner("Analyzing historical ticket patterns with Gemini AI..."):
                report_md = generate_ai_insights(get_api_key(), df)
                st.markdown(report_md)

# ---------------------------------------------------------
# TAB 5: SELF-HELP KNOWLEDGE BASE
# ---------------------------------------------------------
elif navigation == "💡 Self-Help Knowledge Base":
    st.subheader("💡 Campus Self-Help & Non-Emergency FAQ")
    st.write("Check these standard protocols before submitting a formal maintenance request.")
    
    with st.expander("📶 Campus Wi-Fi Connection Troubleshooting"):
        st.write("""
        1. **Forget Network**: Go to Wi-Fi settings on your device and select 'Forget eduroam' or 'Campus-Guest'.
        2. **Re-authenticate**: Re-enter your campus netID username (username@campus.edu) and current password.
        3. **MAC Address Privacy**: On iOS/Android, turn off 'Private Wi-Fi Address' for campus network authentication.
        """)
        
    with st.expander("🔑 Electronic Dorm Keycard Lock Unresponsive"):
        st.write("""
        1. **Check Battery LED**: Swiping keycard: Red flash = Low battery lock; No light = Dead battery lock.
        2. **Temporary Entry**: Contact your Resident Advisor (RA) on duty or Housing Office (Ext 4400) for a physical master key lockout.
        """)
        
    with st.expander("🌡️ Dorm Room Thermostat Controls"):
        st.write("""
        • Central campus HVAC maintains temperatures between 68°F and 74°F.
        • Ensure windows and exterior doors are fully sealed; open windows disable individual room fan coils automatically.
        """)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.divider()
st.caption("CampusFix-AI Platform • Powered by Streamlit & Google Gemini AI • Campus Operations & Facilities Management")
