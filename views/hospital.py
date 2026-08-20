"""
pages/hospital.py — BloodSetu Hospital Portal
Register, update stock, manage slots, announce events
"""

import streamlit as st
from datetime import date
from auth import require_login, register_form, current_user, login_form
from database import (register_hospital, get_all_hospitals, update_hospital_stock,
                      get_eligible_donors, confirm_donation, get_platform_stats)
from utils import (ALL_BLOOD_GROUPS, GUJARAT_CITIES, get_areas,
                   wa_event_message, get_compatible_groups)
from fraud import show_report_button


def show():
    st.markdown("""
    <div class='sec-header'>🏥 Hospital Portal & Inventory Hub</div>
    <p class='sec-sub'>Manage blood inventory levels, confirm donor slots, and broadcast emergency blood drives.</p>
    """, unsafe_allow_html=True)

    if not require_login("hospital"):
        st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)
        st.markdown("### 📝 Hospital Registration")
        _register_flow()
        return

    user = current_user()

    from database import get_conn
    conn = get_conn()
    hosp = conn.execute(
        "SELECT * FROM hospitals WHERE user_id=?", (user["id"],)
    ).fetchone()
    conn.close()

    if not hosp:
        _complete_profile(user["id"])
        return

    hosp = dict(hosp)

    if not hosp["is_verified"]:
        st.warning(
            "⏳ Your hospital registration is **pending admin verification**. "
            "Verification takes 24–48 hours."
        )
        return

    st.success(f"✅ Verified Partner Hospital — **{hosp['name']}**")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🩸 Update Blood Inventory",
        "📅 Donor Slot Management",
        "🔍 Find Emergency Donors",
        "📣 Broadcast Drive",
        "🚩 Fraud Reporting",
    ])

    with tab1:
        _stock_tab(hosp)
    with tab2:
        _slots_tab(hosp)
    with tab3:
        _find_donors_tab(hosp)
    with tab4:
        _announce_tab(hosp)
    with tab5:
        show_report_button("Hospital", hosp["id"], f"hosp_{hosp['id']}")


def _stock_tab(hosp):
    st.markdown("### 🩸 Manage Available Blood Stock")

    if hosp.get("update_due"):
        due = date.fromisoformat(hosp["update_due"])
        if date.today() > due:
            st.error("⚠️ **Inventory update required!** Please update available stock to maintain verified status.")

    st.info(
        f"Last updated: **{hosp.get('last_updated','Never')}** · "
        f"Next update due: **{hosp.get('update_due','—')}**"
    )

    current = hosp.get("blood_available", "") or ""
    current_groups = [g.strip() for g in current.split(",") if g.strip()]

    st.markdown("<div class='form-glass'>", unsafe_allow_html=True)
    available = st.multiselect(
        "Select blood groups currently in stock:",
        ALL_BLOOD_GROUPS,
        default=current_groups
    )

    if st.button("💾 Save Inventory Levels", use_container_width=True):
        update_hospital_stock(hosp["id"], ",".join(available))
        st.success("✅ Inventory updated successfully!")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _slots_tab(hosp):
    st.markdown("### 📅 Booked Donor Slots")

    from database import get_conn
    conn = get_conn()
    slots = conn.execute("""
        SELECT ds.*, d.name as donor_name, d.blood_group, d.phone as donor_phone,
               d.area as donor_area
        FROM donation_slots ds
        JOIN donors d ON ds.donor_id = d.id
        WHERE ds.location_type='Hospital' AND ds.location_id=?
        AND ds.status != 'Cancelled'
        ORDER BY ds.slot_date ASC
    """, (hosp["id"],)).fetchall()
    conn.close()

    if not slots:
        st.info("No donor slots currently booked for this facility.")
    else:
        for slot in slots:
            slot = dict(slot)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class='bs-card'>
                  <p style='font-weight:700;color:white;margin:0 0 4px;font-size:15px'>
                  🩸 {slot["donor_name"]} — <span style='color:#e74c3c'>{slot["blood_group"]}</span></p>
                  <p style='font-size:12px;color:rgba(255,255,255,0.5);margin:0'>
                  📅 Date: {slot["slot_date"]} · ⏰ Time: {slot["slot_time"]}</p>
                  <p style='font-size:12px;color:#f0c040;margin:4px 0 0'>
                  📞 Phone: {slot["donor_phone"]} · 📍 Area: {slot["donor_area"]}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if slot["status"] == "Pending":
                    if st.button("✅ Confirm Donation", key=f"done_{slot['id']}"):
                        confirm_donation(
                            slot["donor_id"], "Hospital",
                            hosp["id"], hosp["name"]
                        )
                        st.success("Donation confirmed! Donor record updated.")
                        st.rerun()


