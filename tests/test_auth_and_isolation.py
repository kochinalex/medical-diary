import os
import sys
import json
import pytest
from starlette.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import app
from src.database import init_db, get_profiles, get_all_records
from src.auth import hash_password, verify_password, create_session_token, verify_session_token

init_db()

def test_password_hashing():
    pwd = "superSecretPassword123"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert "$" in hashed
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongPassword", hashed) is False

def test_session_token():
    user_id = 42
    token = create_session_token(user_id)
    verified_id = verify_session_token(token)
    assert verified_id == user_id
    assert verify_session_token("invalid:token:format") is None
    assert verify_session_token("42:12345:fakesignature") is None

def test_unauthenticated_guard():
    unauth_client = TestClient(app, follow_redirects=False)
    # Visiting home page should redirect to /login
    res = unauth_client.get("/")
    assert res.status_code == 303
    assert res.headers["location"] == "/login"

    # Visiting protected API should return 401
    api_res = unauth_client.get("/api/export")
    assert api_res.status_code == 401

def test_user_registration_and_login():
    client = TestClient(app, follow_redirects=False)
    import time
    unique_email = f"user_{int(time.time() * 1000)}@test.com"

    # Register
    reg_res = client.post(
        "/register",
        data={
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Test User"
        }
    )
    assert reg_res.status_code == 303
    assert "session_token" in reg_res.cookies

    # Duplicate registration should return error banner
    dup_res = client.post(
        "/register",
        data={
            "email": unique_email,
            "password": "Password123!",
            "full_name": "Duplicate"
        }
    )
    assert dup_res.status_code == 200
    assert "already exists" in dup_res.text or "уже зарегистрирован" in dup_res.text

def test_strict_user_data_isolation():
    # Client A
    client_a = TestClient(app)
    import time
    email_a = f"alice_{int(time.time() * 1000)}@test.com"
    client_a.post("/register", data={"email": email_a, "password": "SecretAlice123!", "full_name": "Alice"})
    # Alice accesses home to initialize default profile
    client_a.get("/")
    profiles_a = client_a.get("/api/export").json()["profiles"]
    assert len(profiles_a) >= 1
    alice_pid = profiles_a[0]["id"]

    # Alice creates a confidential medical record
    rec_res = client_a.post(
        "/api/records",
        data={
            "profile_id": alice_pid,
            "category": "sickness",
            "title": "Alice Confidential Condition",
            "event_date": "2026-10-25",
            "notes": "Top secret medical note"
        }
    )
    assert rec_res.status_code == 200

    # Client B
    client_b = TestClient(app)
    email_b = f"bob_{int(time.time() * 1000)}@test.com"
    client_b.post("/register", data={"email": email_b, "password": "SecretBob123!", "full_name": "Bob"})
    client_b.get("/")

    # Bob inspects his data
    export_b = client_b.get("/api/export").json()

    # Bob MUST NOT see Alice's profile
    bob_profile_names = [p["name"] for p in export_b["profiles"]]
    assert "Alice" not in bob_profile_names

    # Bob MUST NOT see Alice's confidential condition
    bob_record_titles = [r["title"] for r in export_b["records"]]
    assert "Alice Confidential Condition" not in bob_record_titles

    # Bob attempts to delete Alice's record (should not delete)
    export_a = client_a.get("/api/export").json()
    alice_rec = [r for r in export_a["records"] if r["title"] == "Alice Confidential Condition"][0]
    alice_rec_id = alice_rec["id"]

    del_attempt = client_b.delete(f"/api/records/{alice_rec_id}")
    assert del_attempt.status_code == 200  # API returns ok but record was not Bob's

    # Verify Alice's record still exists
    export_a_after = client_a.get("/api/export").json()
    assert any(r["id"] == alice_rec_id for r in export_a_after["records"])

def test_data_export_and_import():
    # User 1 exports data
    client_exp = TestClient(app)
    import time
    email_exp = f"exporter_{int(time.time() * 1000)}@test.com"
    client_exp.post("/register", data={"email": email_exp, "password": "Pass12345!", "full_name": "Exporter"})
    client_exp.get("/")
    profiles = client_exp.get("/api/export").json()["profiles"]
    pid = profiles[0]["id"]

    client_exp.post(
        "/api/records",
        data={
            "profile_id": pid,
            "category": "visit",
            "title": "Cardiology Consultation",
            "event_date": "2026-10-15",
            "provider": "Dr. Smith",
            "facility": "Heart Center",
            "notes": "Healthy rhythm"
        }
    )

    export_payload = client_exp.get("/api/export").json()

    # User 2 imports User 1's backup
    client_imp = TestClient(app)
    email_imp = f"importer_{int(time.time() * 1000)}@test.com"
    client_imp.post("/register", data={"email": email_imp, "password": "Pass12345!", "full_name": "Importer"})
    client_imp.get("/")

    # Upload backup JSON
    json_bytes = json.dumps(export_payload).encode("utf-8")
    import_res = client_imp.post(
        "/api/import",
        files={"file": ("backup.json", json_bytes, "application/json")}
    )
    assert import_res.status_code == 200
    import_data = import_res.json()
    assert import_data["status"] == "success"
    assert import_data["counts"]["records"] >= 1

    # Verify importer now has the records under their own account
    imp_records = client_imp.get("/api/export").json()["records"]
    assert any(r["title"] == "Cardiology Consultation" for r in imp_records)
