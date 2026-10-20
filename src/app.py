import os
import json
import shutil
from typing import Optional
from fastapi import FastAPI, Request, Response, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import (
    init_db, get_profiles, get_profile, add_profile, update_profile, delete_profile,
    get_all_records, add_record, add_biomarker,
    get_biomarker_history, get_all_reminders, toggle_reminder,
    add_reminder
)
from .advisory import generate_health_advisory
from .parser import extract_text_from_pdf, parse_medical_document
from .i18n import (
    get_translations, localize_record, localize_reminder,
    localize_profile, localize_biomarker_name
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize database
init_db()

app = FastAPI(title="Medical Diary")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "src", "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, response: Response, lang: Optional[str] = None, profile_id: Optional[int] = None):
    # Determine Language: query param -> cookie -> default "en"
    if not lang:
        lang = request.cookies.get("lang", "en")
    if lang not in ["en", "ru", "sr"]:
        lang = "en"

    t = get_translations(lang)

    profiles = get_profiles()
    if not profiles:
        init_db()
        profiles = get_profiles()

    default_profile_id = profiles[0]["id"] if profiles else 1

    # Determine Active Profile: query param -> cookie -> default
    if profile_id is None:
        cookie_pid = request.cookies.get("profile_id")
        if cookie_pid is not None and cookie_pid.isdigit():
            profile_id = int(cookie_pid)
        else:
            profile_id = default_profile_id

    is_all_family = (profile_id == 0)

    if is_all_family:
        current_profile = {
            "id": 0,
            "name": t.get("all_family", "All Family"),
            "role": "Family",
            "blood_type": "Various",
            "allergies": "",
            "chronic_conditions": "",
            "current_medications": "",
            "avatar_color": "#475569"
        }
        records = get_all_records(profile_id=0)
        biomarker_history = get_biomarker_history(profile_id=0)
        reminders = get_all_reminders(profile_id=0)
    else:
        current_profile = get_profile(profile_id)
        if not current_profile and profiles:
            current_profile = profiles[0]
            profile_id = current_profile["id"]

        records = get_all_records(profile_id=profile_id)
        biomarker_history = get_biomarker_history(profile_id=profile_id)
        reminders = get_all_reminders(profile_id=profile_id)

    # Generate Advisory in selected language
    advisory = generate_health_advisory(records, biomarker_history, reminders, current_profile, lang=lang)

    # Localize records, reminders, and profile details for display
    localized_records = [localize_record(r, lang=lang) for r in records]
    localized_reminders = [localize_reminder(rem, lang=lang) for rem in reminders]
    localized_profile = localize_profile(current_profile, lang=lang)

    # Localize biomarker display names
    biomarker_display_map = {name: localize_biomarker_name(name, lang=lang) for name in biomarker_history.keys()}

    res = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "t": t,
            "lang": lang,
            "profiles": profiles,
            "current_profile": localized_profile,
            "raw_profile": current_profile,
            "profile_id": profile_id,
            "is_all_family": is_all_family,
            "records": localized_records,
            "biomarker_history": biomarker_history,
            "biomarker_display_map": biomarker_display_map,
            "biomarker_json": json.dumps(biomarker_history),
            "reminders": localized_reminders,
            "advisory": advisory
        }
    )
    res.set_cookie("lang", lang, max_age=31536000)
    res.set_cookie("profile_id", str(profile_id), max_age=31536000)
    return res

@app.post("/api/records")
async def create_record(
    category: str = Form(...),
    title: str = Form(...),
    event_date: str = Form(...),
    profile_id: int = Form(1),
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

        if file.filename.lower().endswith(".pdf"):
            pdf_text = extract_text_from_pdf(saved_file_path)
            parsed = parse_medical_document(pdf_text)
            extracted_biomarkers = parsed.get("biomarkers", [])

    rec_id = add_record(
        profile_id=profile_id,
        category=category,
        title=title,
        event_date=event_date,
        provider=provider or "",
        facility=facility or "",
        notes=notes or "",
        file_path=saved_file_path
    )

    if bm_name and bm_value is not None:
        add_biomarker(
            profile_id=profile_id,
            record_id=rec_id,
            name=bm_name,
            value=bm_value,
            unit=bm_unit or "units",
            ref_min=None,
            ref_max=None,
            test_date=event_date
        )

    for bm in extracted_biomarkers:
        add_biomarker(
            profile_id=profile_id,
            record_id=rec_id,
            name=bm["name"],
            value=bm["value"],
            unit=bm["unit"],
            ref_min=bm["ref_min"],
            ref_max=bm["ref_max"],
            test_date=event_date
        )

    return {"status": "success", "record_id": rec_id}

@app.post("/api/profiles")
async def create_family_member(
    name: str = Form(...),
    role: str = Form("Child"),
    birth_date: Optional[str] = Form(""),
    gender: Optional[str] = Form("other"),
    blood_type: Optional[str] = Form(""),
    allergies: Optional[str] = Form(""),
    chronic_conditions: Optional[str] = Form(""),
    current_medications: Optional[str] = Form(""),
    emergency_contact: Optional[str] = Form(""),
    avatar_color: Optional[str] = Form("#0d9488")
):
    new_id = add_profile(
        name=name,
        role=role,
        birth_date=birth_date or "",
        gender=gender or "other",
        blood_type=blood_type or "",
        allergies=allergies or "",
        chronic_conditions=chronic_conditions or "",
        current_medications=current_medications or "",
        emergency_contact=emergency_contact or "",
        avatar_color=avatar_color or "#0d9488"
    )
    return {"status": "success", "profile_id": new_id}

@app.delete("/api/profiles/{profile_id}")
async def remove_family_member(profile_id: int):
    success = delete_profile(profile_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete the primary/only profile")
    return {"status": "success"}

@app.post("/api/reminders/{reminder_id}/toggle")
async def toggle_reminder_endpoint(reminder_id: int):
    toggle_reminder(reminder_id)
    return {"status": "success"}

@app.post("/api/reminders")
async def create_reminder(
    title: str = Form(...),
    category: str = Form("screening"),
    due_date: str = Form(...),
    profile_id: int = Form(1),
    frequency: str = Form("once"),
    notes: Optional[str] = Form("")
):
    rem_id = add_reminder(title, category, due_date, profile_id=profile_id, frequency=frequency, notes=notes or "")
    return {"status": "success", "reminder_id": rem_id}

@app.get("/api/export")
async def export_data(profile_id: Optional[int] = None):
    return {
        "profiles": get_profiles(),
        "records": get_all_records(profile_id=profile_id),
        "biomarkers": get_biomarker_history(profile_id=profile_id),
        "reminders": get_all_reminders(profile_id=profile_id)
    }
