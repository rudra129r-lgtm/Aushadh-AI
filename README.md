# 🩺 Aushadh AI - Your Personal Health Companion

Aushadh AI is an intelligent healthcare application that helps you understand doctor's prescriptions and medical documents effortlessly. Simply snap a photo of your prescription and AI will break down the medical jargon into simple, understandable language.

![Aushadh AI](https://img.shields.io/badge/Version-2.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.13+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-cyan)

## ✨ Features

- **📸 Smart Prescription Reading** - Upload photos of prescriptions and get instant analysis
- **🧠 AI-Powered Analysis** - Converts complex medical jargon into simple language
- **💊 Medication Reminders** - Get clear schedules for all your medications
- **🏥 Hospital Visit Checklist** - Never miss a follow-up appointment
- **💬 Health Chat** - Ask questions about your diagnosis and treatment
- **📱 Multi-language Support** - Available in English and Hindi
- **🔐 Secure Authentication** - MongoDB-backed user management

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- MongoDB (local or Atlas cloud)
- API Keys (see configuration below)

### Installation

1. **Clone and navigate to project:**
```bash
cd Aushadh\ AI
```

2. **Create `.env` file:**
```env
# Required - Get free key at https://console.groq.com
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx

# Optional - For image analysis (X-rays, MRIs)
# Get at https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_google_gemini_key

# Required - MongoDB connection string
# Format: mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/aushadh_ai

# Optional - Database name (defaults to aushadh_ai)
MONGODB_DB=aushadh_ai
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python run.py
```

The app will open automatically at **http://localhost:8000**

## 📁 Project Structure

```
Aushadh AI/
├── run.py                    # Application entry point
├── main.py                   # FastAPI server configuration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create yourself)
│
├── app/
│   ├── routers/
│   │   ├── analyse.py       # Prescription analysis endpoints
│   │   ├── chat.py          # AI chat endpoint
│   │   ├── export.py        # Export functionality
│   │   └── auth.py          # Authentication endpoints
│   │
│   └── services/
│       ├── mongo_service.py  # MongoDB operations
│       ├── ocr_service.py    # Text extraction from images
│       └── claude_service.py # AI processing logic
│
├── easyocr_models/           # OCR model files
├── config/                  # Configuration files
│
├── Frontend Files
│   ├── index.html           # Landing page
│   ├── login.html           # Sign In / Sign Up
│   ├── dashboard.html       # Main dashboard
│   ├── documents.html       # Upload prescriptions
│   ├── diagnosis.html       # Health summary
│   ├── medications.html     # Medication schedule
│   ├── checklist.html      # Follow-up checklist
│   ├── profile.html         # User profile
│   ├── chat.html            # AI health chat
│   ├── medbuddy.js          # Shared JavaScript utilities
│   ├── logo_green.png       # App logo
│   └── logo_white.png       # App logo (light)
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health check |
| GET | `/` | Landing page |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/logout` | User logout |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/medications` | Save medications |
| GET | `/api/auth/medications` | Get user medications |
| POST | `/api/analyse/file` | Analyze prescription image |
| POST | `/api/analyse/text` | Analyze pasted text |
| POST | `/api/analyse/sample` | Load demo prescription |
| POST | `/api/chat` | Chat with AI about health |
| POST | `/api/export/txt` | Export summary as text |
| GET | `/docs` | Swagger API documentation |

## 🖥️ User Flow

```
index.html (Landing)
    │
    ▼
login.html (Sign In / Sign Up)
    │
    ▼
dashboard.html (Main Dashboard)
    │
    ├─→ documents.html (Upload Prescription)
    │       │
    │       ▼
    │       diagnosis.html (View Analysis)
    │
    ├─→ medications.html (View Medications)
    │
    ├─→ checklist.html (View Tasks)
    │
    ├─→ chat.html (Ask AI Questions)
    │
    └─→ profile.html (User Profile)
```

## 🛠️ Technology Stack

- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **AI:** Groq Llama 3.3 70B + Google Gemini
- **OCR:** EasyOCR
- **Frontend:** HTML, TailwindCSS, Vanilla JavaScript
- **Deployment:** Render, Railway, Heroku

## 🔐 Getting API Keys

### Groq API Key (Required)
1. Go to [console.groq.com](https://console.groq.com)
2. Create a free account
3. Copy your API key
4. Add to `.env`: `GROQ_API_KEY=your_key`

### Google Gemini (Optional - for image analysis)
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create API key
3. Add to `.env`: `GEMINI_API_KEY=your_key`

### MongoDB (Required)
1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free cluster
3. Get connection string
4. Add to `.env`: `MONGODB_URI=your_connection_string`

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process_id> /F
```

### MongoDB connection error
- Verify your `.env` file has correct `MONGODB_URI`
- Check network connectivity
- Ensure IP is whitelisted in MongoDB Atlas

### Login not working
- Check browser console (F12) for errors
- Verify MongoDB is running
- Check `.env` has correct `MONGODB_URI`

### OCR not extracting text
- Ensure image is clear and readable
- Check `easyocr_models/` folder has model files
- Try using higher quality images

## 📄 License

This project is for educational purposes. Always consult your physician for medical advice.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ for better healthcare understanding
