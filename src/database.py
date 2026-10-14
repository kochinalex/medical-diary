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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        event_date TEXT NOT NULL,
        provider TEXT,
        facility TEXT,
        notes TEXT,
        file_path TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS biomarkers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER,
        name TEXT NOT NULL,
        value REAL NOT NULL,
        unit TEXT NOT NULL,
        ref_min REAL,
        ref_max REAL,
        flag TEXT,
        test_date TEXT NOT NULL,
        FOREIGN KEY (record_id) REFERENCES records (id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        due_date TEXT NOT NULL,
        frequency TEXT,
        completed INTEGER DEFAULT 0,
        notes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profile (
        id INTEGER PRIMARY KEY,
        name TEXT DEFAULT 'Alex Kochina',
        birth_date TEXT DEFAULT '1990-05-14',
        blood_type TEXT DEFAULT 'A+',
        allergies TEXT DEFAULT 'Penicillin (mild rash), Pollen',
        chronic_conditions TEXT DEFAULT 'Mild Seasonal Asthma',
        current_medications TEXT DEFAULT 'Vitamin D3 (2000 IU daily), Iron Bisglycinate (25mg)',
        emergency_contact TEXT DEFAULT 'Partner: +1 (555) 019-2834'
    )
    """)

    conn.commit()

    # Seed if records table is empty
    cursor.execute("SELECT COUNT(*) FROM records")
    if cursor.fetchone()[0] == 0:
        seed_sample_data(cursor)
        conn.commit()

    conn.close()

def seed_sample_data(cursor):
    # Insert profile if not exists
    cursor.execute("SELECT COUNT(*) FROM profile")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO profile (id, name, birth_date, blood_type, allergies, chronic_conditions, current_medications, emergency_contact)
        VALUES (1, 'Alex Kochina', '1990-05-14', 'A+', 'Penicillin (mild rash), Pollen', 'Mild Seasonal Asthma', 'Vitamin D3 (2000 IU daily), Iron Bisglycinate (25mg)', 'Emergency Contact: +1 (555) 019-2834')
        """)

    # 1. Past Blood Test (6 months ago)
    cursor.execute("""
    INSERT INTO records (category, title, event_date, provider, facility, notes)
    VALUES ('test_result', 'Comprehensive Metabolic & Iron Panel (Spring)', '2026-04-10', 'Dr. Elena Rostova', 'Central Diagnostics Lab', 'Routine annual blood work. Mild microcytic anemia indications noted.')
    """)
    rec1_id = cursor.lastrowid

    cursor.execute("INSERT INTO biomarkers (record_id, name, value, unit, ref_min, ref_max, flag, test_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (rec1_id, 'Ferritin', 14.0, 'ng/mL', 24.0, 336.0, 'LOW', '2026-04-10'))
    cursor.execute("INSERT INTO biomarkers (record_id, name, value, unit, ref_min, ref_max, flag, test_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (rec1_id, 'Vitamin D', 18.5, 'ng/mL', 30.0, 100.0, 'LOW', '2026-04-10'))
    cursor.execute("INSERT INTO biomarkers (record_id, name, value, unit, ref_min, ref_max, flag, test_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (rec1_id, 'Total Cholesterol', 198.0, 'mg/dL', 125.0, 200.0, 'NORMAL', '2026-04-10'))
    cursor.execute("INSERT INTO biomarkers (record_id, name, value, unit, ref_min, ref_max, flag, test_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (rec1_id, 'Fasting Glucose', 91.0, 'mg/dL', 70.0, 99.0, 'NORMAL', '2026-04-10'))

    # 2. Recent Follow-Up Blood Test (3 weeks ago)
    cursor.execute("""
    INSERT INTO records (category, title, event_date, provider, facility, notes)
    VALUES ('test_result', 'Follow-up Iron & Vitamin Panel (Autumn)', '2026-09-22', 'Dr. Elena Rostova', 'Central Diagnostics Lab', 'Ferritin has started to rise with supplementation but remains below optimal threshold.')
    """)
    rec2_id = cursor.lastrowid

    cursor.execute("INSERT INTO biomarkers (record_id, name, value, unit, ref_min, ref_max, flag, test_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (rec2_id, 'Ferritin', 23.5, 'ng/mL', 24.0, 336.0, 'LOW', '2026-09-22'))
    cursor.execute("INSERT INTO biomarkers (record_id, name, value, unit, ref_min, ref_max, flag, test_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (rec2_id, 'Vitamin D', 28.0, 'ng/mL', 30.0, 100.0, 'LOW', '2026-09-22'))
    cursor.execute("INSERT INTO biomarkers (record_id, name, value, unit, ref_min, ref_max, flag, test_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (rec2_id, 'Total Cholesterol', 188.0, 'mg/dL', 125.0, 200.0, 'NORMAL', '2026-09-22'))
    cursor.execute("INSERT INTO biomarkers (record_id, name, value, unit, ref_min, ref_max, flag, test_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (rec2_id, 'Fasting Glucose', 89.0, 'mg/dL', 70.0, 99.0, 'NORMAL', '2026-09-22'))

    # 3. Doctor Visit
    cursor.execute("""
    INSERT INTO records (category, title, event_date, provider, facility, notes)
    VALUES ('visit', 'Cardiology & Blood Pressure Review', '2026-06-15', 'Dr. Marcus Vance', 'Heart & Health Clinic', 'Patient reports mild occasional palpitations under work stress. ECG normal. Resting BP 118/76 mmHg. Recommended hydration and magnesium.')
    """)

    # 4. Sickness Record
    cursor.execute("""
    INSERT INTO records (category, title, event_date, provider, facility, notes)
    VALUES ('sickness', 'Acute Viral Rhinosinusitis', '2026-02-04', 'Dr. Sarah Lin', 'Urgent Care Center', 'Fever up to 38.4C, sinus congestion, headache. Prescribed nasal saline rinse, ibuprofen as needed. Fully resolved in 6 days.')
    """)

    # 5. Intervention / Procedure
    cursor.execute("""
    INSERT INTO records (category, title, event_date, provider, facility, notes)
    VALUES ('intervention', 'Preventive Dermatological Mole Excision', '2025-11-20', 'Dr. Christian Meyer', 'St. Jude Dermatology', 'Atypical dysplastic nevus removed from upper back margin. Histopathology confirmed benign margins with clear boundary.')
    """)

    # 6. Free text comment / Note
    cursor.execute("""
    INSERT INTO records (category, title, event_date, provider, facility, notes)
    VALUES ('comment', 'Allergy Season Note & Inhaler Refill', '2026-05-02', 'Self-Report', 'Home Log', 'Birch pollen count very high. Started desloratadine 5mg daily. Albuterol inhaler kept on hand, only needed twice after jogging.')
    """)

    # Reminders
    cursor.execute("""
    INSERT INTO reminders (title, category, due_date, frequency, completed, notes)
    VALUES ('Bi-annual Dental Cleaning & Examination', 'screening', '2026-11-05', '6_months', 0, 'Last visit was in May 2026. Routine checkup and tartar removal.')
    """)
    cursor.execute("""
    INSERT INTO reminders (title, category, due_date, frequency, completed, notes)
    VALUES ('Repeat Ferritin & Complete Blood Count (CBC)', 'lab_retest', '2026-12-20', 'once', 0, 'Check progress after 3 full months on iron bisglycinate.')
    """)
    cursor.execute("""
    INSERT INTO reminders (title, category, due_date, frequency, completed, notes)
    VALUES ('Annual Dermatological Full-Body Mole Check', 'screening', '2026-11-20', 'yearly', 0, '12-month follow up after dysplastic mole excision in Nov 2025.')
    """)
    cursor.execute("""
    INSERT INTO reminders (title, category, due_date, frequency, completed, notes)
    VALUES ('Tetanus / Diphtheria / Pertussis Booster (Tdap)', 'vaccine', '2027-04-10', '10_years', 0, 'Due every 10 years. Last administered in 2017.')
    """)

def add_record(category: str, title: str, event_date: str, provider: str = "", facility: str = "", notes: str = "", file_path: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO records (category, title, event_date, provider, facility, notes, file_path)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (category, title, event_date, provider, facility, notes, file_path))
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id

def add_biomarker(record_id: int, name: str, value: float, unit: str, ref_min: Optional[float], ref_max: Optional[float], test_date: str):
    flag = 'NORMAL'
    if ref_min is not None and value < ref_min:
        flag = 'LOW'
    elif ref_max is not None and value > ref_max:
        flag = 'HIGH'

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO biomarkers (record_id, name, value, unit, ref_min, ref_max, flag, test_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (record_id, name, value, unit, ref_min, ref_max, flag, test_date))
    conn.commit()
    conn.close()

def get_all_records(category: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if category and category != 'all':
        cursor.execute("SELECT * FROM records WHERE category = ? ORDER BY event_date DESC", (category,))
    else:
        cursor.execute("SELECT * FROM records ORDER BY event_date DESC")
    rows = [dict(row) for row in cursor.fetchall()]

    for r in rows:
        cursor.execute("SELECT * FROM biomarkers WHERE record_id = ?", (r["id"],))
        r["biomarkers"] = [dict(b) for b in cursor.fetchall()]

    conn.close()
    return rows

def get_biomarker_history() -> Dict[str, List[Dict[str, Any]]]:
    conn = get_connection()
    cursor = conn.cursor()
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

def get_all_reminders() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reminders ORDER BY completed ASC, due_date ASC")
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

def add_reminder(title: str, category: str, due_date: str, frequency: str = "once", notes: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO reminders (title, category, due_date, frequency, completed, notes)
    VALUES (?, ?, ?, ?, 0, ?)
    """, (title, category, due_date, frequency, notes))
    rem_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rem_id

def get_profile() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def update_profile(data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE profile SET
        name = ?, birth_date = ?, blood_type = ?, allergies = ?,
        chronic_conditions = ?, current_medications = ?, emergency_contact = ?
    WHERE id = 1
    """, (
        data.get("name", ""),
        data.get("birth_date", ""),
        data.get("blood_type", ""),
        data.get("allergies", ""),
        data.get("chronic_conditions", ""),
        data.get("current_medications", ""),
        data.get("emergency_contact", "")
    ))
    conn.commit()
    conn.close()
