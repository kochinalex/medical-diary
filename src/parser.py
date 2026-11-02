import os
import re
import json
import base64
import io
from typing import Dict, Any, List, Optional
import httpx
from pypdf import PdfReader

COMMON_BIOMARKER_PATTERNS = {
    "Ferritin": r"(?:ferritin|serum ferritin)(?:\s*\([^)]*\))?[\s:]*([0-9]+\.?[0-9]*)[\s]*(ng/ml|ug/l)?(?:[\s]*\[?([0-9]+\.?[0-9]*)[\s]*-[\s]*([0-9]+\.?[0-9]*)\]?)?",
    "Vitamin D": r"(?:vitamin d(?:\s*\([^)]*\))?|25-oh vitamin d|25-hydroxyvitamin d)[\s:]*([0-9]+\.?[0-9]*)[\s]*(ng/ml|nmol/l)?(?:[\s]*\[?([0-9]+\.?[0-9]*)[\s]*-[\s]*([0-9]+\.?[0-9]*)\]?)?",
    "Total Cholesterol": r"(?:total cholesterol|cholesterol total)(?:\s*\([^)]*\))?[\s:]*([0-9]+\.?[0-9]*)[\s]*(mg/dl|mmol/l)?(?:[\s]*\[?([0-9]+\.?[0-9]*)[\s]*-[\s]*([0-9]+\.?[0-9]*)\]?)?",
    "LDL": r"(?:ldl|ldl cholesterol|cholesterol ldl)(?:\s*\([^)]*\))?[\s:]*([0-9]+\.?[0-9]*)[\s]*(mg/dl|mmol/l)?(?:[\s]*\[?([0-9]+\.?[0-9]*)[\s]*-[\s]*([0-9]+\.?[0-9]*)\]?)?",
    "HDL": r"(?:hdl|hdl cholesterol|cholesterol hdl)(?:\s*\([^)]*\))?[\s:]*([0-9]+\.?[0-9]*)[\s]*(mg/dl|mmol/l)?(?:[\s]*\[?([0-9]+\.?[0-9]*)[\s]*-[\s]*([0-9]+\.?[0-9]*)\]?)?",
    "Fasting Glucose": r"(?:fasting blood glucose|fasting glucose|glucose|blood sugar)(?:\s*\([^)]*\))?[\s:]*([0-9]+\.?[0-9]*)[\s]*(mg/dl|mmol/l)?(?:[\s]*\[?([0-9]+\.?[0-9]*)[\s]*-[\s]*([0-9]+\.?[0-9]*)\]?)?",
    "HbA1c": r"(?:hba1c|hemoglobin a1c|glycated hemoglobin)(?:\s*\([^)]*\))?[\s:]*([0-9]+\.?[0-9]*)[\s]*(%|mmol/mol)?(?:[\s]*\[?([0-9]+\.?[0-9]*)[\s]*-[\s]*([0-9]+\.?[0-9]*)\]?)?",
    "TSH": r"(?:tsh|thyroid stimulating hormone)(?:\s*\([^)]*\))?[\s:]*([0-9]+\.?[0-9]*)[\s]*(uiu/ml|miu/l|uui/ml)?(?:[\s]*\[?([0-9]+\.?[0-9]*)[\s]*-[\s]*([0-9]+\.?[0-9]*)\]?)?"
}

DEFAULT_UNITS = {
    "Ferritin": ("ng/mL", 24.0, 336.0),
    "Vitamin D": ("ng/mL", 30.0, 100.0),
    "Total Cholesterol": ("mg/dL", 125.0, 200.0),
    "LDL": ("mg/dL", 50.0, 100.0),
    "HDL": ("mg/dL", 40.0, 90.0),
    "Fasting Glucose": ("mg/dL", 70.0, 99.0),
    "HbA1c": ("%", 4.0, 5.6),
    "TSH": ("uIU/mL", 0.4, 4.0)
}

