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

    # 1. Profiles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

    # Migrations for existing databases
    cursor.execute("PRAGMA table_info(records)")
    record_cols = [c[1] for c in cursor.fetchall()]
    if "profile_id" not in record_cols:
        cursor.execute("ALTER TABLE records ADD COLUMN profile_id INTEGER DEFAULT 1")

    cursor.execute("PRAGMA table_info(biomarkers)")
    bm_cols = [c[1] for c in cursor.fetchall()]
    if "profile_id" not in bm_cols:
        cursor.execute("ALTER TABLE biomarkers ADD COLUMN profile_id INTEGER DEFAULT 1")

    cursor.execute("PRAGMA table_info(reminders)")
    rem_cols = [c[1] for c in cursor.fetchall()]
    if "profile_id" not in rem_cols:
        cursor.execute("ALTER TABLE reminders ADD COLUMN profile_id INTEGER DEFAULT 1")

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
    INSERT INTO profiles (id, name, role, birth_date, gender, blood_type, allergies, chronic_conditions, current_medications, emergency_contact, avatar_color, is_default)
    VALUES (1, ?, 'Mother', ?, 'female', ?, ?, ?, ?, ?, '#0d9488', 1)
    """, (name, dob, blood, allergies, conditions, meds, contact))

    # Profile 2: Child (Leo, 4 y.o.)
    cursor.execute("""
    INSERT INTO profiles (id, name, role, birth_date, gender, blood_type, allergies, chronic_conditions, current_medications, emergency_contact, avatar_color, is_default)
    VALUES (2, 'Leo Kochina', 'Child', '2022-06-10', 'male', 'A+', 'Peanuts (mild hives)', 'None', 'Multivitamin syrup', 'Mother (Alex): +1 (555) 019-2834', '#3b82f6', 0)
    """)

    # Update existing records to profile 1
    cursor.execute("UPDATE records SET profile_id = 1 WHERE profile_id IS NULL OR profile_id = 0")
    cursor.execute("UPDATE biomarkers SET profile_id = 1 WHERE profile_id IS NULL OR profile_id = 0")
    cursor.execute("UPDATE reminders SET profile_id = 1 WHERE profile_id IS NULL OR profile_id = 0")

    # Seed initial pediatric records for Leo (Profile 2)
    cursor.execute("""
    INSERT INTO records (profile_id, category, title, event_date, provider, facility, notes)
    VALUES (2, 'visit', '4-Year Well-Child Pediatric Exam', '2026-06-15', 'Dr. Anya Petrović', 'City Pediatric Clinic', 'Height: 104 cm (60th percentile), Weight: 17 kg (55th percentile). Vision screening passed. Recommended preschool MMR booster.')
    """)
    rec_leo_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO biomarkers (profile_id, record_id, name, value, unit, ref_min, ref_max, flag, test_date)
    VALUES (2, ?, 'Hemoglobin', 12.8, 'g/dL', 11.5, 14.5, 'NORMAL', '2026-06-15')
    """, (rec_leo_id,))

    cursor.execute("""
    INSERT INTO records (profile_id, category, title, event_date, provider, facility, notes)
    VALUES (2, 'sickness', 'Viral Gastroenteritis Episode', '2026-03-12', 'Dr. Anya Petrović', 'Urgent Care Center', 'Low fever, mild dehydration. Prescribed oral rehydration salts (ORS) and light diet. Fully resolved in 3 days.')
    """)

    # Leo's Reminders
    cursor.execute("""
    INSERT INTO reminders (profile_id, title, category, due_date, frequency, completed, notes)
    VALUES (2, 'Preschool MMR (Measles/Mumps/Rubella) Booster', 'vaccine', '2026-11-15', 'once', 0, 'Required 4-year booster before kindergarten registration.')
    """)
    cursor.execute("""
    INSERT INTO reminders (profile_id, title, category, due_date, frequency, completed, notes)
    VALUES (2, 'Pediatric Dental Cleaning & Fluoride Check', 'screening', '2026-12-05', '6_months', 0, 'Routine dental examination and fluoride varnish.')
    """)

# Profile CRUD
def get_profiles() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles ORDER BY is_default DESC, id ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_profile(profile_id: int) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def add_profile(name: str, role: str, birth_date: str = "", gender: str = "other",
                blood_type: str = "", allergies: str = "", chronic_conditions: str = "",
                current_medications: str = "", emergency_contact: str = "",
                avatar_color: str = "#0d9488") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO profiles (name, role, birth_date, gender, blood_type, allergies, chronic_conditions,
                         current_medications, emergency_contact, avatar_color, is_default)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (name, role, birth_date, gender, blood_type, allergies, chronic_conditions, current_medications, emergency_contact, avatar_color))
    p_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return p_id

