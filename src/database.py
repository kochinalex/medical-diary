import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "medical_diary.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 0. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    # 1. Profiles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        birth_date TEXT,
        gender TEXT,
        blood_type TEXT,
        allergies TEXT,
        chronic_conditions TEXT,
        current_medications TEXT,
        emergency_contact TEXT,
        avatar_color TEXT DEFAULT '#0d9488',
        is_default INTEGER DEFAULT 0
    )
    """)

    # 2. Records Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        profile_id INTEGER DEFAULT 1,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        event_date TEXT NOT NULL,
        provider TEXT,
        facility TEXT,
        notes TEXT,
        file_path TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (profile_id) REFERENCES profiles (id) ON DELETE CASCADE
    )
    """)

    # 3. Biomarkers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS biomarkers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        profile_id INTEGER DEFAULT 1,
        record_id INTEGER,
        name TEXT NOT NULL,
        value REAL NOT NULL,
        unit TEXT NOT NULL,
        ref_min REAL,
        ref_max REAL,
        flag TEXT,
        test_date TEXT NOT NULL,
        FOREIGN KEY (record_id) REFERENCES records (id) ON DELETE CASCADE,
        FOREIGN KEY (profile_id) REFERENCES profiles (id) ON DELETE CASCADE
    )
    """)

    # 4. Reminders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        profile_id INTEGER DEFAULT 1,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        due_date TEXT NOT NULL,
        frequency TEXT,
        completed INTEGER DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (profile_id) REFERENCES profiles (id) ON DELETE CASCADE
    )
    """)

    conn.commit()

    # Migrations for existing databases: ensure user_id & profile_id columns exist
    for tbl in ["records", "biomarkers", "reminders"]:
        cursor.execute(f"PRAGMA table_info({tbl})")
        cols = [c[1] for c in cursor.fetchall()]
        if "profile_id" not in cols:
            cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN profile_id INTEGER DEFAULT 1")
        if "user_id" not in cols:
            cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN user_id INTEGER DEFAULT 1")

    cursor.execute("PRAGMA table_info(profiles)")
    prof_cols = [c[1] for c in cursor.fetchall()]
    if "user_id" not in prof_cols:
        cursor.execute("ALTER TABLE profiles ADD COLUMN user_id INTEGER DEFAULT 1")

    conn.commit()

    # Migrate or create default primary user (User 1)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        from .auth import hash_password
        default_pw = hash_password("admin123")
        cursor.execute("""
        INSERT INTO users (id, email, password_hash, full_name)
        VALUES (1, 'alex@medical.diary', ?, 'Alex Kochina')
        """, (default_pw,))
        cursor.execute("UPDATE profiles SET user_id = 1 WHERE user_id IS NULL OR user_id = 0")
        cursor.execute("UPDATE records SET user_id = 1 WHERE user_id IS NULL OR user_id = 0")
        cursor.execute("UPDATE biomarkers SET user_id = 1 WHERE user_id IS NULL OR user_id = 0")
        cursor.execute("UPDATE reminders SET user_id = 1 WHERE user_id IS NULL OR user_id = 0")
        conn.commit()

    # Seed Profiles if empty
    cursor.execute("SELECT COUNT(*) FROM profiles")
    if cursor.fetchone()[0] == 0:
        seed_profiles_and_family(cursor)
        conn.commit()

    conn.close()

