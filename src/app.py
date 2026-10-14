import os
import json
import shutil
from typing import Optional
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import (
    init_db, get_all_records, add_record, add_biomarker,
    get_biomarker_history, get_all_reminders, toggle_reminder,
    add_reminder, get_profile, update_profile
)
from .advisory import generate_health_advisory
from .parser import extract_text_from_pdf, parse_medical_document

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize database
init_db()

app = FastAPI(title="Medical Diary")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "src", "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    records = get_all_records()
    biomarker_history = get_biomarker_history()
    reminders = get_all_reminders()
    profile = get_profile()

    advisory = generate_health_advisory(records, biomarker_history, reminders, profile)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "records": records,
            "biomarker_history": biomarker_history,
            "biomarker_json": json.dumps(biomarker_history),
            "reminders": reminders,
            "profile": profile,
            "advisory": advisory
        }
    )

@app.post("/api/records")
async def create_record(
    category: str = Form(...),
    title: str = Form(...),
    event_date: str = Form(...),
    provider: Optional[str] = Form(""),
    facility: Optional[str] = Form(""),
    notes: Optional[str] = Form(""),
    bm_name: Optional[str] = Form(None),
    bm_value: Optional[float] = Form(None),
    bm_unit: Optional[str] = Form(""),
    file: Optional[UploadFile] = File(None)
):
    saved_file_path = ""
    extracted_biomarkers = []

    if file and file.filename:
        filename = f"{event_date}_{file.filename}"
        saved_file_path = os.path.join(UPLOAD_DIR, filename)
        with open(saved_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # If PDF, attempt OCR / text extraction
        if file.filename.lower().endswith(".pdf"):
            pdf_text = extract_text_from_pdf(saved_file_path)
            parsed = parse_medical_document(pdf_text)
            extracted_biomarkers = parsed.get("biomarkers", [])

    rec_id = add_record(
        category=category,
        title=title,
        event_date=event_date,
        provider=provider or "",
        facility=facility or "",
        notes=notes or "",
        file_path=saved_file_path
    )

    # Add manually entered biomarker
    if bm_name and bm_value is not None:
        add_biomarker(
            record_id=rec_id,
            name=bm_name,
            value=bm_value,
            unit=bm_unit or "units",
            ref_min=None,
            ref_max=None,
            test_date=event_date
        )

    # Add any auto-extracted biomarkers from uploaded PDF
    for bm in extracted_biomarkers:
        add_biomarker(
            record_id=rec_id,
            name=bm["name"],
            value=bm["value"],
            unit=bm["unit"],
            ref_min=bm["ref_min"],
            ref_max=bm["ref_max"],
            test_date=event_date
        )

    return {"status": "success", "record_id": rec_id}

@app.post("/api/reminders/{reminder_id}/toggle")
async def toggle_reminder_endpoint(reminder_id: int):
    toggle_reminder(reminder_id)
    return {"status": "success"}

@app.post("/api/reminders")
async def create_reminder(
    title: str = Form(...),
    category: str = Form("screening"),
    due_date: str = Form(...),
    frequency: str = Form("once"),
    notes: Optional[str] = Form("")
):
    rem_id = add_reminder(title, category, due_date, frequency, notes or "")
    return {"status": "success", "reminder_id": rem_id}

@app.get("/api/export")
async def export_data():
    return {
        "profile": get_profile(),
        "records": get_all_records(),
        "biomarkers": get_biomarker_history(),
        "reminders": get_all_reminders()
    }
