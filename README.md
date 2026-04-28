# 🩺 Aushadh AI — Your Personal Health Companion

> *"Aushadh" (औषध) means medicine in Hindi/Sanskrit.*

Aushadh AI is an intelligent healthcare web application that helps patients understand their doctor's prescriptions and medical documents. Upload a photo of your prescription — the AI reads it, breaks down the medical jargon, builds your medication schedule, and lets you chat with an AI doctor about your diagnosis.



---

## ✨ Features

- **📸 Smart Prescription Reading** — Upload a photo or PDF of any prescription and get an instant structured analysis
- **🧠 AI-Powered Analysis** — Groq's Llama 3.3 70B converts complex medical jargon into simple language
- **🖼️ Medical Image Analysis** — Google Gemini 1.5 Flash analyzes X-rays, MRIs, and scanned documents
- **💊 Medication Schedules** — Auto-generates clear timing schedules for all prescribed medicines
- **🏥 Hospital Visit Checklist** — Never miss a follow-up with auto-generated task lists
- **💬 AI Health Chat** — Ask follow-up questions about your diagnosis and treatment in plain language
- **📤 Export Summary** — Download your analysis as a text file
- **🔐 Secure Authentication** — MongoDB-backed user registration and session management
- **🌐 Multi-language Support** — English and Hindi supported

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI 0.111.0 (Python) |
| **Server** | Uvicorn (ASGI) |
| **Database** | MongoDB (via PyMongo) |
| **Primary AI** | Groq — Llama 3.3 70B |
| **Vision AI** | Google Gemini 1.5 Flash |
| **OCR** | EasyOCR + Google Cloud Vision |
| **PDF Parsing** | pdfplumber |
| **Frontend** | HTML5, TailwindCSS, Vanilla JavaScript |

---

## 📁 Project Structure

```
Aushadh AI/
├── main.py                   # FastAPI app — routes, middleware, static file serving
├── run.py                    # Local dev entry point (opens browser automatically)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this yourself)
│
├── app/
│   ├── routers/
│   │   ├── analyse.py        # POST /api/analyse/file — prescription image/PDF analysis
│   │   ├── chat.py           # POST /api/chat — AI health chat
│   │   ├── export.py         # POST /api/export/txt — export analysis as text
│   │   ├── auth.py           # POST /api/auth/register, /login, /logout, /me
│   │   └── profile.py        # GET/POST /api/auth/medications — medication management
│   │
│   └── services/
│       ├── mongo_service.py  # All MongoDB read/write operations
│       ├── ocr_service.py    # Text extraction from images (EasyOCR + Cloud Vision)
│       └── claude_service.py # AI orchestration — Groq + Gemini API calls
│
├── easyocr_models/           # Pre-downloaded EasyOCR model weights
├── logos/                    # App logo assets
│
└── Frontend (served directly by FastAPI)
    ├── index.html            # Landing page
    ├── login.html            # Sign In / Sign Up
    ├── dashboard.html        # Main dashboard
    ├── documents.html        # Upload & analyse prescriptions
    ├── diagnosis.html        # View AI analysis results
    ├── medications.html      # View medication schedule
    ├── checklist.html        # Follow-up task checklist
    ├── chat.html             # AI health chat interface
    ├── profile.html          # User profile page
    └── medbuddy.js           # Shared JS utilities (auth, API calls, UI helpers)
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server health check + API key status |
| `GET` | `/` | Landing page (`index.html`) |
| `GET` | `/docs` | Interactive Swagger API documentation |
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login and create session |
| `POST` | `/api/auth/logout` | Logout and clear session |
| `GET` | `/api/auth/me` | Get current logged-in user |
| `POST` | `/api/auth/medications` | Save user's medications |
| `GET` | `/api/auth/medications` | Fetch user's saved medications |
| `POST` | `/api/analyse/file` | Analyse prescription image or PDF |
| `POST` | `/api/analyse/text` | Analyse pasted prescription text |
| `POST` | `/api/analyse/sample` | Load a demo prescription |
| `POST` | `/api/chat` | Chat with AI about health query |
| `POST` | `/api/export/txt` | Export prescription summary as `.txt` |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- MongoDB (local or Atlas)
- Groq API key (required)
- Google Gemini API key (optional — for image/X-ray analysis)

### 1. Clone the repo

```bash
git clone https://github.com/rudra129r-lgtm/Aushadh-AI.git
cd "Aushadh AI"
```

### 2. Create `.env` file

```env
# Required — Get free key at https://console.groq.com
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx

# Optional — For X-ray/MRI image analysis
# Get at https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_google_gemini_key

# Required — MongoDB connection string
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/aushadh_ai

# Optional — defaults to aushadh_ai
MONGODB_DB=aushadh_ai
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run locally

```bash
python run.py
```

App opens automatically at **http://localhost:8000** — API docs at **http://localhost:8000/docs**

---

---

## 🔐 Getting API Keys

### Groq API Key (Required)
1. Go to [console.groq.com](https://console.groq.com)
2. Create a free account
3. Generate an API key
4. Add to `.env`: `GROQ_API_KEY=gsk_...`

### Google Gemini (Optional — for image analysis)
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create an API key
3. Add to `.env`: `GEMINI_API_KEY=your_key`

### MongoDB Atlas (Required)
1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free M0 cluster
3. Whitelist `0.0.0.0/0` under Network Access
4. Get connection string → add to `.env`: `MONGODB_URI=mongodb+srv://...`

---

## 🖥️ User Flow

```
index.html (Landing Page)
        │
        ▼
login.html (Sign In / Sign Up)
        │
        ▼
dashboard.html (Main Hub)
        │
        ├──▶ documents.html (Upload Prescription)
        │           │
        │           ▼
        │    diagnosis.html (AI Analysis Results)
        │
        ├──▶ medications.html (Medication Schedule)
        │
        ├──▶ checklist.html (Follow-up Tasks)
        │
        ├──▶ chat.html (Ask AI Health Questions)
        │
        └──▶ profile.html (User Profile)
```

---

## 🐛 Troubleshooting

**Server won't start**
```bash
# Check if port 8000 is already in use
netstat -ano | findstr :8000
# Kill the process
taskkill /PID <process_id> /F
```

**MongoDB connection error**
- Verify `MONGODB_URI` in your `.env` is correct
- Ensure your IP is whitelisted in MongoDB Atlas under Network Access → `0.0.0.0/0`

**Groq API errors**
- Check your `GROQ_API_KEY` is valid at [console.groq.com](https://console.groq.com)
- Free tier has rate limits — wait a moment and retry

**OCR not extracting text from image**
- Ensure the image is clear, well-lit, and readable
- Check that `easyocr_models/` folder contains the model files
- Try with a higher resolution image

**Login not working**
- Open browser console (F12) and check for errors
- Verify MongoDB is running and `MONGODB_URI` is correct

---

## 📄 License

This project is for **educational purposes only**. Always consult a qualified physician for medical advice. Do not use AI analysis as a substitute for professional healthcare.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open a Pull Request or Issue.

---

*Built with ❤️ by **Pairfect** — for better healthcare understanding in India and beyond*