def seed_profiles_and_family(cursor):
    # Check if legacy single profile exists to copy over
    legacy_profile = None
    try:
        cursor.execute("SELECT * FROM profile WHERE id = 1")
        row = cursor.fetchone()
        if row:
            legacy_profile = dict(row)
    except Exception:
        pass

    # Profile 1: Primary (Mother / Self)
    name = legacy_profile["name"] if legacy_profile else "Alex Kochina"
    dob = legacy_profile["birth_date"] if legacy_profile else "1990-05-14"
    blood = legacy_profile["blood_type"] if legacy_profile else "A+"
    allergies = legacy_profile["allergies"] if legacy_profile else "Penicillin (rash), Pollen"
    conditions = legacy_profile["chronic_conditions"] if legacy_profile else "Mild Seasonal Asthma"
    meds = legacy_profile["current_medications"] if legacy_profile else "Vitamin D3 (2000 IU), Iron (25mg)"
    contact = legacy_profile["emergency_contact"] if legacy_profile else "Partner: +1 (555) 019-2834"

    cursor.execute("""
    INSERT INTO profiles (id, user_id, name, role, birth_date, gender, blood_type, allergies, chronic_conditions, current_medications, emergency_contact, avatar_color, is_default)
    VALUES (1, 1, ?, 'Mother', ?, 'female', ?, ?, ?, ?, ?, '#0d9488', 1)
    """, (name, dob, blood, allergies, conditions, meds, contact))

    # Profile 2: Child (Leo / Alisa)
    cursor.execute("""
    INSERT INTO profiles (id, user_id, name, role, birth_date, gender, blood_type, allergies, chronic_conditions, current_medications, emergency_contact, avatar_color, is_default)
    VALUES (2, 1, 'Leo Kochina', 'Child', '2022-06-10', 'male', 'A+', 'Peanuts (mild hives)', 'None', 'Multivitamin syrup', 'Mother (Alex): +1 (555) 019-2834', '#3b82f6', 0)
    """)

    # Update existing records to profile 1 and user 1
    cursor.execute("UPDATE records SET profile_id = 1, user_id = 1 WHERE profile_id IS NULL OR profile_id = 0")
    cursor.execute("UPDATE biomarkers SET profile_id = 1, user_id = 1 WHERE profile_id IS NULL OR profile_id = 0")
    cursor.execute("UPDATE reminders SET profile_id = 1, user_id = 1 WHERE profile_id IS NULL OR profile_id = 0")

    # Seed initial pediatric records for Leo (Profile 2)
    cursor.execute("""
    INSERT INTO records (user_id, profile_id, category, title, event_date, provider, facility, notes)
    VALUES (1, 2, 'visit', '4-Year Well-Child Pediatric Exam', '2026-06-15', 'Dr. Anya Petrović', 'City Pediatric Clinic', 'Height: 104 cm (60th percentile), Weight: 17 kg (55th percentile). Vision screening passed. Recommended preschool MMR booster.')
    """)
    rec_leo_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO biomarkers (user_id, profile_id, record_id, name, value, unit, ref_min, ref_max, flag, test_date)
    VALUES (1, 2, ?, 'Hemoglobin', 12.8, 'g/dL', 11.5, 14.5, 'NORMAL', '2026-06-15')
    """, (rec_leo_id,))

    cursor.execute("""
    INSERT INTO records (user_id, profile_id, category, title, event_date, provider, facility, notes)
    VALUES (1, 2, 'sickness', 'Viral Gastroenteritis Episode', '2026-03-12', 'Dr. Anya Petrović', 'Urgent Care Center', 'Low fever, mild dehydration. Prescribed oral rehydration salts (ORS) and light diet. Fully resolved in 3 days.')
    """)

    cursor.execute("""
    INSERT INTO reminders (user_id, profile_id, title, category, due_date, frequency, completed, notes)
    VALUES (1, 2, 'Preschool MMR (Measles/Mumps/Rubella) Booster', 'vaccine', '2026-11-15', 'once', 0, 'Required 4-year booster before kindergarten registration.')
    """)
    cursor.execute("""
    INSERT INTO reminders (user_id, profile_id, title, category, due_date, frequency, completed, notes)
    VALUES (1, 2, 'Pediatric Dental Cleaning & Fluoride Check', 'screening', '2026-12-05', '6_months', 0, 'Routine dental examination and fluoride varnish.')
    """)

# User Accounts
def create_user(email: str, password_hash: str, full_name: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO users (email, password_hash, full_name)
    VALUES (?, ?, ?)
    """, (email.lower().strip(), password_hash, full_name.strip()))
    u_id = cursor.lastrowid

    # Create an initial default profile for this new user
    profile_name = full_name.strip() if full_name.strip() else email.split("@")[0].capitalize()
    cursor.execute("""
    INSERT INTO profiles (user_id, name, role, is_default, avatar_color)
    VALUES (?, ?, 'Self', 1, '#0d9488')
    """, (u_id, profile_name))

    conn.commit()
    conn.close()
    return u_id

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE lower(email) = ?", (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Profile CRUD
def get_profiles(user_id: int = 1) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE user_id = ? ORDER BY is_default DESC, id ASC", (user_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_profile(profile_id: int, user_id: int = 1) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE id = ? AND user_id = ?", (profile_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def add_profile(name: str, role: str, birth_date: str = "", gender: str = "other",
                blood_type: str = "", allergies: str = "", chronic_conditions: str = "",
                current_medications: str = "", emergency_contact: str = "",
                avatar_color: str = "#0d9488", user_id: int = 1) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO profiles (user_id, name, role, birth_date, gender, blood_type, allergies, chronic_conditions,
                         current_medications, emergency_contact, avatar_color, is_default)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (user_id, name, role, birth_date, gender, blood_type, allergies, chronic_conditions, current_medications, emergency_contact, avatar_color))
    p_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return p_id

