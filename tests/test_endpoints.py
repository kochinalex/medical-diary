import os
import sys
import pytest
from starlette.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import app
from src.database import get_profile

client = TestClient(app)

def test_home_page_languages():
    for lang in ["en", "ru", "sr"]:
        response = client.get(f"/?lang={lang}")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Medical Diary" in response.text or "Медицинский Дневник" in response.text or "Medicinski Dnevnik" in response.text

def test_update_profile_endpoint():
    response = client.post(
        "/api/profiles/1",
        data={
            "name": "Alex Kochina",
            "role": "Mother",
            "birth_date": "1990-05-14",
            "gender": "female",
            "blood_type": "A+",
            "allergies": "Penicillin (rash), Pollen",
            "chronic_conditions": "Mild Seasonal Asthma",
            "current_medications": "Vitamin D3 (2000 IU), Iron (25mg)",
            "emergency_contact": "Partner: +1 (555) 019-2834",
            "avatar_color": "#0d9488"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

    prof = get_profile(1)
    assert prof["name"] == "Alex Kochina"
    assert prof["allergies"] == "Penicillin (rash), Pollen"

def test_export_endpoint():
    response = client.get("/api/export")
    assert response.status_code == 200
    data = response.json()
    assert "profiles" in data
    assert "records" in data
    assert "reminders" in data

def test_record_and_reminder_crud_endpoints():
    # 1. Create a temporary record
    res = client.post(
        "/api/records",
        data={
            "profile_id": 1,
            "category": "comment",
            "title": "Temporary Test Note",
            "event_date": "2026-10-20",
            "notes": "Testing record removal"
        }
    )
    assert res.status_code == 200

    # Find the created record
    export = client.get("/api/export?profile_id=1").json()
    created = [r for r in export["records"] if r["title"] == "Temporary Test Note"]
    assert len(created) > 0
    rec_id = created[0]["id"]

    # Delete the record
    del_res = client.delete(f"/api/records/{rec_id}")
    assert del_res.status_code == 200

    # Verify deleted
    export_after = client.get("/api/export?profile_id=1").json()
    assert not any(r["id"] == rec_id for r in export_after["records"])
