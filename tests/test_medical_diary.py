import pytest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import (
    init_db, get_profiles, get_profile, add_profile, update_profile, delete_profile,
    get_all_records, add_record, add_biomarker, get_biomarker_history,
    get_all_reminders
)
from src.advisory import generate_health_advisory, generate_doctor_brief
from src.parser import parse_medical_document
from src.i18n import get_translations

def test_database_initialization_and_profiles():
    init_db()
    profiles = get_profiles()
    assert len(profiles) >= 2, "Database should have seeded Mother and Child profiles"

    primary = profiles[0]
    assert primary.get("name") == "Alex Kochina"
    assert primary.get("role") == "Mother"

    child = profiles[1]
    assert child.get("name") == "Leo Kochina"
    assert child.get("role") == "Child"

def test_family_profiles_and_scoped_records():
    init_db()
    # Add a 3rd member (Spouse)
    spouse_id = add_profile(
        name="Dan Kochina",
        role="Spouse",
        birth_date="1988-11-20",
        gender="male",
        blood_type="O+",
        allergies="None"
    )
    assert spouse_id > 2

    # Add a record for Dan
    rec_id = add_record(
        profile_id=spouse_id,
        category="visit",
        title="Spouse Routine Health Checkup",
        event_date="2026-10-18",
        provider="Dr. Smith"
    )
    assert rec_id > 0

    # Verify filtering: Dan's records vs Leo's records
    dan_records = get_all_records(profile_id=spouse_id)
    assert len(dan_records) == 1
    assert dan_records[0]["title"] == "Spouse Routine Health Checkup"

    leo_records = get_all_records(profile_id=2)
    assert all(r["profile_id"] == 2 for r in leo_records)

    # Clean up test member
    delete_profile(spouse_id)
    assert get_profile(spouse_id) == {}

def test_profile_update():
    init_db()
    test_id = add_profile(
        name="Test Person",
        role="Self",
        birth_date="1995-01-01",
        blood_type="B+"
    )
    assert test_id > 0
    update_profile(test_id, {
        "name": "Updated Person",
        "role": "Father",
        "birth_date": "1994-02-02",
        "gender": "male",
        "blood_type": "AB+",
        "allergies": "Pollen, Dust",
        "chronic_conditions": "None",
        "current_medications": "Vitamin D",
        "emergency_contact": "Emergency: 555-0199",
        "avatar_color": "#3b82f6"
    })
    updated = get_profile(test_id)
    assert updated["name"] == "Updated Person"
    assert updated["role"] == "Father"
    assert updated["blood_type"] == "AB+"
    assert updated["allergies"] == "Pollen, Dust"

    delete_profile(test_id)
    assert get_profile(test_id) == {}

def test_i18n_dictionaries():
    for lang in ["en", "ru", "sr"]:
        t = get_translations(lang)
        assert "app_title" in t
        assert "timeline_tab" in t
        assert "cat_visit" in t
        assert "emergency_card_title" in t
        assert "search_placeholder" in t
        assert "sort_newest" in t
        assert "sort_oldest" in t
        assert "edit_profile_btn" in t
        assert len(t["cat_visit"]) > 0

def test_pediatric_vs_adult_advisory():
    # Adult Profile (Alex, 36 y.o.)
    adult = get_profile(1)
    adult_records = get_all_records(profile_id=1)
    adult_bms = get_biomarker_history(profile_id=1)
    adult_rems = get_all_reminders(profile_id=1)

    advisory_en = generate_health_advisory(adult_records, adult_bms, adult_rems, adult, lang="en")
    assert any("Ferritin" in ins["title"] for ins in advisory_en["insights"])

    advisory_ru = generate_health_advisory(adult_records, adult_bms, adult_rems, adult, lang="ru")
    assert any("ферритин" in ins["title"].lower() for ins in advisory_ru["insights"])

    advisory_sr = generate_health_advisory(adult_records, adult_bms, adult_rems, adult, lang="sr")
    assert any("feritin" in ins["title"].lower() for ins in advisory_sr["insights"])

    # Child Profile (Leo, 4 y.o.)
    child = get_profile(2)
    child_records = get_all_records(profile_id=2)
    child_bms = get_biomarker_history(profile_id=2)
    child_rems = get_all_reminders(profile_id=2)

    pediatric_advisory = generate_health_advisory(child_records, child_bms, child_rems, child, lang="en")
    assert any("Vaccine" in ins["title"] or "Dental" in ins["title"] for ins in pediatric_advisory["insights"])

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
