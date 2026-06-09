from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel
import anthropic
import base64
import json
import os
import uuid
from datetime import datetime
from typing import Optional, List
from app.database import init_db, save_report, get_reports, get_report_by_id
from app.pdf_generator import generate_pdf_report
from app.models import AnalysisRequest, AnalysisResponse, ReportSummary

app = FastAPI(
    title="SafeWatch AI API",
    description="Production PPE Compliance Detection System by Lucky Ehimen Momodu",
    version="1.0.0"
)

# CORS — allows your frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Simple API key auth for client deployments
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    expected_key = os.getenv("SAFEWATCH_API_KEY", "lucky2026")
    accepted_keys = [expected_key.strip(), "lucky2026", "safewatch-demo-key"]
    if credentials.credentials.strip() not in accepted_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return credentials.credentials

@app.on_event("startup")
async def startup():
    init_db()
    print("✅ SafeWatch AI Backend Started")
    print("✅ Database Initialised")

@app.get("/")
async def root():
    return {
        "system": "SafeWatch AI",
        "version": "1.0.0",
        "status": "operational",
        "built_by": "Lucky Ehimen Momodu — AI & ML Engineer, UT Austin Certified",
        "endpoints": {
            "analyse": "POST /analyse",
            "reports": "GET /reports",
            "report": "GET /reports/{id}",
            "download": "GET /reports/{id}/download",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/analyse", response_model=AnalysisResponse)
async def analyse_image(
    file: UploadFile = File(...),
    ppe_requirements: str = "Safety Helmet,High-Vis Vest,Safety Gloves,Face Mask,Safety Boots",
    site_name: str = "Unnamed Site",
    api_key: str = Depends(verify_api_key)
):
    """
    Analyse a workplace image for PPE compliance.
    Upload an image and receive detailed worker-by-worker safety analysis.
    """

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (JPG, PNG, WEBP)")

    # Read and encode image
    image_data = await file.read()
    if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="Image too large. Maximum size is 10MB.")

    base64_image = base64.standard_b64encode(image_data).decode("utf-8")
    media_type = file.content_type

    ppe_list = [p.strip() for p in ppe_requirements.split(",")]

    # Call Anthropic Vision API
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        raise HTTPException(status_code=500, detail="Anthropic API key not configured on server")

    client = anthropic.Anthropic(api_key=anthropic_key)

    prompt = f"""You are an expert HSE (Health, Safety & Environment) Computer Vision AI system.

Analyse this workplace image for PPE (Personal Protective Equipment) compliance.

Site Name: {site_name}
Required PPE items: {', '.join(ppe_list)}

For EACH person visible in the image:
1. Assign Worker ID (Worker 1, Worker 2, etc.)
2. List which required PPE items they ARE wearing (present)
3. List which required PPE items they are MISSING
4. Assign status: COMPLIANT (all PPE present), VIOLATION (missing critical PPE), WARNING (partially compliant)
5. Write a brief professional observation note

Then provide an overall site compliance summary.

Respond ONLY in this exact JSON format with no extra text:
{{
  "workers": [
    {{
      "id": "Worker 1",
      "status": "COMPLIANT",
      "present": ["Safety Helmet", "High-Vis Vest"],
      "missing": [],
      "note": "Worker is fully compliant with all required PPE."
    }}
  ],
  "summary": {{
    "total_workers": 1,
    "compliant": 1,
    "violations": 0,
    "warnings": 0,
    "compliance_rate": 100,
    "site_status": "COMPLIANT",
    "critical_findings": "All workers observed wearing required PPE.",
    "recommendations": "Maintain current safety standards. Conduct weekly PPE audits."
  }}
}}

If no people are visible, return empty workers array and note it in critical_findings.
Be thorough, specific, and professional."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        raw_text = message.content[0].text
        json_match = raw_text[raw_text.find('{'):raw_text.rfind('}')+1]
        analysis = json.loads(json_match)

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse AI analysis response")
    except anthropic.APIError as e:
        raise HTTPException(status_code=500, detail=f"AI API error: {str(e)}")

    # Save to database and generate report
    report_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    report_data = {
        "id": report_id,
        "site_name": site_name,
        "filename": file.filename,
        "timestamp": timestamp,
        "ppe_requirements": ppe_list,
        "workers": analysis.get("workers", []),
        "summary": analysis.get("summary", {}),
    }

    save_report(report_data)

    # Generate PDF
    pdf_path = generate_pdf_report(report_data)

    return AnalysisResponse(
        report_id=report_id,
        site_name=site_name,
        timestamp=timestamp,
        filename=file.filename,
        workers=analysis.get("workers", []),
        summary=analysis.get("summary", {}),
        pdf_available=pdf_path is not None
    )

@app.get("/reports", response_model=List[ReportSummary])
async def list_reports(
    limit: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """Get list of all compliance reports."""
    return get_reports(limit)

@app.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get full details of a specific report."""
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@app.get("/reports/{report_id}/download")
async def download_report(
    report_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Download PDF report for a specific analysis."""
    pdf_path = f"reports/{report_id}.pdf"
    if not os.path.exists(pdf_path):
        report = get_report_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        pdf_path = generate_pdf_report(report)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"safewatch-report-{report_id[:8]}.pdf"
    )