def update_profile(profile_id: int, data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE profiles SET
        name = ?, role = ?, birth_date = ?, gender = ?, blood_type = ?, allergies = ?,
        chronic_conditions = ?, current_medications = ?, emergency_contact = ?, avatar_color = ?
    WHERE id = ?
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
        profile_id
    ))
    conn.commit()
    conn.close()

def delete_profile(profile_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM profiles")
    if cursor.fetchone()[0] <= 1:
        conn.close()
        return False  # Cannot delete the only profile
    cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
    cursor.execute("DELETE FROM records WHERE profile_id = ?", (profile_id,))
    cursor.execute("DELETE FROM biomarkers WHERE profile_id = ?", (profile_id,))
    cursor.execute("DELETE FROM reminders WHERE profile_id = ?", (profile_id,))
    conn.commit()
    conn.close()
    return True

def delete_record(record_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    if row and row["file_path"] and os.path.exists(row["file_path"]):
        try:
            os.remove(row["file_path"])
        except Exception:
            pass
    cursor.execute("DELETE FROM biomarkers WHERE record_id = ?", (record_id,))
    cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return True

def delete_reminder(reminder_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()
    return True

def clear_all_records(profile_id: Optional[int] = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    if profile_id and profile_id > 0:
        cursor.execute("DELETE FROM biomarkers WHERE profile_id = ?", (profile_id,))
        cursor.execute("DELETE FROM records WHERE profile_id = ?", (profile_id,))
        cursor.execute("DELETE FROM reminders WHERE profile_id = ?", (profile_id,))
    else:
        cursor.execute("DELETE FROM biomarkers")
        cursor.execute("DELETE FROM records")
        cursor.execute("DELETE FROM reminders")
    conn.commit()
    conn.close()
    return True

# Record CRUD with profile filtering
def add_record(category: str, title: str, event_date: str, profile_id: int = 1,
               provider: str = "", facility: str = "", notes: str = "", file_path: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO records (profile_id, category, title, event_date, provider, facility, notes, file_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (profile_id, category, title, event_date, provider, facility, notes, file_path))
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id

def add_biomarker(record_id: int, name: str, value: float, unit: str,
                  ref_min: Optional[float], ref_max: Optional[float],
                  test_date: str, profile_id: int = 1):
    flag = 'NORMAL'
    if ref_min is not None and value < ref_min:
        flag = 'LOW'
    elif ref_max is not None and value > ref_max:
        flag = 'HIGH'

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO biomarkers (profile_id, record_id, name, value, unit, ref_min, ref_max, flag, test_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (profile_id, record_id, name, value, unit, ref_min, ref_max, flag, test_date))
    conn.commit()
    conn.close()

def get_all_records(category: Optional[str] = None, profile_id: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT r.*, p.name as member_name, p.role as member_role, p.avatar_color as member_color
    FROM records r
    LEFT JOIN profiles p ON r.profile_id = p.id
    WHERE 1=1
    """
    params = []
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
        cursor.execute("SELECT * FROM biomarkers WHERE record_id = ?", (r["id"],))
        r["biomarkers"] = [dict(b) for b in cursor.fetchall()]

    conn.close()
    return rows

def get_biomarker_history(profile_id: Optional[int] = None) -> Dict[str, List[Dict[str, Any]]]:
    conn = get_connection()
    cursor = conn.cursor()
    if profile_id and profile_id > 0:
        cursor.execute("SELECT * FROM biomarkers WHERE profile_id = ? ORDER BY test_date ASC", (profile_id,))
    else:
        cursor.execute("SELECT * FROM biomarkers ORDER BY test_date ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    grouped = {}
    for r in rows:
        b_name = r["name"]
        if b_name not in grouped:
            grouped[b_name] = []
        grouped[b_name].append(r)
    return grouped

def get_all_reminders(profile_id: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT rem.*, p.name as member_name, p.role as member_role, p.avatar_color as member_color
    FROM reminders rem
    LEFT JOIN profiles p ON rem.profile_id = p.id
    WHERE 1=1
    """
    params = []
    if profile_id and profile_id > 0:
        query += " AND rem.profile_id = ?"
        params.append(profile_id)

    query += " ORDER BY rem.completed ASC, rem.due_date ASC"
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def toggle_reminder(reminder_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE reminders SET completed = CASE WHEN completed = 1 THEN 0 ELSE 1 END WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()
    return True

def add_reminder(title: str, category: str, due_date: str, profile_id: int = 1,
                 frequency: str = "once", notes: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO reminders (profile_id, title, category, due_date, frequency, completed, notes)
    VALUES (?, ?, ?, ?, ?, 0, ?)
    """, (profile_id, title, category, due_date, frequency, notes))
    rem_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rem_id
