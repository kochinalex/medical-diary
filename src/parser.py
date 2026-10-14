import re
from typing import Dict, Any, List
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

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
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

    # Extract date if found
    date_match = re.search(r"\b(20[2-3][0-9][-/.](?:0[1-9]|1[0-2])[-/.](?:0[1-9]|[12][0-9]|3[01]))\b", text)
    extracted_date = date_match.group(1).replace("/", "-").replace(".", "-") if date_match else None

    return {
        "raw_text": text[:1000],
        "extracted_date": extracted_date,
        "biomarkers": biomarkers
    }