def update_profile(profile_id: int, data: Dict[str, Any], user_id: int = 1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE profiles SET
        name = ?, role = ?, birth_date = ?, gender = ?, blood_type = ?, allergies = ?,
        chronic_conditions = ?, current_medications = ?, emergency_contact = ?, avatar_color = ?
    WHERE id = ? AND user_id = ?
    """, (
        data.get("name", ""),
        data.get("role", "Self"),
        data.get("birth_date", ""),
        data.get("gender", "other"),
        data.get("blood_type", ""),
        data.get("allergies", ""),
        data.get("chronic_conditions", ""),
        data.get("current_medications", ""),
        data.get("emergency_contact", ""),
        data.get("avatar_color", "#0d9488"),
        profile_id,
        user_id
    ))
    conn.commit()
    conn.close()

def delete_profile(profile_id: int, user_id: int = 1) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM profiles WHERE user_id = ?", (user_id,))
    if cursor.fetchone()[0] <= 1:
        conn.close()
        return False  # Cannot delete the only profile
    cursor.execute("DELETE FROM profiles WHERE id = ? AND user_id = ?", (profile_id, user_id))
    cursor.execute("DELETE FROM records WHERE profile_id = ? AND user_id = ?", (profile_id, user_id))
    cursor.execute("DELETE FROM biomarkers WHERE profile_id = ? AND user_id = ?", (profile_id, user_id))
    cursor.execute("DELETE FROM reminders WHERE profile_id = ? AND user_id = ?", (profile_id, user_id))
    conn.commit()
    conn.close()
    return True

def delete_record(record_id: int, user_id: int = 1) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM records WHERE id = ? AND user_id = ?", (record_id, user_id))
    row = cursor.fetchone()
    if row and row["file_path"] and os.path.exists(row["file_path"]):
        try:
            os.remove(row["file_path"])
        except Exception:
            pass
    cursor.execute("DELETE FROM biomarkers WHERE record_id = ? AND user_id = ?", (record_id, user_id))
    cursor.execute("DELETE FROM records WHERE id = ? AND user_id = ?", (record_id, user_id))
    conn.commit()
    conn.close()
    return True

def delete_reminder(reminder_id: int, user_id: int = 1) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
    conn.commit()
    conn.close()
    return True

def clear_all_records(profile_id: Optional[int] = None, user_id: int = 1) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    if profile_id and profile_id > 0:
        cursor.execute("DELETE FROM biomarkers WHERE profile_id = ? AND user_id = ?", (profile_id, user_id))
        cursor.execute("DELETE FROM records WHERE profile_id = ? AND user_id = ?", (profile_id, user_id))
        cursor.execute("DELETE FROM reminders WHERE profile_id = ? AND user_id = ?", (profile_id, user_id))
    else:
        cursor.execute("DELETE FROM biomarkers WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM records WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM reminders WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

# Record CRUD with profile filtering
def add_record(category: str, title: str, event_date: str, profile_id: int = 1,
               provider: str = "", facility: str = "", notes: str = "", file_path: str = "", user_id: int = 1) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO records (user_id, profile_id, category, title, event_date, provider, facility, notes, file_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, profile_id, category, title, event_date, provider, facility, notes, file_path))
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id

def add_biomarker(record_id: int, name: str, value: float, unit: str,
                  ref_min: Optional[float], ref_max: Optional[float],
                  test_date: str, profile_id: int = 1, user_id: int = 1):
    flag = 'NORMAL'
    if ref_min is not None and value < ref_min:
        flag = 'LOW'
    elif ref_max is not None and value > ref_max:
        flag = 'HIGH'

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO biomarkers (user_id, profile_id, record_id, name, value, unit, ref_min, ref_max, flag, test_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, profile_id, record_id, name, value, unit, ref_min, ref_max, flag, test_date))
    conn.commit()
    conn.close()

def get_all_records(category: Optional[str] = None, profile_id: Optional[int] = None, user_id: int = 1) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT r.*, p.name as member_name, p.role as member_role, p.avatar_color as member_color
    FROM records r
    LEFT JOIN profiles p ON r.profile_id = p.id
    WHERE r.user_id = ?
    """
    params = [user_id]
    if profile_id and profile_id > 0:
        query += " AND r.profile_id = ?"
        params.append(profile_id)
    if category and category != 'all':
        query += " AND r.category = ?"
        params.append(category)

    query += " ORDER BY r.event_date DESC"
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]

    for r in rows:
        cursor.execute("SELECT * FROM biomarkers WHERE record_id = ? AND user_id = ?", (r["id"], user_id))
        r["biomarkers"] = [dict(b) for b in cursor.fetchall()]

    conn.close()
    return rows

