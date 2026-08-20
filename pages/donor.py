"""
pages/donor.py — BloodSetu Donor Dashboard
Register, slots, history, eligibility, badges, SOS alerts
"""

import streamlit as st
from datetime import date, timedelta
from auth import require_login, register_form, current_user, login_form
from database import (register_donor, get_donor_by_user, get_donor_slots,
                      get_donor_donations, book_slot, cancel_slot,
                      update_donor_status, get_all_hospitals,
                      get_all_blood_banks, get_all_camps, get_active_sos)
from utils import (ALL_BLOOD_GROUPS, GUJARAT_CITIES, get_areas,
                   check_eligibility, eligibility_progress,
                   get_earned_badges, BADGES, get_msg, wa_awareness_message)


def show():
    st.markdown("""
    <div class='sec-header'>🩸 Donor Portal & Dashboard</div>
    <p class='sec-sub'>Manage your availability, donation slots, history, and achievements.</p>
    """, unsafe_allow_html=True)

    if not require_login("donor"):
        st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)
        st.markdown("### 📝 New Donor Registration")
        _register_flow()
        return

    user = current_user()
    donor = get_donor_by_user(user["id"])

    if not donor:
        st.warning("Please complete your donor profile to access the portal.")
        _complete_profile(user["id"])
        return

    # ── PROFILE CARD ──────────────────────────────────────────
    _profile_card(donor)
    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "⏳ Eligibility Status",
        "📅 Upcoming Slots",
        "📊 Donation History",
        "🚨 Emergency SOS Near Me",
        "🏆 Badges & Achievements",
        "⚙️ Account Settings",
    ])

    with tab1:
        _eligibility_tab(donor)

    with tab2:
        _slots_tab(donor)

    with tab3:
        _history_tab(donor)

    with tab4:
        _sos_tab(donor)

    with tab5:
        _badges_tab(donor)

    with tab6:
        _settings_tab(donor)