def extract_text_from_pdf(file_path_or_bytes) -> str:
    text = ""
    try:
        if isinstance(file_path_or_bytes, bytes):
            stream = io.BytesIO(file_path_or_bytes)
            reader = PdfReader(stream)
        else:
            reader = PdfReader(file_path_or_bytes)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def parse_medical_document(text: str) -> Dict[str, Any]:
    biomarkers = []
    text_lower = text.lower()

    for name, pattern in COMMON_BIOMARKER_PATTERNS.items():
        match = re.search(pattern, text_lower)
        if match:
            try:
                val = float(match.group(1))
                unit = match.group(2) if match.group(2) else DEFAULT_UNITS[name][0]
                ref_min = float(match.group(3)) if match.group(3) else DEFAULT_UNITS[name][1]
                ref_max = float(match.group(4)) if match.group(4) else DEFAULT_UNITS[name][2]
                biomarkers.append({
                    "name": name,
                    "value": val,
                    "unit": unit,
                    "ref_min": ref_min,
                    "ref_max": ref_max
                })
            except Exception:
                pass

    date_match = re.search(r"\b(20[2-3][0-9][-/.](?:0[1-9]|1[0-2])[-/.](?:0[1-9]|[12][0-9]|3[01]))\b", text)
    extracted_date = date_match.group(1).replace("/", "-").replace(".", "-") if date_match else None

    # Simple provider and facility heuristics
    provider = ""
    facility = ""
    doc_match = re.search(r"(?:dr\.?|doctor|physician)\s+([a-z\s]+)", text, re.IGNORECASE)
    if doc_match:
        provider = doc_match.group(0).strip().title()

    clinic_match = re.search(r"([a-z0-9\s]+(?:clinic|hospital|laboratory|lab|center|health|poliklinika|bolnica))", text, re.IGNORECASE)
    if clinic_match:
        facility = clinic_match.group(1).strip().title()

    return {
        "category": "test_result" if biomarkers else "visit",
        "event_date": extracted_date,
        "title": "Medical Record" if not biomarkers else "Lab Test Results",
        "provider": provider,
        "facility": facility,
        "notes": text[:500].strip(),
        "biomarkers": biomarkers
    }

