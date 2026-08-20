"""
api.py — BloodSetu FastAPI Backend
Full REST API replacing Streamlit views.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import hashlib, secrets, os
from datetime import datetime, date, timedelta

# Import existing logic (unchanged)
from database import (
    init_db, get_conn,
    register_user, login_user, block_user_by_phone,
    register_donor, get_donor_by_user, update_donor_status,
    get_eligible_donors, get_all_donors_daata_wall, confirm_donation, get_donor_donations,
    search_hospitals, search_blood_banks, search_camps,
    get_all_hospitals, get_all_blood_banks, get_all_camps,
)
from ml_model import tier_search, predict_shortage
from utils import (
    GUJARAT_AREAS, GUJARAT_CITIES, get_areas, get_compatible_groups,
    check_eligibility, eligibility_progress, get_earned_badges,
    wa_sos_message, wa_event_message, wa_awareness_message,
    ALL_BLOOD_GROUPS, BADGES, QUOTES,
)
from fraud import report_fake, admin_fraud_panel

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="BloodSetu API", version="2.0.0")

init_db()

_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # Production — set FRONTEND_ORIGIN env var on Vercel, e.g. https://bloodsetu.vercel.app
    *([os.environ["FRONTEND_ORIGIN"]] if os.environ.get("FRONTEND_ORIGIN") else []),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Simple token store (in-memory for now) ───────────────────────────────────
_sessions: dict[str, dict] = {}

def make_token(user: dict) -> str:
    tok = secrets.token_hex(32)
    _sessions[tok] = user
    return tok

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))):
    if not creds:
        return None
    return _sessions.get(creds.credentials)

def require_user(creds: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    user = _sessions.get(creds.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def require_role(role: str):
    def dep(creds: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        user = _sessions.get(creds.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        if user["role"] != role and user["role"] != "admin":
            raise HTTPException(status_code=403, detail=f"Requires {role} role")
        return user
    return dep

# ─── Pydantic Models ──────────────────────────────────────────────────────────
class LoginReq(BaseModel):
    username: str
    password: str

class RegisterReq(BaseModel):
    username: str
    password: str
    role: str
    phone: str

class DonorProfileReq(BaseModel):
    name: str
    blood_group: str
    city: str
    area: str
    phone: str

class HospitalProfileReq(BaseModel):
    name: str
    doctor_name: Optional[str] = None
    address: Optional[str] = None
    city: str
    area: str
    phone: str
    emergency_24x7: bool = False

class BloodBankProfileReq(BaseModel):
    name: str
    doctor_name: Optional[str] = None
    city: str
    area: str
    phone: str

class CampProfileReq(BaseModel):
    organizer: str
    doctor_name: Optional[str] = None
    city: str
    area: str
    phone: str
    camp_date: str
    timings: Optional[str] = None

class InventoryReq(BaseModel):
    groups: List[str]

class SlotBookReq(BaseModel):
    location_type: str
    location_id: int
    slot_date: str
    slot_time: str

class SosReq(BaseModel):
    blood_group: str
    city: str
    area: str
    seeker_name: Optional[str] = None
    seeker_phone: Optional[str] = None
    urgency: str = "Urgent"

class FraudReportReq(BaseModel):
    reported_phone: str
    reason: str

class VerifyEntityReq(BaseModel):
    entity_type: str  # hospital | blood_bank | camp
    entity_id: int

class FraudActionReq(BaseModel):
    report_id: int
    action: str  # Blocked | Ignored


# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


# ─── Auth ─────────────────────────────────────────────────────────────────────
@app.post("/api/auth/login")
def login(req: LoginReq):
    ADMIN_USERNAME = "bloodsetu_admin"
    ADMIN_PASSWORD = "BloodSetu@2026"
    if req.username == ADMIN_USERNAME and req.password == ADMIN_PASSWORD:
        user = {"id": 0, "username": ADMIN_USERNAME, "role": "admin", "phone": ""}
        return {"token": make_token(user), "user": user}
    user = login_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials or account blocked")
    tok = make_token(user)
    donor_data = None
    if user["role"] == "donor":
        donor_data = get_donor_by_user(user["id"])
    return {"token": tok, "user": user, "donor_data": donor_data}

@app.post("/api/auth/register")
def register(req: RegisterReq):
    if req.role not in ("donor", "hospital", "blood_bank", "camp"):
        raise HTTPException(status_code=400, detail="Invalid role")
    if len(req.phone) != 10 or not req.phone.isdigit():
        raise HTTPException(status_code=400, detail="Invalid phone")
    ok, user_id = register_user(req.username, req.password, req.role, req.phone)
    if not ok:
        raise HTTPException(status_code=409, detail="Username already exists")
    return {"user_id": user_id}

@app.get("/api/auth/me")
def me(user=Depends(require_user)):
    extra = {}
    if user.get("role") == "donor":
        extra["donor_data"] = get_donor_by_user(user["id"])
    return {**user, **extra}

@app.post("/api/auth/logout")
def logout(creds: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    _sessions.pop(creds.credentials, None)
    return {"ok": True}


# ─── Reference Data ───────────────────────────────────────────────────────────
@app.get("/api/ref/cities")
def cities():
    return GUJARAT_CITIES

@app.get("/api/ref/areas/{city}")
def areas(city: str):
    return get_areas(city)

@app.get("/api/ref/blood-groups")
def blood_groups():
    return ALL_BLOOD_GROUPS

@app.get("/api/ref/quotes")
def quotes():
    return QUOTES


# ─── Stats ────────────────────────────────────────────────────────────────────
@app.get("/api/stats")
def stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM donors WHERE status='Available'")
    donors = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM hospitals WHERE is_verified=1")
    hospitals = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM blood_banks WHERE is_verified=1")
    banks = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM blood_camps WHERE is_verified=1 AND is_active=1")
    camps = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM donations")
    donations = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM sos_requests WHERE is_active=1")
    active_sos = c.fetchone()[0]
    conn.close()
    return {
        "donors": donors,
        "hospitals": hospitals,
        "blood_banks": banks,
        "camps": camps,
        "donations": donations,
        "active_sos": active_sos,
        "lives_saved": donations * 3,
    }


# ─── SOS ──────────────────────────────────────────────────────────────────────
@app.get("/api/sos/active")
def get_active_sos():
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""SELECT * FROM sos_requests
                 WHERE is_active=1 AND (expires_at IS NULL OR expires_at > ?)
                 ORDER BY posted_at DESC LIMIT 10""", (now,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.post("/api/sos")
def post_sos(req: SosReq):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    expires = (datetime.now() + timedelta(hours=24)).isoformat()
    c.execute("""INSERT INTO sos_requests
        (blood_group,city,area,seeker_name,seeker_phone,urgency,posted_at,expires_at,is_active)
        VALUES (?,?,?,?,?,?,?,?,1)""",
        (req.blood_group, req.city, req.area,
         req.seeker_name, req.seeker_phone, req.urgency, now, expires))
    conn.commit()
    conn.close()
    # Return WhatsApp message too
    msg = wa_sos_message(req.blood_group, req.area, req.city,
                         req.seeker_phone or "Contact BloodSetu")
    return {"ok": True, "wa_message": msg}

@app.get("/api/sos/city/{city}")
def sos_by_city(city: str):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""SELECT * FROM sos_requests
                 WHERE city=? AND is_active=1 AND (expires_at IS NULL OR expires_at > ?)
                 ORDER BY posted_at DESC""", (city, now))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ─── Search / Tier Search ─────────────────────────────────────────────────────
@app.get("/api/search")
def search(blood_group: str, city: str, area: str):
    if blood_group not in ALL_BLOOD_GROUPS:
        raise HTTPException(status_code=400, detail="Invalid blood group")
    results = tier_search(blood_group, city, area)
    return results


# ─── Donor ────────────────────────────────────────────────────────────────────
@app.post("/api/donor/profile")
def create_donor_profile(req: DonorProfileReq, user=Depends(require_role("donor"))):
    existing = get_donor_by_user(user["id"])
    if existing:
        raise HTTPException(status_code=409, detail="Donor profile already exists")
    register_donor(user["id"], req.name, req.blood_group, req.city, req.area, req.phone)
    return get_donor_by_user(user["id"])

@app.get("/api/donor/profile")
def get_my_donor_profile(user=Depends(require_role("donor"))):
    donor = get_donor_by_user(user["id"])
    if not donor:
        raise HTTPException(status_code=404, detail="Profile not found")
    is_eligible, days_since, days_remaining = check_eligibility(donor.get("last_donated"))
    progress = eligibility_progress(donor.get("last_donated"))
    badges = get_earned_badges(donor.get("donations_count", 0), donor.get("blood_group", ""))
    return {
        **donor,
        "is_eligible": is_eligible,
        "days_since": days_since,
        "days_remaining": days_remaining,
        "progress": progress,
        "badges": badges,
    }

@app.patch("/api/donor/status")
def update_status(status_val: str, user=Depends(require_role("donor"))):
    donor = get_donor_by_user(user["id"])
    if not donor:
        raise HTTPException(status_code=404, detail="Profile not found")
    update_donor_status(donor["id"], status_val)
    return {"ok": True}

@app.patch("/api/donor/daata-wall")
def toggle_daata_wall(opt_in: bool, user=Depends(require_role("donor"))):
    donor = get_donor_by_user(user["id"])
    if not donor:
        raise HTTPException(status_code=404, detail="Profile not found")
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE donors SET daata_wall_opt=? WHERE id=?", (1 if opt_in else 0, donor["id"]))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/donor/history")
def donor_history(user=Depends(require_role("donor"))):
    donor = get_donor_by_user(user["id"])
    if not donor:
        return []
    return get_donor_donations(donor["id"])

@app.get("/api/donor/slots")
def donor_slots(user=Depends(require_role("donor"))):
    donor = get_donor_by_user(user["id"])
    if not donor:
        return []
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT ds.*, 
        CASE ds.location_type
            WHEN 'Hospital' THEN (SELECT name FROM hospitals WHERE id=ds.location_id)
            WHEN 'Blood Bank' THEN (SELECT name FROM blood_banks WHERE id=ds.location_id)
            WHEN 'Blood Camp' THEN (SELECT organizer FROM blood_camps WHERE id=ds.location_id)
        END as location_name
        FROM donation_slots ds WHERE ds.donor_id=? ORDER BY slot_date DESC""", (donor["id"],))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.post("/api/donor/slots")