# ── PROFILE CARD ──────────────────────────────────────────
def _profile_card(donor):
    is_elig, days_since, days_rem = check_eligibility(donor.get("last_donated"))
    lives = donor["donations_count"] * 3

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"""
    <div style='background:rgba(192,57,43,0.08);border:1px solid rgba(192,57,43,0.25);
    border-radius:14px;padding:16px;text-align:center;backdrop-filter:blur(10px)'>
      <div style='font-size:32px;margin-bottom:4px'>🩸</div>
      <div style='font-family:"Playfair Display",serif;font-size:18px;
                  font-weight:700;color:white'>{donor["name"]}</div>
      <div style='font-size:13px;color:#e74c3c;font-weight:600;margin-top:2px'>
          {donor["blood_group"]}</div>
      <div style='font-size:11px;color:rgba(255,255,255,0.5);margin-top:4px'>
          📍 {donor["area"]}, {donor["city"]}</div>
    </div>
    """, unsafe_allow_html=True)

    col2.metric("💉 Total Donations", donor["donations_count"])
    col3.metric("❤️ Lives Saved", lives)
    col4.metric(
        "⏳ Eligibility Status",
        "✅ Ready" if is_elig else f"⏳ {days_rem} days"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    new_status = st.radio(
        "🟢 Set Community Availability Status",
        ["Available", "Unavailable"],
        index=0 if donor["status"] == "Available" else 1,
        horizontal=True,
        key="status_radio"
    )
    if new_status != donor["status"]:
        update_donor_status(donor["id"], new_status)
        st.success(f"Status updated to **{new_status}**")
        st.rerun()


# ── ELIGIBILITY TAB ───────────────────────────────────────
def _eligibility_tab(donor):
    is_elig, days_since, days_rem = check_eligibility(donor.get("last_donated"))
    progress = eligibility_progress(donor.get("last_donated"))

    if is_elig:
        st.markdown(f"""
        <div class='msg-box-success'>
          <b>✅ {get_msg("eligible_again","en")}</b><br>
          <span style='color:rgba(255,255,255,0.45)'>{get_msg("eligible_again","gu")}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='msg-box'>
          ⏳ Whole blood recovery protocol active.<br>
          <b style='color:#e74c3c'>{days_rem} days remaining</b> until your next eligible donation date.<br>
          <span style='color:rgba(255,255,255,0.45)'>તમારું શરીર આગામી વીર કાર્ય માટે તૈયાર થઈ રહ્યું છે.</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='margin-top:12px'>
      <div style='display:flex;justify-content:space-between;font-size:12px;color:rgba(255,255,255,0.6);margin-bottom:4px'>
        <span>WHO 90-Day Recovery Progress</span>
        <span>{progress*100:.0f}%</span>
      </div>
      <div class='progress-wrap'>
        <div class='progress-fill' style='width:{progress*100:.0f}%'></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if donor.get("next_eligible"):
        st.info(f"📅 Next eligible donation date: **{donor['next_eligible']}**")

    if is_elig:
        st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)
        st.markdown("### 📅 Book a Donation Slot")
        _book_slot_form(donor)


# ── SLOTS TAB ─────────────────────────────────────────────
def _slots_tab(donor):
    st.markdown("### 📅 Your Scheduled Slots")
    slots = get_donor_slots(donor["id"])

    if not slots:
        st.info("No upcoming donation slots scheduled. Book a slot below!")
        _book_slot_form(donor)
        return

    for slot in slots:
        loc_type = slot["location_type"]
        icon = "🏥" if loc_type == "Hospital" else "🏦" if loc_type == "Blood Bank" else "🏕️"
        status_color = {
            "Pending": "#f0c040",
            "Confirmed": "#2ecc71",
            "Cancelled": "#e74c3c",
        }.get(slot["status"], "#888")

        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
            <div class='bs-card'>
              <p style='font-size:14px;font-weight:600;color:white;margin:0 0 4px'>
                {icon} {loc_type} Slot</p>
              <p style='font-size:12px;color:rgba(255,255,255,0.5);margin:0'>
                📅 {slot["slot_date"]} &nbsp;|&nbsp; ⏰ {slot["slot_time"]}</p>
              <p style='font-size:11px;margin:4px 0 0'>
                Status: <span style='color:{status_color};font-weight:700'>{slot["status"]}</span>
              </p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if slot["status"] == "Pending":
                if st.button("❌ Cancel Slot", key=f"cancel_{slot['id']}"):
                    cancel_slot(slot["id"])
                    st.success("Slot cancelled.")
                    st.rerun()

    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)
    st.markdown("### ➕ Book Another Slot")
    _book_slot_form(donor)


def _book_slot_form(donor):
    st.markdown("<div class='form-glass'>", unsafe_allow_html=True)

    loc_type = st.selectbox(
        "Select Donation Facility Type",
        ["Hospital", "Blood Bank", "Blood Camp"],
        key="slot_loc_type"
    )

    loc_id = None
    if loc_type == "Hospital":
        hospitals = get_all_hospitals()
        options = {f"🏥 {h['name']} — {h['area']}, {h['city']}": h["id"] for h in hospitals}
        sel = st.selectbox("Select Hospital Facility", list(options.keys()), key="slot_hosp")
        if sel: loc_id = options[sel]

    elif loc_type == "Blood Bank":
        banks = get_all_blood_banks()
        options = {f"🏦 {b['name']} — {b['area']}, {b['city']}": b["id"] for b in banks}
        sel = st.selectbox("Select Blood Bank Facility", list(options.keys()), key="slot_bank")
        if sel: loc_id = options[sel]

    else:
        camps = get_all_camps()
        options = {f"🏕️ {c['organizer']} — {c['camp_date']}": c["id"] for c in camps}
        if options:
            sel = st.selectbox("Select Blood Camp", list(options.keys()), key="slot_camp")
            if sel: loc_id = options[sel]
        else:
            st.info("No active blood camps available right now.")

    slot_date = st.date_input(
        "📅 Preferred Date",
        min_value=date.today(),
        value=date.today() + timedelta(days=1),
        key="slot_date"
    )
    slot_time = st.selectbox(
        "⏰ Preferred Time Slot",
        ["Morning (9AM – 12PM)", "Afternoon (12PM – 4PM)", "Evening (4PM – 7PM)"],
        key="slot_time"
    )

    if st.button("📅 Confirm Slot Booking", use_container_width=True, key="book_slot_btn"):
        if loc_id:
            book_slot(donor["id"], loc_type, loc_id, slot_date.isoformat(), slot_time)
            st.success("✅ Donation slot successfully booked!")
            st.rerun()
        else:
            st.warning("Please select a valid facility.")

    st.markdown("</div>", unsafe_allow_html=True)


# ── HISTORY TAB ───────────────────────────────────────────
def _history_tab(donor):
    st.markdown("### 📊 Verified Donation Records")
    donations = get_donor_donations(donor["id"])

    if not donations:
        st.info("No confirmed donation records found yet. Book your first slot! 🩸")
        return

    for d in donations:
        st.markdown(f"""
        <div class='bs-card'>
          <p style='font-size:14px;font-weight:600;color:white;margin:0 0 4px'>
            ✅ {d["donation_date"]} — {d["location_name"]}</p>
          <p style='font-size:12px;color:rgba(255,255,255,0.5);margin:0'>
            Verified by: {d["confirmed_by_type"]} &nbsp;|&nbsp; ❤️ Potentially saved 3 lives
          </p>
        </div>
        """, unsafe_allow_html=True)


# ── SOS TAB ───────────────────────────────────────────────
def _sos_tab(donor):
    st.markdown("### 🚨 Emergency SOS Requests in Your City")
    is_elig, _, _ = check_eligibility(donor.get("last_donated"))

    if not is_elig:
        st.warning("⏳ SOS alerts hidden — you are currently within your 90-day recovery window.")
        return

    sos_list = get_active_sos()
    nearby = [s for s in sos_list if s["city"] == donor["city"]]

    if not nearby:
        st.info("✅ No active SOS emergency requests in your city right now.")
        return

    for s in nearby:
        st.markdown(f"""
        <div class='result-card' style='border-left-color:#e74c3c'>
          <h4>🚨 {s["blood_group"]} Needed Urgently</h4>
          <p>📍 <b>Location:</b> {s["area"]}, {s["city"]} &nbsp;|&nbsp; ⚡ <b>Urgency:</b> {s["urgency"]}</p>
          <p>📞 <b>Seeker Contact:</b> {s["seeker_name"]} — {s["seeker_phone"]}</p>
          <p style='font-size:11px;color:rgba(255,255,255,0.35);margin-top:4px !important'>Posted: {s["posted_at"][:16]}</p>
        </div>
        """, unsafe_allow_html=True)


# ── BADGES TAB ────────────────────────────────────────────
def _badges_tab(donor):
    st.markdown("### 🏆 Badges & Achievements")
    earned = get_earned_badges(donor["donations_count"], donor["blood_group"])
    earned_ids = {b["id"] for b in earned}

    cols = st.columns(3)
    for i, badge in enumerate(BADGES):
        col = cols[i % 3]
        is_earned = badge["id"] in earned_ids
        badge_class = "badge-gold" if is_earned else "badge-locked"

        col.markdown(f"""
        <div class='bs-card' style='text-align:center;padding:20px 14px'>
          <div style='font-size:36px;margin-bottom:6px'>{badge["icon"]}</div>
          <div style='font-size:14px;font-weight:700;color:white;margin-bottom:2px'>{badge["name"]}</div>
          <div style='font-size:10px;color:rgba(255,255,255,0.45);margin-bottom:6px'>{badge["name_gu"]}</div>
          <div style='font-size:11px;color:rgba(255,255,255,0.35);margin-bottom:8px'>{badge["condition"]}</div>
          <span class='badge-pill {badge_class}'>{"✅ Unlocked" if is_earned else "🔒 Locked"}</span>
        </div>
        """, unsafe_allow_html=True)


# ── SETTINGS TAB ──────────────────────────────────────────
def _settings_tab(donor):
    st.markdown("### ⚙️ Privacy & Preferences")

    from database import get_conn
    current_opt = bool(donor.get("daata_wall_opt", 0))
    new_opt = st.checkbox(
        "🏆 Display profile publicly on the Daata Wall of Honor",
        value=current_opt,
        key="daata_opt"
    )
    if new_opt != current_opt:
        conn = get_conn()
        conn.execute("UPDATE donors SET daata_wall_opt=? WHERE id=?",
                     (int(new_opt), donor["id"]))
        conn.commit()
        conn.close()
        st.success("Preference updated successfully!")

    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)
    st.markdown("### 📤 Awareness Toolkit")
    with st.expander("📲 Generate WhatsApp Awareness Broadcast"):
        st.code(wa_awareness_message(), language=None)


# ── REGISTER FLOW ─────────────────────────────────────────
def _register_flow():
    success, user_id = register_form("donor")
    if success and user_id:
        _complete_profile(user_id)


def _complete_profile(user_id):
    st.markdown("<div class='form-glass'>", unsafe_allow_html=True)
    st.markdown("### 🩸 Complete Donor Registration")

    consent = st.checkbox(
        "✅ I consent to sharing my blood group, area, and contact details with verified seekers during emergencies."
    )

    if not consent:
        st.info("Please accept the donor privacy consent to proceed.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    with st.form("donor_profile_form"):
        name        = st.text_input("Full Name *")
        blood_group = st.selectbox("Blood Group *", ALL_BLOOD_GROUPS)
        city        = st.selectbox("City *", GUJARAT_CITIES)
        areas       = get_areas(city)
        area        = st.selectbox("Area *", areas if areas else ["—"])
        phone       = st.text_input("Phone Number * (10 digits)")

        if st.form_submit_button("✅ Create Donor Profile", use_container_width=True):
            if name and phone and len(phone) == 10 and phone.isdigit():
                register_donor(user_id, name, blood_group, city, area, phone)
                st.success("✅ Registration complete! Welcome to BloodSetu. 🩸")
                st.rerun()
            else:
                st.warning("Please fill all required fields with a valid 10-digit phone number.")

    st.markdown("</div>", unsafe_allow_html=True)