def extract_from_document(file_bytes: bytes, filename: str, mime_type: Optional[str] = None, target_lang: str = "en") -> Dict[str, Any]:
    """
    Extracts structured medical record data from an uploaded scan, image, or PDF.
    First tries Gemini multimodal AI for high-accuracy multilingual extraction and automatic translation to target_lang.
    Falls back gracefully to offline regex/pypdf if API key is not present or call fails.
    """
    if not mime_type:
        ext = os.path.splitext(filename.lower())[1]
        if ext in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        elif ext == ".png":
            mime_type = "image/png"
        elif ext == ".webp":
            mime_type = "image/webp"
        else:
            mime_type = "application/pdf"

    LANG_MAP = {
        "ru": "Russian",
        "en": "English",
        "sr": "Serbian"
    }
    target_lang_name = LANG_MAP.get((target_lang or "en").lower(), "English")

    api_key = os.environ.get("GEMINI_API_KEY")
    is_image = bool(mime_type and mime_type.startswith("image/"))

    if not api_key:
        if is_image:
            raise ValueError("GEMINI_API_KEY is missing on the server. Please add your GEMINI_API_KEY in the Render Environment settings.")
    else:
        try:
            b64_data = base64.b64encode(file_bytes).decode("utf-8")
            prompt = f"""You are an expert clinical document analyzer and medical translator.
Analyze this medical document (lab report, doctor's visit summary, prescription, discharge summary, or sickness note).
Extract all relevant fields into a single JSON object with this exact schema:
{{
  "category": "visit" | "test_result" | "sickness" | "intervention" | "comment",
  "event_date": "YYYY-MM-DD",
  "title": "Short descriptive title translated into {target_lang_name} (e.g. MRI of Right Knee, Comprehensive Blood Panel)",
  "provider": "Doctor / Physician / Specialist name (keep in original/recognizable form) or empty string",
  "facility": "Clinic / Hospital / Laboratory name (keep in original/recognizable form) or empty string",
  "notes": "Concise clinical summary of findings, diagnosis, conclusions, and physician advice translated accurately into {target_lang_name}",
  "biomarkers": [
    {{
      "name": "Standard biomarker name translated into {target_lang_name} (e.g. Ferritin, Vitamin D, Fasting Glucose)",
      "value": numeric_value_float_or_null,
      "unit": "standard measurement unit",
      "ref_min": numeric_lower_reference_limit_or_null,
      "ref_max": numeric_upper_reference_limit_or_null
    }}
  ]
}}
IMPORTANT: You MUST translate the 'title', 'notes' (all clinical findings, conclusions, and advice), and biomarker names into {target_lang_name} to match the user's diary language. Keep physician and facility names recognizable.
If event_date is missing, use current date. Ensure category matches document type accurately.
Return ONLY valid JSON.
"""
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inlineData": {"mimeType": mime_type, "data": b64_data}}
                    ]
                }],
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            }
            with httpx.Client(timeout=25.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    resp_json = res.json()
                    candidates = resp_json.get("candidates", [])
                    if candidates:
                        text_part = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        data = json.loads(text_part)
                        if isinstance(data, list) and len(data) > 0:
                            data = data[0]
                        if isinstance(data, dict):
                            # Ensure clean structure
                            return {
                                "category": data.get("category", "visit"),
                                "event_date": data.get("event_date"),
                                "title": data.get("title", "Medical Record"),
                                "provider": data.get("provider", ""),
                                "facility": data.get("facility", ""),
                                "notes": data.get("notes", ""),
                                "biomarkers": data.get("biomarkers", [])
                            }
                    if is_image:
                        raise ValueError("Gemini AI was unable to parse clinical data from this image. Please ensure the document photo is clear.")
                else:
                    err_msg = res.text
                    try:
                        err_msg = res.json().get("error", {}).get("message", res.text)
                    except Exception:
                        pass
                    print(f"Gemini API returned error {res.status_code}: {err_msg}")
                    if is_image:
                        raise ValueError(f"Gemini API error ({res.status_code}): {err_msg}")
        except Exception as e:
            print(f"Gemini document scan error: {e}")
            if is_image:
                raise

    # Fallback to local offline parser for PDFs
    raw_text = ""
    if mime_type == "application/pdf" or filename.lower().endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_bytes)
    return parse_medical_document(raw_text)

def translate_medical_text(title: str, notes: str, target_lang: str = "en") -> Dict[str, str]:
    """
    Translates medical record title and clinical notes into the target language using Gemini.
    """
    LANG_MAP = {
        "ru": "Russian",
        "en": "English",
        "sr": "Serbian"
    }
    target_lang_name = LANG_MAP.get((target_lang or "en").lower(), "English")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"title": title, "notes": notes}

    try:
        prompt = f"""Translate the following medical record title and clinical notes into {target_lang_name} with high clinical accuracy.
Title: {title}
Notes: {notes}

Return a single JSON object with this exact schema:
{{
  "title": "Translated title in {target_lang_name}",
  "notes": "Translated clinical notes in {target_lang_name}"
}}
Return ONLY valid JSON.
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        with httpx.Client(timeout=20.0) as client:
            res = client.post(url, json=payload)
            if res.status_code == 200:
                candidates = res.json().get("candidates", [])
                if candidates:
                    text_part = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    data = json.loads(text_part)
                    if isinstance(data, dict):
                        return {
                            "title": data.get("title", title),
                            "notes": data.get("notes", notes)
                        }
    except Exception as e:
        print(f"Translation error: {e}")

    return {"title": title, "notes": notes}

