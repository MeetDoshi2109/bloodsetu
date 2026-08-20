"""
pages/camp.py — BloodSetu Blood Camp Portal
Register camp, manage RSVPs, announce events, auto-expire
"""

import streamlit as st
from datetime import date
from auth import require_login, register_form, current_user
from database import (register_camp, get_all_camps, confirm_donation)
from utils import (GUJARAT_CITIES, get_areas, wa_event_message)
from fraud import show_report_button


def show():
    st.markdown("""
    <div class='sec-header'>🏕️ Blood Donation Drive & Camp Hub</div>
    <p class='sec-sub'>Organize community blood drives, manage donor RSVPs, and confirm donations.</p>
    """, unsafe_allow_html=True)

    if not require_login("camp"):
        st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)
        st.markdown("### 📝 Register New Blood Camp")
        _register_flow()
        return

    user = current_user()

    from database import get_conn
    conn = get_conn()
    camp = conn.execute(
        "SELECT * FROM blood_camps WHERE user_id=?", (user["id"],)
    ).fetchone()
    conn.close()

    if not camp:
        _complete_profile(user["id"])
        return

    camp = dict(camp)

    if camp["camp_date"] < date.today().isoformat():
        st.warning("⏳ This blood drive date has passed. The event is listed as inactive.")
        return

    if not camp["is_verified"]:
        st.warning("⏳ Your blood camp registration is pending admin verification.")
        return

    st.success(f"✅ Verified Active Drive — **{camp['organizer']}**")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Camp Overview",
        "📅 Donor RSVPs & Slots",
        "📣 Broadcast Drive",
        "🚩 Fraud Reporting",
    ])

    with tab1:
        _details_tab(camp)
    with tab2:
        _slots_tab(camp)
    with tab3:
        _announce_tab(camp)
    with tab4:
        show_report_button("Blood Camp", camp["id"], f"camp_{camp['id']}")


def _details_tab(camp):
    st.markdown("### 📋 Drive Information")
    st.markdown(f"""
    <div class='bs-card'>
      <p style='font-weight:700;font-size:18px;color:white;margin:0 0 8px'>
      🏕️ {camp["organizer"]}</p>
      <p style='font-size:13px;color:rgba(255,255,255,0.65);margin:4px 0'>
      👨‍⚕️ <b>Coordinator:</b> {camp.get("doctor_name","—")}</p>
      <p style='font-size:13px;color:rgba(255,255,255,0.65);margin:4px 0'>
      📍 <b>Venue:</b> {camp["area"]}, {camp["city"]}</p>
      <p style='font-size:13px;color:#f0c040;margin:4px 0'>
      📅 <b>Date:</b> {camp["camp_date"]} &nbsp;·&nbsp; ⏰ <b>Timings:</b> {camp.get("timings","—")}</p>
      <p style='font-size:13px;color:rgba(255,255,255,0.65);margin:4px 0'>
      📞 <b>Phone:</b> {camp["phone"]}</p>
      <p style='font-size:13px;color:#2ecc71;margin:8px 0 0;font-weight:600'>
      ✅ RSVPs / Slots Booked: {camp["rsvp_count"]} donors</p>
    </div>
    """, unsafe_allow_html=True)


def _slots_tab(camp):
    st.markdown("### 📅 Booked Donor Slots")

    from database import get_conn
    conn = get_conn()
    slots = conn.execute("""
        SELECT ds.*, d.name as donor_name, d.blood_group,
               d.phone as donor_phone
        FROM donation_slots ds
        JOIN donors d ON ds.donor_id = d.id
        WHERE ds.location_type='Blood Camp' AND ds.location_id=?
        AND ds.status != 'Cancelled'
        ORDER BY ds.slot_date ASC
    """, (camp["id"],)).fetchall()
    conn.close()

    if not slots:
        st.info("No donor slots currently booked for this camp.")
        return

    for slot in [dict(s) for s in slots]:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div class='bs-card'>
              <p style='font-weight:700;color:white;margin:0 0 4px;font-size:15px'>
              🩸 {slot["donor_name"]} — <span style='color:#e74c3c'>{slot["blood_group"]}</span></p>
              <p style='font-size:12px;color:rgba(255,255,255,0.5);margin:0'>
              📅 Date: {slot["slot_date"]} · ⏰ Time: {slot["slot_time"]}</p>
              <p style='font-size:12px;color:#f0c040;margin:4px 0 0'>
              📞 Contact Phone: {slot["donor_phone"]}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if slot["status"] == "Pending":
                if st.button("✅ Mark Done", key=f"camp_done_{slot['id']}"):
                    confirm_donation(
                        slot["donor_id"], "Blood Camp",
                        camp["id"], camp["organizer"]
                    )
                    st.success("Donation confirmed!")
                    st.rerun()


def _announce_tab(camp):
    st.markdown("### 📣 WhatsApp Drive Announcement")
    msg = wa_event_message(
        camp["organizer"], camp["city"], camp["area"],
        camp["camp_date"], camp.get("timings", "—"),
        camp.get("doctor_name", "Camp Coordinator"), camp["phone"]
    )
    st.markdown("<div class='wa-box'>", unsafe_allow_html=True)
    st.code(msg, language=None)
    st.markdown("</div>", unsafe_allow_html=True)


def _register_flow():
    success, user_id = register_form("camp")
    if success and user_id:
        _complete_profile(user_id)


def _complete_profile(user_id):
    st.markdown("<div class='form-glass'>", unsafe_allow_html=True)
    st.markdown("### 🏕️ Register Blood Donation Drive")
    with st.form("camp_profile_form"):
        organizer  = st.text_input("Organizer / NGO / College Name *")
        doctor     = st.text_input("Coordinator / Doctor Name *")
        city       = st.selectbox("City *", GUJARAT_CITIES)
        areas      = get_areas(city)
        area       = st.selectbox("Area *", areas if areas else ["—"])
        phone      = st.text_input("Contact Phone Number *")
        camp_date  = st.date_input("Drive Date *", min_value=date.today())
        timings    = st.text_input("Drive Timings *", placeholder="e.g. 9AM – 4PM")

        if st.form_submit_button("📝 Submit Drive for Verification", use_container_width=True):
            if organizer and doctor and phone:
                register_camp(
                    user_id, organizer, doctor, city, area,
                    phone, camp_date.isoformat(), timings
                )
                st.success("✅ Camp registered! Admin review pending.")
                st.rerun()
            else:
                st.warning("Please fill all required fields.")
    st.markdown("</div>", unsafe_allow_html=True)