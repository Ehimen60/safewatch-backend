# 🦺 SafeWatch AI — Production Backend

**PPE Compliance Detection System**
Built by Lucky Ehimen Momodu — AI & ML Engineer | UT Austin Certified

---

## What This Does

A production-ready REST API that:
- Accepts workplace image uploads
- Analyses PPE compliance using Claude Vision AI
- Returns worker-by-worker safety analysis
- Generates downloadable PDF compliance reports
- Stores all reports in a database
- Secures all endpoints with API key authentication

---

## Project Structure

```
safewatch-backend/
├── app/
│   ├── __init__.py
│   ├── main.py          ← FastAPI application & all endpoints
│   ├── models.py        ← Request/Response data models
│   ├── database.py      ← SQLite database operations
│   └── pdf_generator.py ← Professional PDF report generation
├── reports/             ← Generated PDFs stored here
├── requirements.txt     ← Python dependencies
├── railway.toml         ← Railway deployment config
├── Procfile             ← Process config for deployment
├── .env.example         ← Environment variables template
└── README.md
```

---

## Setup On Your Laptop (Local Development)

### Step 1 — Download the project files
Save all files into a folder called `safewatch-backend` on your laptop.

### Step 2 — Open terminal in the project folder
- Press `Windows + R` → type `cmd` → press Enter
- Navigate to your folder:
```
cd path\to\safewatch-backend
```

### Step 3 — Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```
You'll see `(venv)` appear in your terminal — this means it's active.

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```
This installs FastAPI, Anthropic SDK, ReportLab (PDF), and all other packages.

### Step 5 — Set up environment variables
```bash
copy .env.example .env
```
Then open `.env` in Notepad and fill in:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
SAFEWATCH_API_KEY=choose-any-strong-password-here
```

### Step 6 — Run the server
```bash
uvicorn app.main:app --reload
```

### Step 7 — Test it's working
Open your browser and go to:
```
http://localhost:8000
```
You should see:
```json
{
  "system": "SafeWatch AI",
  "version": "1.0.0",
  "status": "operational"
}
```

### Step 8 — View the API Documentation
Go to:
```
http://localhost:8000/docs
```
This shows the full interactive API documentation — you can test every endpoint here!

---

## API Endpoints

### POST /analyse
Upload a workplace image for PPE analysis.

**Headers:**
```
Authorization: Bearer your-safewatch-api-key
```

**Form Data:**
- `file` — Image file (JPG, PNG, WEBP)
- `ppe_requirements` — Comma-separated PPE items (optional)
- `site_name` — Name of the site (optional)

**Example Response:**
```json
{
  "report_id": "uuid-here",
  "site_name": "Factory Floor A",
  "timestamp": "2026-06-01T10:30:00",
  "workers": [
    {
      "id": "Worker 1",
      "status": "VIOLATION",
      "present": ["Safety Helmet", "High-Vis Vest"],
      "missing": ["Safety Gloves", "Face Mask"],
      "note": "Worker missing hand and respiratory protection."
    }
  ],
  "summary": {
    "total_workers": 1,
    "compliant": 0,
    "violations": 1,
    "compliance_rate": 0,
    "site_status": "NON-COMPLIANT",
    "critical_findings": "Worker observed without gloves near machinery.",
    "recommendations": "Immediately enforce glove and mask policy in this zone."
  },
  "pdf_available": true
}
```

### GET /reports
Get list of all compliance reports.

### GET /reports/{report_id}
Get full details of a specific report.

### GET /reports/{report_id}/download
Download the PDF report.

### GET /health
Health check endpoint.

---

## Deploy to Railway (5 Minutes)

### Step 1 — Create GitHub repository
1. Go to github.com → New repository
2. Name it `safewatch-backend`
3. Upload all project files

### Step 2 — Deploy on Railway
1. Go to railway.app → Sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `safewatch-backend` repo
4. Railway auto-detects Python and deploys

### Step 3 — Add environment variables on Railway
1. Click your project → "Variables" tab
2. Add:
   - `ANTHROPIC_API_KEY` = your Anthropic key
   - `SAFEWATCH_API_KEY` = your chosen password

### Step 4 — Get your live URL
Railway gives you a URL like:
```
https://safewatch-backend-production.up.railway.app
```

Your API is now live! 🚀

---

## Connect Frontend to Backend

Update your `safewatch-ai.html` frontend to call your Railway URL instead of Anthropic directly:

```javascript
// Replace the Anthropic direct call with:
const res = await fetch('https://your-railway-url.up.railway.app/analyse', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-safewatch-api-key'
  },
  body: formData  // FormData with the image file
});
```

---

## For Client Deployments

When you deploy for a paying client:

1. They get their own Railway/AWS instance
2. Their `ANTHROPIC_API_KEY` is configured on the server — they never see it
3. Their `SAFEWATCH_API_KEY` is a unique key only their system uses
4. You manage the server as part of the monthly retainer
5. All their compliance reports are stored in their own database

---

## Pricing Reminder

| Package | Price | What They Get |
|---------|-------|---------------|
| SafeWatch Lite | ₦350,000 | This backend + basic frontend |
| SafeWatch Pro | ₦900,000 | + Live camera + multi-user dashboard |
| SafeWatch Enterprise | ₦2,500,000+ | + CCTV integration + mobile app |
| Monthly Retainer | ₦120,000–₦300,000 | Server + support + updates |

---

## Built By

**Lucky Ehimen Momodu**
AI & ML Engineer | Supply Chain Specialist
Post Graduate Program — AI & ML, University of Texas at Austin (GPA 3.9)

*"10+ years of supply chain experience. Now powered by AI."*
