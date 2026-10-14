import pytest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db, get_all_records, add_record, add_biomarker, get_biomarker_history, get_all_reminders, get_profile
from src.advisory import generate_health_advisory, generate_doctor_brief
from src.parser import parse_medical_document

def test_database_initialization_and_seed():
    init_db()
    records = get_all_records()
    assert len(records) >= 5, "Database should have seeded records"

    profile = get_profile()
    assert profile.get("name") == "Alex Kochina"
    assert profile.get("blood_type") == "A+"

def test_record_and_biomarker_addition():
    init_db()
    rec_id = add_record(
        category="test_result",
        title="Automated Test Lab",
        event_date="2026-10-15",
        provider="Dr. Test",
        facility="Lab 1",
        notes="Automated test entry"
    )
    assert rec_id > 0

    add_biomarker(
        record_id=rec_id,
        name="Ferritin",
        value=15.0,
        unit="ng/mL",
        ref_min=24.0,
        ref_max=336.0,
        test_date="2026-10-15"
    )

    history = get_biomarker_history()
    assert "Ferritin" in history
    latest_ferritin = history["Ferritin"][-1]
    assert latest_ferritin["flag"] == "LOW"

def test_advisory_engine():
    records = get_all_records()
    biomarkers = get_biomarker_history()
    reminders = get_all_reminders()
    profile = get_profile()

    advisory = generate_health_advisory(records, biomarkers, reminders, profile)
    assert "insights" in advisory
    assert len(advisory["insights"]) > 0

    # Verify low ferritin was flagged
    ferritin_insight = any("Ferritin" in ins["title"] for ins in advisory["insights"])
    assert ferritin_insight, "Advisory should flag low ferritin"

    # Verify doctor brief was generated
    assert len(advisory["doctor_brief"]) > 50
    assert "PATIENT BRIEF:" in advisory["doctor_brief"]

def test_parser_biomarker_matching():
    sample_text = """
    CENTRAL LAB REPORT - 2026-09-10
    Patient: Alex Kochina
    Serum Ferritin: 19.2 ng/mL [24.0 - 336.0]
    Vitamin D (25-OH): 25.0 ng/mL [30.0 - 100.0]
    Total Cholesterol: 185 mg/dL [125.0 - 200.0]
    Fasting Glucose: 92 mg/dL [70.0 - 99.0]
    """
    result = parse_medical_document(sample_text)
    assert len(result["biomarkers"]) >= 3
    names = [b["name"] for b in result["biomarkers"]]
    assert "Ferritin" in names
    assert "Vitamin D" in names
    assert "Total Cholesterol" in names