def get_biomarker_history(profile_id: Optional[int] = None, user_id: int = 1) -> Dict[str, List[Dict[str, Any]]]:
    conn = get_connection()
    cursor = conn.cursor()
    if profile_id and profile_id > 0:
        cursor.execute("SELECT * FROM biomarkers WHERE user_id = ? AND profile_id = ? ORDER BY test_date ASC", (user_id, profile_id))
    else:
        cursor.execute("SELECT * FROM biomarkers WHERE user_id = ? ORDER BY test_date ASC", (user_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    grouped = {}
    for r in rows:
        b_name = r["name"]
        if b_name not in grouped:
            grouped[b_name] = []
        grouped[b_name].append(r)
    return grouped

def get_all_reminders(profile_id: Optional[int] = None, user_id: int = 1) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT rem.*, p.name as member_name, p.role as member_role, p.avatar_color as member_color
    FROM reminders rem
    LEFT JOIN profiles p ON rem.profile_id = p.id
    WHERE rem.user_id = ?
    """
    params = [user_id]
    if profile_id and profile_id > 0:
        query += " AND rem.profile_id = ?"
        params.append(profile_id)

    query += " ORDER BY rem.completed ASC, rem.due_date ASC"
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def toggle_reminder(reminder_id: int, user_id: int = 1) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE reminders SET completed = CASE WHEN completed = 1 THEN 0 ELSE 1 END WHERE id = ? AND user_id = ?", (reminder_id, user_id))
    conn.commit()
    conn.close()
    return True

def add_reminder(title: str, category: str, due_date: str, profile_id: int = 1,
                 frequency: str = "once", notes: str = "", user_id: int = 1) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO reminders (user_id, profile_id, title, category, due_date, frequency, completed, notes)
    VALUES (?, ?, ?, ?, ?, 0, ?)
    """, (user_id, profile_id, title, category, due_date, frequency, notes))
    rem_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rem_id

def import_user_health_data(user_id: int, data: Dict[str, Any]) -> Dict[str, int]:
    """
    Imports exported medical diary data (profiles, records, biomarkers, reminders)
    into the specified user account, safely remapping profile IDs.
    """
    conn = get_connection()
    cursor = conn.cursor()

    counts = {"profiles": 0, "records": 0, "biomarkers": 0, "reminders": 0}

    # 1. Map old profile id -> new profile id
    profile_id_map = {}

    cursor.execute("SELECT id, name FROM profiles WHERE user_id = ?", (user_id,))
    existing_profiles = {row["name"].strip().lower(): row["id"] for row in cursor.fetchall()}

    incoming_profiles = data.get("profiles", [])
    for p in incoming_profiles:
        old_id = p.get("id")
        p_name = p.get("name", "").strip().lower()
        if p_name in existing_profiles:
            profile_id_map[old_id] = existing_profiles[p_name]
        else:
            cursor.execute("""
            INSERT INTO profiles (user_id, name, role, birth_date, gender, blood_type,
                                 allergies, chronic_conditions, current_medications,
                                 emergency_contact, avatar_color, is_default)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                user_id, p.get("name", "Family Member"), p.get("role", "Other"),
                p.get("birth_date", ""), p.get("gender", "other"), p.get("blood_type", ""),
                p.get("allergies", ""), p.get("chronic_conditions", ""),
                p.get("current_medications", ""), p.get("emergency_contact", ""),
                p.get("avatar_color", "#0d9488")
            ))
            new_p_id = cursor.lastrowid
            profile_id_map[old_id] = new_p_id
            existing_profiles[p_name] = new_p_id
            counts["profiles"] += 1

    cursor.execute("SELECT id FROM profiles WHERE user_id = ? ORDER BY is_default DESC LIMIT 1", (user_id,))
    fallback_row = cursor.fetchone()
    default_pid = fallback_row["id"] if fallback_row else 1

    # 2. Insert records & biomarkers
    incoming_records = data.get("records", [])
    for r in incoming_records:
        old_pid = r.get("profile_id")
        target_pid = profile_id_map.get(old_pid, default_pid)

        cursor.execute("""
        INSERT INTO records (user_id, profile_id, category, title, event_date, provider, facility, notes, file_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, target_pid, r.get("category", "comment"), r.get("title", "Imported Record"),
            r.get("event_date", datetime.now().strftime("%Y-%m-%d")),
            r.get("provider", ""), r.get("facility", ""), r.get("notes", ""), r.get("file_path", "")
        ))
        new_rec_id = cursor.lastrowid
        counts["records"] += 1

        for b in r.get("biomarkers", []):
            cursor.execute("""
            INSERT INTO biomarkers (user_id, profile_id, record_id, name, value, unit, ref_min, ref_max, flag, test_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, target_pid, new_rec_id, b.get("name", ""), b.get("value", 0.0),
                b.get("unit", ""), b.get("ref_min"), b.get("ref_max"), b.get("flag", "NORMAL"),
                b.get("test_date", r.get("event_date", datetime.now().strftime("%Y-%m-%d")))
            ))
            counts["biomarkers"] += 1

    # 3. Insert reminders
    incoming_reminders = data.get("reminders", [])
    for rem in incoming_reminders:
        old_pid = rem.get("profile_id")
        target_pid = profile_id_map.get(old_pid, default_pid)
        cursor.execute("""
        INSERT INTO reminders (user_id, profile_id, title, category, due_date, frequency, completed, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, target_pid, rem.get("title", "Imported Reminder"),
            rem.get("category", "screening"), rem.get("due_date", datetime.now().strftime("%Y-%m-%d")),
            rem.get("frequency", "once"), rem.get("completed", 0), rem.get("notes", "")
        ))
        counts["reminders"] += 1

    conn.commit()
    conn.close()
    return counts
