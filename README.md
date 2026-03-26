# 🩺 MedBuddy — Complete Application

## Folder Structure
```
medbuddy/
├── run.py              ← START HERE - runs everything
├── main.py             ← FastAPI application
├── requirements.txt    ← Python dependencies
├── .env                ← Your API key (create this yourself)
├── app/
│   ├── routers/
│   │   ├── analyse.py  ← Upload & analyse endpoints
│   │   ├── chat.py     ← Chat endpoint
│   │   └── export.py   ← Export endpoint
│   └── services/
│       └── claude_service.py ← AI logic
├── index.html          ← Welcome/Landing page
├── login.html          ← Login & Signup
├── dashboard.html      ← Main dashboard
├── documents.html      ← Upload & processing
├── diagnosis.html      ← Health summary
├── medications.html    ← Medication schedule
├── checklist.html      ← Follow-up & alerts
├── profile.html        ← User profile
└── medbuddy.js         ← Shared JS utilities
```

## Setup (One Time)

### Step 1 — Create .env file
Create a file named `.env` in the medbuddy folder:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### Step 2 — Install packages
```bash
pip install -r requirements.txt
```

### Step 3 — Run
```bash
python run.py
```

Browser opens automatically at http://localhost:8000 🚀

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/analyse/file | Upload PDF/image |
| POST | /api/analyse/text | Paste text |
| POST | /api/analyse/sample | Demo prescription |
| POST | /api/chat | Chat about prescription |
| POST | /api/export/txt | Download summary |
| GET  | /health | Check server status |
| GET  | /docs | Swagger API docs |

## User Flow
```
index.html → login.html → dashboard.html → documents.html
                                        → diagnosis.html
                                        → medications.html
                                        → checklist.html
                                        → profile.html
```
