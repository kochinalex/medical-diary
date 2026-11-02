import os
import json
import shutil
import mimetypes
from typing import Optional
from fastapi import FastAPI, Request, Response, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .auth import (
    hash_password, verify_password,
    create_session_token, verify_session_token
)
from .database import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    get_profiles, get_profile, add_profile, update_profile, delete_profile,
    get_all_records, get_record, update_record, add_record, add_biomarker, delete_record,
    get_biomarker_history, get_all_reminders, toggle_reminder,
    add_reminder, delete_reminder, clear_all_records, import_user_health_data
)
from .advisory import generate_health_advisory
from .parser import (
    extract_text_from_pdf, parse_medical_document,
    extract_from_document, translate_medical_text
)
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

def get_current_user_id(request: Request) -> Optional[int]:
    token = request.cookies.get("session_token")
    return verify_session_token(token)

def get_request_lang(request: Request, query_lang: Optional[str] = None) -> str:
    lang = query_lang or request.cookies.get("lang", "en")
    return lang if lang in ["en", "ru", "sr"] else "en"

# ================= AUTH ROUTES =================
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, lang: Optional[str] = None, mode: Optional[str] = "login"):
    user_id = get_current_user_id(request)
    if user_id:
        return RedirectResponse(url="/", status_code=303)
    
    active_lang = get_request_lang(request, lang)
    t = get_translations(active_lang)
    
    res = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"t": t, "lang": active_lang, "mode": mode, "error": None}
    )
    res.set_cookie("lang", active_lang, max_age=31536000)
    return res

@app.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    active_lang = get_request_lang(request)
    t = get_translations(active_lang)
    
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"t": t, "lang": active_lang, "mode": "login", "error": t.get("invalid_credentials", "Invalid credentials")}
        )
    
    token = create_session_token(user["id"])
    res = RedirectResponse(url="/", status_code=303)
    res.set_cookie("session_token", token, max_age=30 * 86400, httponly=True, samesite="lax")
    res.set_cookie("lang", active_lang, max_age=31536000)
    return res

@app.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form("")
):
    active_lang = get_request_lang(request)
    t = get_translations(active_lang)
    
    existing = get_user_by_email(email)
    if existing:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"t": t, "lang": active_lang, "mode": "register", "error": t.get("email_exists", "Email already exists")}
        )
    
    pw_hash = hash_password(password)
    user_id = create_user(email=email, password_hash=pw_hash, full_name=full_name)
    
    token = create_session_token(user_id)
    res = RedirectResponse(url="/", status_code=303)
    res.set_cookie("session_token", token, max_age=30 * 86400, httponly=True, samesite="lax")
    res.set_cookie("lang", active_lang, max_age=31536000)
    return res

@app.get("/logout")
async def logout():
    res = RedirectResponse(url="/login", status_code=303)
    res.delete_cookie("session_token")
    return res

# ================= MAIN APPLICATION =================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, response: Response, lang: Optional[str] = None, profile_id: Optional[int] = None):
    user_id = get_current_user_id(request)
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = get_user_by_id(user_id)
    if not user:
        res = RedirectResponse(url="/login", status_code=303)
        res.delete_cookie("session_token")
        return res

    active_lang = get_request_lang(request, lang)
    t = get_translations(active_lang)

    profiles = get_profiles(user_id=user_id)
    if not profiles:
        # Create an initial self profile if user has none
        p_name = user.get("full_name") or user["email"].split("@")[0].capitalize()
        add_profile(name=p_name, role="Self", avatar_color="#0d9488", user_id=user_id)
        profiles = get_profiles(user_id=user_id)

    default_profile_id = profiles[0]["id"] if profiles else 1

    # Determine Active Profile: query param -> cookie -> default
    if profile_id is None:
        cookie_pid = request.cookies.get("profile_id")
        if cookie_pid is not None and cookie_pid.isdigit():
            profile_id = int(cookie_pid)
        else:
            profile_id = default_profile_id

    # Verify profile belongs to user
    profile_ids = [p["id"] for p in profiles]
    is_all_family = (profile_id == 0)
    if not is_all_family and profile_id not in profile_ids:
        profile_id = default_profile_id

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
        records = get_all_records(profile_id=0, user_id=user_id)
        biomarker_history = get_biomarker_history(profile_id=0, user_id=user_id)
        reminders = get_all_reminders(profile_id=0, user_id=user_id)
    else:
        current_profile = get_profile(profile_id, user_id=user_id)
        if not current_profile and profiles:
            current_profile = profiles[0]
            profile_id = current_profile["id"]

        records = get_all_records(profile_id=profile_id, user_id=user_id)
        biomarker_history = get_biomarker_history(profile_id=profile_id, user_id=user_id)
        reminders = get_all_reminders(profile_id=profile_id, user_id=user_id)

    # Generate Advisory in selected language
    advisory = generate_health_advisory(records, biomarker_history, reminders, current_profile, lang=active_lang)

    # Localize records, reminders, and profile details for display
    localized_records = [localize_record(r, lang=active_lang) for r in records]
    localized_reminders = [localize_reminder(rem, lang=active_lang) for rem in reminders]
    localized_profile = localize_profile(current_profile, lang=active_lang)

    # Localize biomarker display names
    biomarker_display_map = {name: localize_biomarker_name(name, lang=active_lang) for name in biomarker_history.keys()}

    res = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "t": t,
            "lang": active_lang,
            "current_user": user,
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
    res.set_cookie("lang", active_lang, max_age=31536000)
    res.set_cookie("profile_id", str(profile_id), max_age=31536000)
    return res

