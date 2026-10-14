# Medical Diary (`medical_diary`) - Project Guidelines & Rules

## 1. Operating Environment & Execution Rules (Windows / PowerShell)
- **Virtual Environment:** Active project venv is at `.\.venv\`.
- **Python Execution:** Always invoke Python through the virtual environment binary directly:
  - `& .\.venv\Scripts\python.exe <args>`
  - `& .\.venv\Scripts\pip.exe <args>`
  - Or use the Windows Python launcher: `py -m ...`
- **Never Run `activate`:** Do not invoke `.venv\Scripts\activate` or `activate.ps1` in PowerShell.
- **No Complex One-Liners via `-c`:** Write debug/utility code into `.py` scripts to avoid PowerShell quote-stripping issues.
- **UTF-8 Encoding:** Always enforce UTF-8 for console output and file operations (`py -X utf8` or `encoding='utf-8'` in file I/O).

## 2. Core Architecture & Privacy Principles
- **Privacy First (Local & Encrypted):** Medical records contain sensitive personal identifiable information (PII / PHI). All uploaded documents, test results, and notes must be stored securely. Do not transmit raw unencrypted medical data to unauthenticated external third-party endpoints.
- **Modular Data Architecture:**
  - `models/`: Data models for medical entities (Visits, LabResults, Medications, Screenings/Checkups, Symptoms).
  - `storage/` or `services/ocr/`: Extensible parsers for PDF/image medical documents (OCR, structured extraction).
  - `services/insights/`: Proactive clinical / health reasoning engine with rule-based safety guardrails.
  - `web/` or `api/`: User interface and REST/GraphQL API.
- **Safety & Disclaimers:** AI recommendations must never present themselves as definitive medical diagnoses. They should serve as informed educational suggestions and prompt consultations with licensed healthcare providers.

## 3. Code Quality & Testing Standards
- All backend code must include type hints (`typing` / `pydantic`).
- Maintain unit and integration tests under `tests/` targeting models, parsers, and scheduling logic.
- Verify tests using `& .\.venv\Scripts\pytest.exe`.
