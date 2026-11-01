import os
import sys
import json
import pytest
from starlette.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import app
from src.database import init_db, get_all_records, get_biomarker_history
from src.auth import create_session_token
from src.parser import parse_medical_document, extract_from_document

init_db()

@pytest.fixture
def auth_client():
    client = TestClient(app)
    token = create_session_token(1)
    client.cookies.set("session_token", token)
    return client

def test_offline_parser_biomarkers_and_date():
    text = """
    Central Medical Diagnostic Center
    Date: 2026-09-15
    Doctor: Dr. Helen Thorne
    Patient: Alex Kochina
    Test Name: Comprehensive Metabolic & Lipid Panel
    Fasting Glucose: 92.5 mg/dL [70.0 - 99.0]
    Total Cholesterol: 185.0 mg/dL [125.0 - 200.0]
    Ferritin: 19.5 ng/mL [24.0 - 336.0]
    TSH: 2.1 uIU/mL [0.4 - 4.0]
    Notes: Mild iron depletion observed. Fasting blood sugar and thyroid function within ideal ranges.
    """
    res = parse_medical_document(text)
    assert res["category"] == "test_result"
    assert res["event_date"] == "2026-09-15"
    assert len(res["biomarkers"]) >= 3
    b_names = [b["name"] for b in res["biomarkers"]]
    assert "Fasting Glucose" in b_names
    assert "Ferritin" in b_names
    assert "TSH" in b_names

def test_scan_document_endpoint_requires_auth():
    unauth_client = TestClient(app)
    res = unauth_client.post(
        "/api/scan-document",
        files={"file": ("report.pdf", b"%PDF-1.4...", "application/pdf")}
    )
    assert res.status_code == 401

def test_scan_document_endpoint_success(auth_client):
    sample_text = b"""
    City Health Laboratory
    Date: 2026-10-01
    Dr. Robert Sterling
    Vitamin D (25-OH): 24.5 ng/mL [30.0 - 100.0]
    Ferritin: 21.0 ng/mL [24.0 - 336.0]
    Notes: Continue vitamin D3 supplementation.
    """
    res = auth_client.post(
        "/api/scan-document",
        files={"file": ("lab_report.txt", sample_text, "text/plain")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    extracted = data["data"]
    assert "category" in extracted
    assert "title" in extracted
    assert "biomarkers" in extracted

def test_create_record_with_multi_biomarkers_json(auth_client):
    biomarkers = [
        {"name": "Ferritin", "value": 16.5, "unit": "ng/mL", "ref_min": 24.0, "ref_max": 336.0},
        {"name": "Vitamin D", "value": 21.0, "unit": "ng/mL", "ref_min": 30.0, "ref_max": 100.0},
        {"name": "HbA1c", "value": 5.2, "unit": "%", "ref_min": 4.0, "ref_max": 5.6}
    ]

    res = auth_client.post(
        "/api/records",
        data={
            "profile_id": 1,
            "category": "test_result",
            "title": "Comprehensive Iron & Vitamin Panel",
            "event_date": "2026-10-28",
            "provider": "Dr. Sarah Vance",
            "facility": "Central Diagnostics",
            "notes": "Follow-up lab after 3 months",
            "biomarkers_json": json.dumps(biomarkers)
        }
    )
    assert res.status_code == 200
    rec_id = res.json()["record_id"]
    assert rec_id > 0

    # Verify all 3 biomarkers were recorded
    history = get_biomarker_history(profile_id=1, user_id=1)
    assert "Ferritin" in history
    assert "Vitamin D" in history
    assert "HbA1c" in history
    hba1c_entries = history["HbA1c"]
    assert any(h["value"] == 5.2 for h in hba1c_entries)
