"""
database.py — BloodSetu SQLite Database Handler
All 9 tables. Complete CRUD operations.
"""

import sqlite3
import hashlib
from datetime import datetime, date, timedelta
import os

DB_PATH = os.environ.get("DB_PATH", "bloodsetu.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Create all 9 tables if they don't exist."""
    conn = get_conn()
    c = conn.cursor()

    # 1. USERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        username    TEXT UNIQUE NOT NULL,
        password    TEXT NOT NULL,
        role        TEXT NOT NULL,
        phone       TEXT,
        otp_verified INTEGER DEFAULT 0,
        is_blocked  INTEGER DEFAULT 0,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # 2. DONORS
    c.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id         INTEGER REFERENCES users(id),
        name            TEXT NOT NULL,
        blood_group     TEXT NOT NULL,
        city            TEXT NOT NULL,
        area            TEXT NOT NULL,
        phone           TEXT NOT NULL,
        last_donated    TEXT,
        next_eligible   TEXT,
        status          TEXT DEFAULT 'Available',
        donations_count INTEGER DEFAULT 0,
        daata_wall_opt  INTEGER DEFAULT 0,
        consent_given   INTEGER DEFAULT 0,
        created_at      TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # 3. HOSPITALS
    c.execute("""
    CREATE TABLE IF NOT EXISTS hospitals (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id         INTEGER REFERENCES users(id),
        name            TEXT NOT NULL,
        doctor_name     TEXT,
        address         TEXT,
        city            TEXT NOT NULL,
        area            TEXT NOT NULL,
        phone           TEXT NOT NULL,
        blood_available TEXT,
        last_updated    TEXT,
        update_due      TEXT,
        is_verified     INTEGER DEFAULT 0,
        emergency_24x7  INTEGER DEFAULT 0,
        created_at      TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # 4. BLOOD BANKS
    c.execute("""
    CREATE TABLE IF NOT EXISTS blood_banks (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id          INTEGER REFERENCES users(id),
        name             TEXT NOT NULL,
        doctor_name      TEXT,
        city             TEXT NOT NULL,
        area             TEXT NOT NULL,
        phone            TEXT NOT NULL,
        groups_available TEXT,
        last_updated     TEXT,
        is_verified      INTEGER DEFAULT 0,
        created_at       TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # 5. BLOOD CAMPS
    c.execute("""
    CREATE TABLE IF NOT EXISTS blood_camps (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER REFERENCES users(id),
        organizer   TEXT NOT NULL,
        doctor_name TEXT,
        city        TEXT NOT NULL,
        area        TEXT NOT NULL,
        phone       TEXT NOT NULL,
        camp_date   TEXT NOT NULL,
        timings     TEXT,
        rsvp_count  INTEGER DEFAULT 0,
        is_active   INTEGER DEFAULT 1,
        is_verified INTEGER DEFAULT 0,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # 6. DONATION SLOTS
    c.execute("""
    CREATE TABLE IF NOT EXISTS donation_slots (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id      INTEGER REFERENCES donors(id),
        location_type TEXT NOT NULL,
        location_id   INTEGER NOT NULL,
        slot_date     TEXT NOT NULL,
        slot_time     TEXT NOT NULL,
        status        TEXT DEFAULT 'Pending',
        confirmed_by  TEXT,
        created_at    TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # 7. DONATIONS (confirmed)
    c.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id            INTEGER REFERENCES donors(id),
        confirmed_by_type   TEXT NOT NULL,
        confirmed_by_id     INTEGER NOT NULL,
        location_name       TEXT,
        donation_date       TEXT NOT NULL,
        next_eligible       TEXT NOT NULL,
        created_at          TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # 8. SOS REQUESTS
    c.execute("""
    CREATE TABLE IF NOT EXISTS sos_requests (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        blood_group   TEXT NOT NULL,
        city          TEXT NOT NULL,
        area          TEXT NOT NULL,
        seeker_name   TEXT,
        seeker_phone  TEXT,
        urgency       TEXT DEFAULT 'Urgent',
        posted_at     TEXT DEFAULT CURRENT_TIMESTAMP,
        expires_at    TEXT,
        is_active     INTEGER DEFAULT 1
    )""")

    # 9. FAKE REPORTS
    c.execute("""
    CREATE TABLE IF NOT EXISTS fake_reports (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        reported_phone   TEXT NOT NULL,
        reported_by_type TEXT,
        reported_by_id   INTEGER,
        reason           TEXT,
        reported_at      TEXT DEFAULT CURRENT_TIMESTAMP,
        admin_action     TEXT DEFAULT 'Pending',
        resolved_at      TEXT
    )""")

    conn.commit()
    conn.close()
    seed_sample_data()


# ══════════════════════════════════════════
# SEED SAMPLE DATA
# ══════════════════════════════════════════
def seed_sample_data():
    conn = get_conn()
    c = conn.cursor()

    # seed hospitals if empty
    c.execute("SELECT COUNT(*) FROM hospitals")
    if c.fetchone()[0] == 0:
        hospitals = [
            ("SSG Hospital", "Dr. Rajesh Mehta", "Raopura, Vadodara", "Vadodara", "Raopura",
             "0265-2225555", "A+,A-,B+,B-,O+,O-,AB+,AB-", 1, 1),
            ("Sterling Hospital", "Dr. Priya Shah", "Race Course Road, Vadodara", "Vadodara", "Race Course",
             "0265-2991000", "A+,B+,O+,O-,AB+", 1, 1),
            ("Kiran Hospital", "Dr. Amit Patel", "Surat", "Surat", "Adajan",
             "0261-2474000", "A+,B+,O+,AB+", 1, 1),
            ("Civil Hospital Ahmedabad", "Dr. Sunita Verma", "Asarwa, Ahmedabad", "Ahmedabad", "Asarwa",
             "079-22683721", "A+,A-,B+,B-,O+,O-,AB+,AB-", 1, 1),
            ("Rajkot Civil Hospital", "Dr. Mahesh Solanki", "Kalawad Road, Rajkot", "Rajkot", "Kalawad Road",
             "0281-2244771", "A+,B+,O+,AB+", 1, 1),
        ]
        for h in hospitals:
            today = date.today().isoformat()
            due = (date.today() + timedelta(days=15)).isoformat()
            c.execute("""INSERT INTO hospitals
                (name,doctor_name,address,city,area,phone,blood_available,is_verified,emergency_24x7,last_updated,update_due)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (*h, today, due))

    # seed blood banks if empty
    c.execute("SELECT COUNT(*) FROM blood_banks")
    if c.fetchone()[0] == 0:
        banks = [
            ("Red Cross Blood Bank Vadodara", "Dr. Leena Joshi", "Vadodara", "Sayajigunj",
             "0265-2361234", "A+,A-,B+,B-,O+,O-,AB+,AB-", 1),
            ("Lions Blood Bank Surat", "Dr. Vikram Rao", "Surat", "Nanpura",
             "0261-2461234", "A+,B+,O+,O-,AB+", 1),
            ("Ahmedabad Blood Bank", "Dr. Neha Kapoor", "Ahmedabad", "Navrangpura",
             "079-26302040", "A+,A-,B+,O+,O-,AB+,AB-", 1),
        ]
        for b in banks:
            today = date.today().isoformat()
            c.execute("""INSERT INTO blood_banks
                (name,doctor_name,city,area,phone,groups_available,is_verified,last_updated)
                VALUES (?,?,?,?,?,?,?,?)""", (*b, today))

    # seed sample donors if empty
    c.execute("SELECT COUNT(*) FROM donors")
    if c.fetchone()[0] == 0:
        donors = [
            ("Rahul Shah",   "B+",  "Vadodara", "Alkapuri",   "9876543210", 9, 1),
            ("Priya Mehta",  "O+",  "Vadodara", "Fatehgunj",  "9876543211", 6, 1),
            ("Amit Patel",   "AB-", "Surat",    "Adajan",     "9876543212", 5, 1),
            ("Sneha Joshi",  "A+",  "Ahmedabad","Satellite",  "9876543213", 4, 1),
            ("Dev Raval",    "O-",  "Vadodara", "Manjalpur",  "9876543214", 3, 1),
            ("Kavya Desai",  "AB-", "Surat",    "Vesu",       "9876543215", 4, 1),
            ("Rohan Trivedi","B-",  "Ahmedabad","Navrangpura","9876543216", 2, 1),
            ("Hiral Modi",   "O+",  "Vadodara", "Gotri",      "9876543217", 5, 1),
            ("Tanvi Shah",   "A-",  "Rajkot",   "Kalawad Road","9876543218",6, 1),
            ("Kiran Patel",  "B+",  "Surat",    "Citylight",  "9876543219", 3, 1),
        ]
        ninety_ago = (date.today() - timedelta(days=95)).isoformat()
        eligible   = (date.today() + timedelta(days=0)).isoformat()
        for d in donors:
            c.execute("""INSERT INTO donors
                (name,blood_group,city,area,phone,donations_count,daata_wall_opt,
                 last_donated,next_eligible,status,consent_given)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (*d, ninety_ago, eligible, "Available", 1))

    # seed blood camps if empty
    c.execute("SELECT COUNT(*) FROM blood_camps")
    if c.fetchone()[0] == 0:
        camps = [
            ("Parul University", "Dr. Shivam Dave", "Vadodara", "Waghodia",
             "9898989898", (date.today() + timedelta(days=10)).isoformat(), "9AM - 4PM"),
            ("Lions Club Surat", "Dr. Nila Shah", "Surat", "Adajan",
             "9797979797", (date.today() + timedelta(days=5)).isoformat(), "10AM - 3PM"),
        ]
        for camp in camps:
            c.execute("""INSERT INTO blood_camps
                (organizer,doctor_name,city,area,phone,camp_date,timings,is_verified)
                VALUES (?,?,?,?,?,?,?,1)""", camp)

    conn.commit()
    conn.close()


# ══════════════════════════════════════════
# USER OPERATIONS
# ══════════════════════════════════════════
def register_user(username, password, role, phone):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password,role,phone) VALUES (?,?,?,?)",
                  (username, hash_password(password), role, phone))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return True, user_id
    except sqlite3.IntegrityError:
        return False, None


def login_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=? AND is_blocked=0",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None


def block_user_by_phone(phone):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET is_blocked=1 WHERE phone=?", (phone,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════
# DONOR OPERATIONS
# ══════════════════════════════════════════
def register_donor(user_id, name, blood_group, city, area, phone):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO donors
        (user_id,name,blood_group,city,area,phone,status,consent_given)
        VALUES (?,?,?,?,?,?,'Available',1)""",
        (user_id, name, blood_group, city, area, phone))
    conn.commit()
    conn.close()


def get_donor_by_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM donors WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def update_donor_status(donor_id, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE donors SET status=? WHERE id=?", (status, donor_id))
    conn.commit()
    conn.close()


def get_eligible_donors(blood_groups: list, city: str, area: str):
    """Return donors eligible by 90-day rule, matching blood group + location."""
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    placeholders = ",".join("?" * len(blood_groups))
    query = f"""
        SELECT * FROM donors
        WHERE blood_group IN ({placeholders})
        AND status = 'Available'
        AND consent_given = 1
        AND (last_donated IS NULL OR next_eligible <= ?)
        AND city = ?
        ORDER BY
            CASE WHEN area=? THEN 0 ELSE 1 END,
            donations_count DESC
    """
    c.execute(query, (*blood_groups, today, city, area))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_donors_daata_wall():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT * FROM donors WHERE daata_wall_opt=1
                 ORDER BY donations_count DESC LIMIT 20""")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def confirm_donation(donor_id, confirmed_by_type, confirmed_by_id, location_name):
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    next_el = (date.today() + timedelta(days=90)).isoformat()
    c.execute("""INSERT INTO donations
        (donor_id,confirmed_by_type,confirmed_by_id,location_name,donation_date,next_eligible)
        VALUES (?,?,?,?,?,?)""",
        (donor_id, confirmed_by_type, confirmed_by_id, location_name, today, next_el))
    c.execute("""UPDATE donors SET
        last_donated=?, next_eligible=?, donations_count=donations_count+1
        WHERE id=?""", (today, next_el, donor_id))
    conn.commit()
    conn.close()


def get_donor_donations(donor_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM donations WHERE donor_id=? ORDER BY donation_date DESC", (donor_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ══════════════════════════════════════════
# HOSPITAL / BANK / CAMP SEARCH
# ══════════════════════════════════════════
def search_hospitals(blood_group: str, city: str, area: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT * FROM hospitals
                 WHERE is_verified=1
                 AND city=?
                 AND blood_available LIKE ?
                 ORDER BY CASE WHEN area=? THEN 0 ELSE 1 END""",
              (city, f"%{blood_group}%", area))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_blood_banks(blood_group: str, city: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT * FROM blood_banks
                 WHERE is_verified=1 AND city=?
                 AND groups_available LIKE ?""",
              (city, f"%{blood_group}%"))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_camps(city: str):
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("""SELECT * FROM blood_camps
                 WHERE is_verified=1 AND city=?
                 AND camp_date >= ? AND is_active=1
                 ORDER BY camp_date ASC""",
              (city, today))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_hospitals(verified_only=True):
    conn = get_conn()
    c = conn.cursor()
    if verified_only:
        c.execute("SELECT * FROM hospitals WHERE is_verified=1 ORDER BY city, name")
    else:
        c.execute("SELECT * FROM hospitals ORDER BY city, name")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_blood_banks(verified_only=True):
    conn = get_conn()
    c = conn.cursor()
    if verified_only:
        c.execute("SELECT * FROM blood_banks WHERE is_verified=1 ORDER BY city, name")
    else:
        c.execute("SELECT * FROM blood_banks ORDER BY city, name")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_camps(active_only=True):
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    if active_only:
        c.execute("""SELECT * FROM blood_camps
                     WHERE is_verified=1 AND camp_date >= ? AND is_active=1
                     ORDER BY camp_date ASC""", (today,))
    else:
        c.execute("SELECT * FROM blood_camps ORDER BY camp_date DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ══════════════════════════════════════════
# REGISTRATION (Hospital/Bank/Camp)
# ══════════════════════════════════════════
def register_hospital(user_id, name, doctor, address, city, area, phone, emergency):
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    due = (date.today() + timedelta(days=15)).isoformat()
    c.execute("""INSERT INTO hospitals
        (user_id,name,doctor_name,address,city,area,phone,emergency_24x7,last_updated,update_due)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (user_id, name, doctor, address, city, area, phone, emergency, today, due))
    conn.commit()
    conn.close()


def register_blood_bank(user_id, name, doctor, city, area, phone):
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("""INSERT INTO blood_banks
        (user_id,name,doctor_name,city,area,phone,last_updated)
        VALUES (?,?,?,?,?,?,?)""",
        (user_id, name, doctor, city, area, phone, today))
    conn.commit()
    conn.close()


def register_camp(user_id, organizer, doctor, city, area, phone, camp_date, timings):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO blood_camps
        (user_id,organizer,doctor_name,city,area,phone,camp_date,timings)
        VALUES (?,?,?,?,?,?,?,?)""",
        (user_id, organizer, doctor, city, area, phone, camp_date, timings))
    conn.commit()
    conn.close()


def update_hospital_stock(hospital_id, blood_available):
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    due = (date.today() + timedelta(days=15)).isoformat()
    c.execute("""UPDATE hospitals SET
        blood_available=?, last_updated=?, update_due=?
        WHERE id=?""", (blood_available, today, due, hospital_id))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════
# SLOTS
# ══════════════════════════════════════════
def book_slot(donor_id, location_type, location_id, slot_date, slot_time):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO donation_slots
        (donor_id,location_type,location_id,slot_date,slot_time)
        VALUES (?,?,?,?,?)""",
        (donor_id, location_type, location_id, slot_date, slot_time))
    conn.commit()
    conn.close()


def get_donor_slots(donor_id):
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("""SELECT * FROM donation_slots
                 WHERE donor_id=? AND slot_date >= ?
                 ORDER BY slot_date ASC""", (donor_id, today))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cancel_slot(slot_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE donation_slots SET status='Cancelled' WHERE id=?", (slot_id,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════
# SOS
# ══════════════════════════════════════════
def post_sos(blood_group, city, area, seeker_name, seeker_phone, urgency):
    conn = get_conn()
    c = conn.cursor()
    posted = datetime.now().isoformat()
    expires = (datetime.now() + timedelta(hours=24)).isoformat()
    c.execute("""INSERT INTO sos_requests
        (blood_group,city,area,seeker_name,seeker_phone,urgency,posted_at,expires_at)
        VALUES (?,?,?,?,?,?,?,?)""",
        (blood_group, city, area, seeker_name, seeker_phone, urgency, posted, expires))
    conn.commit()
    conn.close()


def get_active_sos():
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""SELECT * FROM sos_requests
                 WHERE is_active=1 AND expires_at > ?
                 ORDER BY posted_at DESC""", (now,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def expire_old_sos():
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("UPDATE sos_requests SET is_active=0 WHERE expires_at <= ?", (now,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════
# FRAUD
# ══════════════════════════════════════════
def report_fake(reported_phone, reported_by_type, reported_by_id, reason):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO fake_reports
        (reported_phone,reported_by_type,reported_by_id,reason)
        VALUES (?,?,?,?)""",
        (reported_phone, reported_by_type, reported_by_id, reason))
    conn.commit()
    conn.close()


def get_all_reports():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM fake_reports ORDER BY reported_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def resolve_report(report_id, action):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""UPDATE fake_reports SET
        admin_action=?, resolved_at=? WHERE id=?""",
        (action, now, report_id))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════
def verify_hospital(hospital_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE hospitals SET is_verified=1 WHERE id=?", (hospital_id,))
    conn.commit()
    conn.close()


def verify_blood_bank(bank_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE blood_banks SET is_verified=1 WHERE id=?", (bank_id,))
    conn.commit()
    conn.close()


def verify_camp(camp_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE blood_camps SET is_verified=1 WHERE id=?", (camp_id,))
    conn.commit()
    conn.close()


def get_pending_hospitals():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM hospitals WHERE is_verified=0")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pending_banks():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM blood_banks WHERE is_verified=0")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pending_camps():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM blood_camps WHERE is_verified=0")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_platform_stats():
    conn = get_conn()
    c = conn.cursor()
    stats = {}
    c.execute("SELECT COUNT(*) FROM donors"); stats["donors"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM hospitals WHERE is_verified=1"); stats["hospitals"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM blood_banks WHERE is_verified=1"); stats["banks"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM blood_camps WHERE is_verified=1"); stats["camps"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM donations"); stats["donations"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM sos_requests WHERE is_active=1"); stats["active_sos"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM fake_reports WHERE admin_action='Pending'"); stats["pending_reports"] = c.fetchone()[0]
    conn.close()
    return stats