def book_slot(req: SlotBookReq, user=Depends(require_role("donor"))):
    donor = get_donor_by_user(user["id"])
    if not donor:
        raise HTTPException(status_code=404, detail="Profile not found")
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO donation_slots (donor_id,location_type,location_id,slot_date,slot_time)
                 VALUES (?,?,?,?,?)""",
              (donor["id"], req.location_type, req.location_id, req.slot_date, req.slot_time))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/api/donor/slots/{slot_id}")
def cancel_slot(slot_id: int, user=Depends(require_role("donor"))):
    donor = get_donor_by_user(user["id"])
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE donation_slots SET status='Cancelled' WHERE id=? AND donor_id=?",
              (slot_id, donor["id"]))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/donor/wa-message")
def donor_wa_message():
    return {"message": wa_awareness_message()}


# ─── Daata Wall ───────────────────────────────────────────────────────────────
@app.get("/api/daata-wall")
def daata_wall():
    donors = get_all_donors_daata_wall()
    result = []
    for d in donors:
        badges = get_earned_badges(d.get("donations_count", 0), d.get("blood_group", ""))
        result.append({**d, "badges": badges})
    return result


# ─── Hospital ─────────────────────────────────────────────────────────────────
@app.post("/api/hospital/profile")
def create_hospital_profile(req: HospitalProfileReq, user=Depends(require_role("hospital"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM hospitals WHERE user_id=?", (user["id"],))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail="Profile exists")
    today = date.today().isoformat()
    due = (date.today() + timedelta(days=15)).isoformat()
    c.execute("""INSERT INTO hospitals (user_id,name,doctor_name,address,city,area,phone,emergency_24x7,last_updated,update_due)
                 VALUES (?,?,?,?,?,?,?,?,?,?)""",
              (user["id"], req.name, req.doctor_name, req.address,
               req.city, req.area, req.phone, 1 if req.emergency_24x7 else 0, today, due))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/hospital/profile")
def get_hospital_profile(user=Depends(require_role("hospital"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM hospitals WHERE user_id=?", (user["id"],))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    return dict(row)

@app.patch("/api/hospital/inventory")
def update_hospital_inventory(req: InventoryReq, user=Depends(require_role("hospital"))):
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    due = (date.today() + timedelta(days=15)).isoformat()
    c.execute("UPDATE hospitals SET blood_available=?,last_updated=?,update_due=? WHERE user_id=?",
              (",".join(req.groups), today, due, user["id"]))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/hospital/slots")
def hospital_slots(user=Depends(require_role("hospital"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM hospitals WHERE user_id=?", (user["id"],))
    row = c.fetchone()
    if not row:
        conn.close()
        return []
    hosp_id = row[0]
    c.execute("""SELECT ds.*, d.name as donor_name, d.blood_group, d.phone as donor_phone
                 FROM donation_slots ds
                 JOIN donors d ON ds.donor_id=d.id
                 WHERE ds.location_type='Hospital' AND ds.location_id=?
                 AND ds.status='Pending'
                 ORDER BY ds.slot_date, ds.slot_time""", (hosp_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.post("/api/hospital/confirm/{slot_id}")
def hospital_confirm(slot_id: int, user=Depends(require_role("hospital"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id,name FROM hospitals WHERE user_id=?", (user["id"],))
    hosp = c.fetchone()
    if not hosp:
        conn.close()
        raise HTTPException(status_code=404)
    c.execute("SELECT donor_id FROM donation_slots WHERE id=? AND location_type='Hospital' AND location_id=?",
              (slot_id, hosp[0]))
    slot = c.fetchone()
    if not slot:
        conn.close()
        raise HTTPException(status_code=404, detail="Slot not found")
    c.execute("UPDATE donation_slots SET status='Confirmed' WHERE id=?", (slot_id,))
    conn.commit()
    conn.close()
    confirm_donation(slot[0], "Hospital", hosp[0], hosp[1])
    return {"ok": True}

@app.get("/api/hospital/donors")
def hospital_find_donors(blood_group: str, city: str, area: str, user=Depends(require_role("hospital"))):
    compatible = get_compatible_groups(blood_group)
    donors = get_eligible_donors(compatible, city, area)
    return donors

@app.post("/api/hospital/fraud-report")
def hospital_report_fraud(req: FraudReportReq, user=Depends(require_role("hospital"))):
    report_fake(req.reported_phone, "Hospital", user["id"], req.reason)
    return {"ok": True}

@app.get("/api/hospital/wa-message")
def hospital_wa(user=Depends(require_role("hospital"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM hospitals WHERE user_id=?", (user["id"],))
    h = c.fetchone()
    conn.close()
    if not h:
        return {"message": ""}
    h = dict(h)
    msg = wa_event_message(h["name"], h["city"], h["area"], date.today().isoformat(),
                           "9AM - 4PM", h.get("doctor_name", ""), h["phone"])
    return {"message": msg}


# ─── Blood Bank ───────────────────────────────────────────────────────────────
@app.post("/api/blood-bank/profile")
def create_bank_profile(req: BloodBankProfileReq, user=Depends(require_role("blood_bank"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM blood_banks WHERE user_id=?", (user["id"],))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail="Profile exists")
    today = date.today().isoformat()
    c.execute("INSERT INTO blood_banks (user_id,name,doctor_name,city,area,phone,last_updated) VALUES (?,?,?,?,?,?,?)",
              (user["id"], req.name, req.doctor_name, req.city, req.area, req.phone, today))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/blood-bank/profile")
def get_bank_profile(user=Depends(require_role("blood_bank"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM blood_banks WHERE user_id=?", (user["id"],))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404)
    return dict(row)

@app.patch("/api/blood-bank/inventory")
def update_bank_inventory(req: InventoryReq, user=Depends(require_role("blood_bank"))):
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("UPDATE blood_banks SET groups_available=?,last_updated=? WHERE user_id=?",
              (",".join(req.groups), today, user["id"]))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/blood-bank/slots")
def bank_slots(user=Depends(require_role("blood_bank"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM blood_banks WHERE user_id=?", (user["id"],))
    row = c.fetchone()
    if not row:
        conn.close()
        return []
    bank_id = row[0]
    c.execute("""SELECT ds.*, d.name as donor_name, d.blood_group, d.phone as donor_phone
                 FROM donation_slots ds
                 JOIN donors d ON ds.donor_id=d.id
                 WHERE ds.location_type='Blood Bank' AND ds.location_id=?
                 AND ds.status='Pending'
                 ORDER BY ds.slot_date, ds.slot_time""", (bank_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.post("/api/blood-bank/confirm/{slot_id}")
def bank_confirm(slot_id: int, user=Depends(require_role("blood_bank"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id,name FROM blood_banks WHERE user_id=?", (user["id"],))
    bank = c.fetchone()
    if not bank:
        conn.close()
        raise HTTPException(status_code=404)
    c.execute("SELECT donor_id FROM donation_slots WHERE id=? AND location_type='Blood Bank' AND location_id=?",
              (slot_id, bank[0]))
    slot = c.fetchone()
    if not slot:
        conn.close()
        raise HTTPException(status_code=404)
    c.execute("UPDATE donation_slots SET status='Confirmed' WHERE id=?", (slot_id,))
    conn.commit()
    conn.close()
    confirm_donation(slot[0], "Blood Bank", bank[0], bank[1])
    return {"ok": True}

@app.get("/api/blood-bank/donors")
def bank_find_donors(blood_group: str, city: str, area: str, user=Depends(require_role("blood_bank"))):
    compatible = get_compatible_groups(blood_group)
    return get_eligible_donors(compatible, city, area)

@app.post("/api/blood-bank/fraud-report")
def bank_report_fraud(req: FraudReportReq, user=Depends(require_role("blood_bank"))):
    report_fake(req.reported_phone, "Blood Bank", user["id"], req.reason)
    return {"ok": True}


# ─── Blood Camp ───────────────────────────────────────────────────────────────
@app.post("/api/camp/profile")
def create_camp_profile(req: CampProfileReq, user=Depends(require_role("camp"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM blood_camps WHERE user_id=?", (user["id"],))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail="Profile exists")
    c.execute("""INSERT INTO blood_camps (user_id,organizer,doctor_name,city,area,phone,camp_date,timings)
                 VALUES (?,?,?,?,?,?,?,?)""",
              (user["id"], req.organizer, req.doctor_name, req.city, req.area,
               req.phone, req.camp_date, req.timings))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/camp/profile")
def get_camp_profile(user=Depends(require_role("camp"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM blood_camps WHERE user_id=?", (user["id"],))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404)
    return dict(row)

@app.get("/api/camp/slots")
def camp_slots(user=Depends(require_role("camp"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM blood_camps WHERE user_id=?", (user["id"],))
    row = c.fetchone()
    if not row:
        conn.close()
        return []
    camp_id = row[0]
    c.execute("""SELECT ds.*, d.name as donor_name, d.blood_group, d.phone as donor_phone
                 FROM donation_slots ds
                 JOIN donors d ON ds.donor_id=d.id
                 WHERE ds.location_type='Blood Camp' AND ds.location_id=?
                 AND ds.status='Pending'
                 ORDER BY ds.slot_date""", (camp_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.post("/api/camp/confirm/{slot_id}")
def camp_confirm(slot_id: int, user=Depends(require_role("camp"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id,organizer FROM blood_camps WHERE user_id=?", (user["id"],))
    camp = c.fetchone()
    if not camp:
        conn.close()
        raise HTTPException(status_code=404)
    c.execute("SELECT donor_id FROM donation_slots WHERE id=? AND location_type='Blood Camp' AND location_id=?",
              (slot_id, camp[0]))
    slot = c.fetchone()
    if not slot:
        conn.close()
        raise HTTPException(status_code=404)
    c.execute("UPDATE donation_slots SET status='Confirmed' WHERE id=?", (slot_id,))
    conn.commit()
    conn.close()
    confirm_donation(slot[0], "Blood Camp", camp[0], camp[1])
    return {"ok": True}

@app.post("/api/camp/fraud-report")
def camp_report_fraud(req: FraudReportReq, user=Depends(require_role("camp"))):
    report_fake(req.reported_phone, "Blood Camp", user["id"], req.reason)
    return {"ok": True}

@app.get("/api/camp/wa-message")
def camp_wa(user=Depends(require_role("camp"))):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM blood_camps WHERE user_id=?", (user["id"],))
    camp = c.fetchone()
    conn.close()
    if not camp:
        return {"message": ""}
    c2 = dict(camp)
    msg = wa_event_message(c2["organizer"], c2["city"], c2["area"],
                           c2["camp_date"], c2.get("timings", ""),
                           c2.get("doctor_name", ""), c2["phone"])
    return {"message": msg}


# ─── Admin ────────────────────────────────────────────────────────────────────
def require_admin(creds: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    user = _sessions.get(creds.credentials)
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user

@app.get("/api/admin/pending")
def admin_pending(admin=Depends(require_admin)):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM hospitals WHERE is_verified=0 ORDER BY created_at DESC")
    hospitals = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM blood_banks WHERE is_verified=0 ORDER BY created_at DESC")
    banks = [dict(r) for r in c.fetchall()]
    c.execute("SELECT * FROM blood_camps WHERE is_verified=0 ORDER BY created_at DESC")
    camps = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"hospitals": hospitals, "blood_banks": banks, "camps": camps}

@app.post("/api/admin/verify")
def admin_verify(req: VerifyEntityReq, admin=Depends(require_admin)):
    conn = get_conn()
    c = conn.cursor()
    table_map = {"hospital": "hospitals", "blood_bank": "blood_banks", "camp": "blood_camps"}
    table = table_map.get(req.entity_type)
    if not table:
        conn.close()
        raise HTTPException(status_code=400, detail="Unknown entity type")
    c.execute(f"UPDATE {table} SET is_verified=1 WHERE id=?", (req.entity_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/api/admin/entity/{entity_type}/{entity_id}")
def admin_reject(entity_type: str, entity_id: int, admin=Depends(require_admin)):
    conn = get_conn()
    c = conn.cursor()
    table_map = {"hospital": "hospitals", "blood_bank": "blood_banks", "camp": "blood_camps"}
    table = table_map.get(entity_type)
    if not table:
        conn.close()
        raise HTTPException(status_code=400)
    c.execute(f"DELETE FROM {table} WHERE id=? AND is_verified=0", (entity_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/admin/fraud-reports")
def admin_fraud(admin=Depends(require_admin)):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM fake_reports ORDER BY reported_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.post("/api/admin/fraud-action")
def admin_fraud_action(req: FraudActionReq, admin=Depends(require_admin)):
    conn = get_conn()
    c = conn.cursor()
    if req.action == "Blocked":
        c.execute("SELECT reported_phone FROM fake_reports WHERE id=?", (req.report_id,))
        row = c.fetchone()
        if row:
            block_user_by_phone(row[0])
    c.execute("UPDATE fake_reports SET admin_action=?,resolved_at=? WHERE id=?",
              (req.action, datetime.now().isoformat(), req.report_id))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/admin/all-donors")
def admin_all_donors(admin=Depends(require_admin)):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM donors ORDER BY created_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.get("/api/admin/all-hospitals")
def admin_all_hospitals(admin=Depends(require_admin)):
    return get_all_hospitals(verified_only=False)

@app.get("/api/admin/all-blood-banks")
def admin_all_banks(admin=Depends(require_admin)):
    return get_all_blood_banks(verified_only=False)

@app.get("/api/admin/all-camps")
def admin_all_camps(admin=Depends(require_admin)):
    return get_all_camps(active_only=False)


# ─── Analytics ────────────────────────────────────────────────────────────────
@app.get("/api/analytics/shortage")
def shortage_prediction(city: str = "Vadodara"):
    return predict_shortage(city)

@app.get("/api/analytics/blood-distribution")
def blood_distribution():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT blood_group, COUNT(*) as count FROM donors GROUP BY blood_group ORDER BY blood_group")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.get("/api/analytics/hospitals-by-city")
def hospitals_by_city():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT city, COUNT(*) as count FROM hospitals WHERE is_verified=1 GROUP BY city ORDER BY count DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.get("/api/analytics/donations-trend")
def donations_trend():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT substr(donation_date,1,7) as month, COUNT(*) as count
                 FROM donations GROUP BY month ORDER BY month DESC LIMIT 12""")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return list(reversed(rows))


# ─── Public Hospital/Bank/Camp Lists ─────────────────────────────────────────
@app.get("/api/hospitals")
def public_hospitals(city: Optional[str] = None):
    hospitals = get_all_hospitals()
    if city:
        hospitals = [h for h in hospitals if h["city"] == city]
    return hospitals

@app.get("/api/blood-banks")
def public_banks(city: Optional[str] = None):
    banks = get_all_blood_banks()
    if city:
        banks = [b for b in banks if b["city"] == city]
    return banks

@app.get("/api/camps")
def public_camps(city: Optional[str] = None):
    camps = get_all_camps()
    if city:
        camps = [c for c in camps if c["city"] == city]
    return camps
