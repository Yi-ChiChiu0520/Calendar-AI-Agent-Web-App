# 📅 Calendar AI Agent Web App

An AI-powered scheduling assistant that extracts events from natural language, validates participant credentials, integrates with Google Calendar, and sends email/text notifications. Built with a React frontend and Python backend using FastAPI and OpenAI API.

---

## 🧠 Features

- 🔐 **Police Login & Badge Validation** – Secure account creation and login system.
- 📝 **Natural Language Event Parsing** – Converts plain text descriptions into structured calendar events using GPT.
- 📧 **Notification System** – Sends SMS and email alerts to participants.
- 📆 **Google Calendar Integration** – Automatically schedules valid events to Google Calendar.
- 🧪 **Form & Input Validation** – Checks badge numbers, article codes, license plates, and more.
- 🔁 **Return to Menu Option** – Enables multiple entries in one session.

---

## 🧰 Tech Stack

| Layer      | Technology               |
|------------|---------------------------|
| Frontend   | React, JavaScript, HTML, CSS |
| Backend    | FastAPI, Python, OpenAI SDK |
| Auth       | OAuth (Google), Badge Validation API |
| Notification | SMTP (Email), Twilio (SMS) |
| Storage    | Google Calendar API       |

---

## 🚀 Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/Yi-ChiChiu0520/Calendar-AI-Agent-Web-App.git
cd Calendar-AI-Agent-Web-App
```
### 2. Environment Setup
#### 🖥️ Backend (/backend)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
#### ✏️  Create a .env file with (see .env.example):
```bash
OPENAI_API_KEY=your_api_key
SENDER_EMAIL=your_email
SENDER_PASSWORD=your_password
GOOGLE_CLIENT_SECRET=your_credentials.json
```

#### ▶️ Run the Backend Server (Uvicorn)
If running from the project root, set the Python path:
```bash
export PYTHONPATH=$(pwd)
uvicorn backend.main:app --reload --port 8000
```
Or, if running from within the backend/ directory, use:
```bash
cd backend
uvicorn main:app --reload --port 8000
```
#### 🌐 Frontend (/frontend)
```bash
cd ../frontend
npm install
npm start
```
