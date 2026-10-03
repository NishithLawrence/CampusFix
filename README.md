# 🏫 CampusFix-AI: Intelligent Campus Maintenance & Triage System

**CampusFix-AI** is an AI-powered, multimodal campus infrastructure issue reporting, diagnostic triage, interactive AI chat, and facilities dispatch platform built with Streamlit and Google Gemini AI. It streamlines campus facilities management by analyzing user-reported issues (text & images), assessing hazard levels, maintaining interactive follow-up chats, and dispatching official email reports via the Resend Email API.

---

## ✨ Key Features

- 📸 **Multimodal Gemini Vision Triage**: Upload photos or capture camera input of physical defects; Gemini AI auto-triages incidents in real time.
- 💬 **Interactive Gemini Multi-Turn Chat**: Real-time follow-up conversational assistant (`st.chat_message`, `st.chat_input`) retaining full incident context (image, description, location, category, urgency, safety findings).
- 📧 **Resend Email API Dispatch**: Sends official facilities dispatch reports via the Resend Email API using credentials from `.streamlit/secrets.toml`.
- 🚨 **Automated Hazard & Urgency Assessment**: Real-time hazard scoring (1-10) and safety alert warnings for emergencies (exposed wiring, active leaks, gas, structural risks).
- 🏷️ **Smart Categorization & Department Dispatch**: Auto-routes incidents to Campus Electrical, Central HVAC, IT Field Support, Janitorial, Plumbing, etc.
- 📋 **Technician & Admin Workstation**: Kanban task management with status tracking, technician notes logging, and AI technical repair advice.
- 📊 **Executive Analytics & AI Insights**: Plotly charts tracking maintenance trends by building and department, plus AI-generated preventive maintenance reports.
- 💾 **Local Persistence**: Saves tickets to `tickets.json` for continuous tracking across sessions.

---

## 📁 Project Structure

```text
CampusFix-AI/
├── app.py                      # Streamlit application with Vision analysis, Chat, and Resend dispatch
├── prompts.py                  # AI prompt templates & JSON response schemas for Gemini
├── requirements.txt            # Python dependencies (Streamlit, google-genai, resend, Plotly, Pillow, Pandas)
├── README.md                   # Complete documentation & quickstart guide
├── .gitignore                  # Git ignore rules for secrets and temporary files
└── .streamlit/
    └── secrets.toml.example    # Streamlit secrets configuration template
```

---

## 🚀 Quickstart Guide

### 1. Installation

```bash
# Create virtual environment (optional)
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Resend & Gemini Secrets Configuration

1. Create a free account at [Resend.com](https://resend.com) and generate an API key in the Resend dashboard.
2. Copy the example secrets file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
3. Edit `.streamlit/secrets.toml` to configure your Gemini API Key and Resend credentials:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
RESEND_API_KEY = "re_your_resend_api_key_here"
MAINTENANCE_EMAIL = "your-email@example.com"
```

> ℹ️ **Note on Resend Sender Addresses & Testing:**  
> • No Gmail password or SMTP configuration is required!  
> • By default, emails are dispatched from `onboarding@resend.dev` (Resend's default test sender domain).  
> • On free Resend accounts, test emails can be sent to the email address registered with your Resend account. To deliver to external custom domains, verify a custom domain in your Resend Dashboard.

---

## 🏃 Running the Application

Launch the Streamlit app:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🛠️ Complete Operational Workflow

1. **Student / Staff Report**: Upload a photo, select location, enter issue description, and click **Analyze & Submit with AI Triage**.
2. **Gemini Vision Analysis**: Gemini evaluates visual and text evidence, generates hazard score, category, and action plan.
3. **Interactive Follow-up Chat**: Use the integrated Gemini Chat interface to ask follow-up questions (*"Is this dangerous?"*, *"Why did you classify this as electrical?"*, *"Make the complaint more formal"*).
4. **Email Dispatch**: Click **📧 Send Maintenance Report** to dispatch an official facilities report via Resend API to `MAINTENANCE_EMAIL`.
5. **Technician & Analytics Tracking**: Campus technicians update ticket statuses in the Workstation while management tracks campus health in Analytics.