# ================= REST APIS (SCOPED TO CURRENT USER) =================
@app.post("/api/records")
async def create_record(
    request: Request,
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
    biomarkers_json: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_upload_dir = os.path.join(UPLOAD_DIR, f"user_{user_id}")
    os.makedirs(user_upload_dir, exist_ok=True)

    saved_file_path = ""
    extracted_biomarkers = []
    file_bytes = None
    file_name = ""
    file_mime = ""

    if file and file.filename:
        file_name = file.filename
        file_mime = file.content_type or "application/octet-stream"
        file_bytes = await file.read()
        filename = f"{event_date}_{file.filename}"
        saved_file_path = os.path.join(user_upload_dir, filename)
        try:
            with open(saved_file_path, "wb") as buffer:
                buffer.write(file_bytes)
        except Exception:
            pass

        # If biomarkers_json not already provided, try extracting
        if not biomarkers_json and file.filename.lower().endswith(".pdf"):
            pdf_text = extract_text_from_pdf(file_bytes)
            parsed = parse_medical_document(pdf_text)
            extracted_biomarkers = parsed.get("biomarkers", [])

    rec_id = add_record(
        user_id=user_id,
        profile_id=profile_id,
        category=category,
        title=title,
        event_date=event_date,
        provider=provider or "",
        facility=facility or "",
        notes=notes or "",
        file_path=saved_file_path,
        file_data=file_bytes,
        file_name=file_name,
        file_mime=file_mime
    )

    # 1. Save single biomarker input if provided
    if bm_name and bm_value is not None:
        add_biomarker(
            user_id=user_id,
            profile_id=profile_id,
            record_id=rec_id,
            name=bm_name,
            value=bm_value,
            unit=bm_unit or "units",
            ref_min=None,
            ref_max=None,
            test_date=event_date
        )

    # 2. Save multi-biomarkers from JSON if provided
    if biomarkers_json:
        try:
            b_list = json.loads(biomarkers_json)
            if isinstance(b_list, list):
                for b in b_list:
                    if b.get("name") and b.get("value") is not None:
                        try:
                            v = float(b["value"])
                            rmin = float(b["ref_min"]) if b.get("ref_min") is not None and str(b.get("ref_min")).strip() != "" else None
                            rmax = float(b["ref_max"]) if b.get("ref_max") is not None and str(b.get("ref_max")).strip() != "" else None
                            add_biomarker(
                                user_id=user_id,
                                profile_id=profile_id,
                                record_id=rec_id,
                                name=str(b["name"]).strip(),
                                value=v,
                                unit=str(b.get("unit") or "units").strip(),
                                ref_min=rmin,
                                ref_max=rmax,
                                test_date=event_date
                            )
                        except (ValueError, TypeError):
                            pass
        except Exception as e:
            print("Error parsing biomarkers_json:", e)

    # 3. Save extracted fallback biomarkers if not already stored
    for bm in extracted_biomarkers:
        add_biomarker(
            user_id=user_id,
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

@app.post("/api/scan-document")
async def scan_document_endpoint(
    request: Request,
    file: UploadFile = File(...),
    lang: Optional[str] = Form(None)
):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        content = await file.read()
        filename = file.filename or "document.pdf"
        mime_type = file.content_type
        target_lang = lang or request.cookies.get("lang") or "en"
        extracted = extract_from_document(content, filename=filename, mime_type=mime_type, target_lang=target_lang)
        return {"status": "success", "data": extracted}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/api/records/{record_id}/file")
async def get_record_file(request: Request, record_id: int):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    record = get_record(record_id, user_id=user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if record.get("file_data"):
        filename = record.get("file_name") or "document"
        media_type = record.get("file_mime") or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        return Response(
            content=record["file_data"],
            media_type=media_type,
            headers={"Content-Disposition": f'inline; filename="{filename}"'}
        )

    file_path = record.get("file_path")
    if file_path and os.path.exists(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        filename = os.path.basename(file_path)
        return FileResponse(
            file_path,
            media_type=mime_type or "application/octet-stream",
            filename=filename,
            headers={"Content-Disposition": f'inline; filename="{filename}"'}
        )

    raise HTTPException(status_code=404, detail="File not found")

@app.post("/api/records/{record_id}/translate")
async def translate_record_endpoint(
    request: Request,
    record_id: int,
    target_lang: Optional[str] = Form(None)
):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    record = get_record(record_id, user_id=user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    lang_code = target_lang or request.cookies.get("lang") or "en"
    translated = translate_medical_text(
        title=record.get("title", ""),
        notes=record.get("notes", ""),
        target_lang=lang_code
    )

    update_record(record_id, {
        "title": translated["title"],
        "notes": translated["notes"]
    }, user_id=user_id)

    return {
        "status": "success",
        "title": translated["title"],
        "notes": translated["notes"],
        "lang": lang_code
    }


@app.post("/api/profiles")
async def create_family_member(
    request: Request,
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
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_id = add_profile(
        user_id=user_id,
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

@app.post("/api/profiles/{profile_id}")
async def update_family_member(
    request: Request,
    profile_id: int,
    name: str = Form(...),
    role: str = Form("Self"),
    birth_date: Optional[str] = Form(""),
    gender: Optional[str] = Form("other"),
    blood_type: Optional[str] = Form(""),
    allergies: Optional[str] = Form(""),
    chronic_conditions: Optional[str] = Form(""),
    current_medications: Optional[str] = Form(""),
    emergency_contact: Optional[str] = Form(""),
    avatar_color: Optional[str] = Form("#0d9488")
):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    update_profile(profile_id, {
        "name": name,
        "role": role,
        "birth_date": birth_date or "",
        "gender": gender or "other",
        "blood_type": blood_type or "",
        "allergies": allergies or "",
        "chronic_conditions": chronic_conditions or "",
        "current_medications": current_medications or "",
        "emergency_contact": emergency_contact or "",
        "avatar_color": avatar_color or "#0d9488"
    }, user_id=user_id)
    return {"status": "success", "profile_id": profile_id}

@app.delete("/api/profiles/{profile_id}")
async def remove_family_member(request: Request, profile_id: int):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    success = delete_profile(profile_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete the primary/only profile")
    return {"status": "success"}

@app.post("/api/reminders/{reminder_id}/toggle")
async def toggle_reminder_endpoint(request: Request, reminder_id: int):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    toggle_reminder(reminder_id, user_id=user_id)
    return {"status": "success"}

@app.post("/api/reminders")
async def create_reminder(
    request: Request,
    title: str = Form(...),
    category: str = Form("screening"),
    due_date: str = Form(...),
    profile_id: int = Form(1),
    frequency: str = Form("once"),
    notes: Optional[str] = Form("")
):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    rem_id = add_reminder(
        user_id=user_id,
        title=title,
        category=category,
        due_date=due_date,
        profile_id=profile_id,
        frequency=frequency,
        notes=notes or ""
    )
    return {"status": "success", "reminder_id": rem_id}

@app.delete("/api/records/{record_id}")
async def remove_record(request: Request, record_id: int):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    delete_record(record_id, user_id=user_id)
    return {"status": "success"}

@app.delete("/api/reminders/{reminder_id}")
async def remove_reminder(request: Request, reminder_id: int):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    delete_reminder(reminder_id, user_id=user_id)
    return {"status": "success"}

@app.post("/api/records/clear-sample")
async def clear_sample_endpoint(request: Request, profile_id: Optional[int] = Form(None)):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    clear_all_records(profile_id=profile_id, user_id=user_id)
    return {"status": "success"}

@app.get("/api/export")
async def export_data(request: Request, profile_id: Optional[int] = None, download: bool = False):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    payload = {
        "version": "2.0",
        "profiles": get_profiles(user_id=user_id),
        "records": get_all_records(profile_id=profile_id, user_id=user_id),
        "biomarkers": get_biomarker_history(profile_id=profile_id, user_id=user_id),
        "reminders": get_all_reminders(profile_id=profile_id, user_id=user_id)
    }
    if download:
        return Response(
            content=json.dumps(payload, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=medical_diary_backup.json"}
        )
    return payload

@app.post("/api/import")
async def import_data_endpoint(request: Request, file: UploadFile = File(...)):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
        counts = import_user_health_data(user_id=user_id, data=data)
        return {"status": "success", "counts": counts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid import file: {str(e)}")