def _find_donors_tab(hosp):
    st.markdown("### 🔍 Search Regional Donors")
    col1, col2 = st.columns(2)
    with col1:
        bg = st.selectbox("Blood Group", ALL_BLOOD_GROUPS, key="h_find_bg")
    with col2:
        city = st.selectbox("City", GUJARAT_CITIES,
                            index=GUJARAT_CITIES.index(hosp["city"])
                            if hosp["city"] in GUJARAT_CITIES else 0,
                            key="h_find_city")
    areas = get_areas(city)
    area = st.selectbox("Area", areas if areas else ["—"], key="h_find_area")

    if st.button("🔍 Search Eligible Donors", use_container_width=True, key="h_find_btn"):
        compatible = get_compatible_groups(bg)
        donors = get_eligible_donors(compatible, city, area)
        if donors:
            st.success(f"✅ Found {len(donors)} eligible donor(s):")
            for d in donors:
                st.markdown(f"""
                <div class='result-card'>
                  <h4>🩸 {d["name"]} — {d["blood_group"]}</h4>
                  <p>📍 {d["area"]}, {d["city"]} &nbsp;|&nbsp; 💉 {d["donations_count"]} past donations</p>
                  <p style='color:#f0c040;font-size:14px !important;font-weight:700'>📞 Phone: {d["phone"]}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No eligible donors found in this area.")


def _announce_tab(hosp):
    st.markdown("### 📣 Generate Donation Drive Announcement")
    with st.form("announce_form"):
        event_date = st.date_input("📅 Drive Date", min_value=date.today())
        timings    = st.text_input("⏰ Drive Timings", placeholder="e.g. 9AM – 4PM")
        submitted  = st.form_submit_button("📣 Generate WhatsApp Broadcast Text", use_container_width=True)

    if submitted:
        msg = wa_event_message(
            hosp["name"], hosp["city"], hosp["area"],
            str(event_date), timings,
            hosp.get("doctor_name", "Hospital Team"), hosp["phone"]
        )
        st.markdown("<div class='wa-box'>", unsafe_allow_html=True)
        st.code(msg, language=None)
        st.markdown("</div>", unsafe_allow_html=True)


def _register_flow():
    success, user_id = register_form("hospital")
    if success and user_id:
        _complete_profile(user_id)


def _complete_profile(user_id):
    st.markdown("<div class='form-glass'>", unsafe_allow_html=True)
    st.markdown("### 🏥 Hospital Facility Registration")
    with st.form("hosp_profile_form"):
        name       = st.text_input("Hospital Name *")
        doctor     = st.text_input("Chief Medical Officer / Contact Person *")
        address    = st.text_input("Full Address *")
        city       = st.selectbox("City *", GUJARAT_CITIES)
        areas      = get_areas(city)
        area       = st.selectbox("Area *", areas if areas else ["—"])
        phone      = st.text_input("Official Contact Phone Number *")
        emergency  = st.checkbox("24×7 Emergency Blood Support Available")

        if st.form_submit_button("📝 Submit Registration for Approval", use_container_width=True):
            if name and doctor and phone:
                register_hospital(
                    user_id, name, doctor, address, city, area, phone, int(emergency)
                )
                st.success("✅ Facility profile submitted! Admin review pending.")
                st.rerun()
            else:
                st.warning("Please fill all required fields.")
    st.markdown("</div>", unsafe_allow_html=True)