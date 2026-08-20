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
    <div class='sec-header'>🏥 Hospital Portal</div>
    <p class='sec-sub'>Manage your hospital profile, blood stock and donor slots</p>
    """, unsafe_allow_html=True)

    if not require_login("hospital"):
        st.markdown("---")
        st.markdown("### 📝 Register Your Hospital")
        _register_flow()
        return

    user = current_user()

    # Get this hospital's record
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
            "You will be visible on BloodSetu once approved. "
            "This usually takes 24–48 hours."
        )
        return

    # Verified — show dashboard
    st.success(f"✅ Verified Hospital — Welcome, **{hosp['name']}**!")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🩸 Blood Stock",
        "📅 Donor Slots",
        "🔍 Find Donors",
        "📣 Announce Event",
        "🚩 Reports",
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
    st.markdown("### 🩸 Update Blood Stock")

    # Outdated warning
    if hosp.get("update_due"):
        due = date.fromisoformat(hosp["update_due"])
        if date.today() > due:
            st.error(
                "⚠️ **Your blood stock information is OVERDUE!** "
                "Please update immediately — seekers may be getting incorrect information."
            )

    st.info(
        f"Last updated: **{hosp.get('last_updated','Never')}** · "
        f"Next update due: **{hosp.get('update_due','—')}** (every 7–15 days)"
    )

    current = hosp.get("blood_available", "") or ""
    current_groups = [g.strip() for g in current.split(",") if g.strip()]

    available = st.multiselect(
        "Select blood groups currently available:",
        ALL_BLOOD_GROUPS,
        default=current_groups
    )

    if st.button("💾 Update Stock", use_container_width=True):
        update_hospital_stock(hosp["id"], ",".join(available))
        st.success("✅ Blood stock updated successfully!")
        st.rerun()


def _slots_tab(hosp):
    st.markdown("### 📅 Donation Slot Management")
    st.info(
        "Post your available timing slots so donors can book them. "
        "When a donor books, you will see their details here."
    )

    # Show booked slots for this hospital
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
        st.info("No donor slots booked yet.")
    else:
        st.markdown(f"**{len(slots)} upcoming donor slot(s):**")
        for slot in slots:
            slot = dict(slot)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class='bs-card'>
                  <p style='font-weight:600;color:white;margin:0 0 4px'>
                  🩸 {slot["donor_name"]} — {slot["blood_group"]}</p>
                  <p style='font-size:12px;color:rgba(255,255,255,0.5);margin:0'>
                  📅 {slot["slot_date"]} · ⏰ {slot["slot_time"]}</p>
                  <p style='font-size:12px;color:#f0c040;margin:4px 0 0'>
                  📞 {slot["donor_phone"]} · 📍 {slot["donor_area"]}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if slot["status"] == "Pending":
                    if st.button("✅ Mark Done", key=f"done_{slot['id']}"):
                        confirm_donation(
                            slot["donor_id"], "Hospital",
                            hosp["id"], hosp["name"]
                        )
                        st.success("Donation confirmed! 90-day countdown started for donor.")
                        st.rerun()


def _find_donors_tab(hosp):
    st.markdown("### 🔍 Find Eligible Donors")
    st.info(
        "Search as a seeker — no login restriction. "
        "Find donors in your city when your stock runs low."
    )

    col1, col2 = st.columns(2)
    with col1:
        bg = st.selectbox("Blood Group Needed", ALL_BLOOD_GROUPS, key="h_find_bg")
    with col2:
        city = st.selectbox("City", GUJARAT_CITIES,
                            index=GUJARAT_CITIES.index(hosp["city"])
                            if hosp["city"] in GUJARAT_CITIES else 0,
                            key="h_find_city")
    areas = get_areas(city)
    area = st.selectbox("Area", areas if areas else ["—"], key="h_find_area")

    if st.button("🔍 Find Donors", use_container_width=True, key="h_find_btn"):
        compatible = get_compatible_groups(bg)
        donors = get_eligible_donors(compatible, city, area)
        if donors:
            st.success(f"✅ Found {len(donors)} eligible donor(s):")
            for d in donors:
                st.markdown(f"""
                <div class='result-card'>
                  <h4>🩸 {d["name"]} — {d["blood_group"]}</h4>
                  <p>📍 {d["area"]}, {d["city"]} &nbsp;|&nbsp;
                     💉 {d["donations_count"]} donations</p>
                  <p style='color:#f0c040'>📞 {d["phone"]}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No eligible donors found in this area right now.")


def _announce_tab(hosp):
    st.markdown("### 📣 Announce Blood Donation Event")
    with st.form("announce_form"):
        event_date = st.date_input("📅 Event Date", min_value=date.today())
        timings    = st.text_input("⏰ Timings", placeholder="e.g. 9AM – 4PM")
        target     = st.number_input("🎯 Target Donors Needed", min_value=1, value=50)
        submitted  = st.form_submit_button("📣 Generate WhatsApp Announcement",
                                           use_container_width=True)

    if submitted:
        msg = wa_event_message(
            hosp["name"], hosp["city"], hosp["area"],
            str(event_date), timings,
            hosp.get("doctor_name", "Hospital Team"), hosp["phone"]
        )
        st.markdown("""
        <div style='background:rgba(37,211,102,0.06);
        border:1px solid rgba(37,211,102,0.25);
        border-radius:12px;padding:16px;margin-top:12px'>
          <p style='color:#25D366;font-weight:700;margin:0 0 8px'>
          📲 WhatsApp Announcement Ready:</p>
        </div>
        """, unsafe_allow_html=True)
        st.code(msg, language=None)
        st.caption("Copy this message and share in your WhatsApp groups")


def _register_flow():
    success, user_id = register_form("hospital")
    if success and user_id:
        _complete_profile(user_id)


def _complete_profile(user_id):
    st.markdown("### 🏥 Complete Hospital Profile")
    with st.form("hosp_profile_form"):
        name       = st.text_input("Hospital Name *")
        doctor     = st.text_input("Doctor / CMO Name *")
        address    = st.text_input("Full Address *")
        city       = st.selectbox("City *", GUJARAT_CITIES)
        areas      = get_areas(city)
        area       = st.selectbox("Area *", areas if areas else ["—"])
        phone      = st.text_input("Contact Number *")
        emergency  = st.checkbox("24×7 Emergency Available")

        if st.form_submit_button("📝 Submit for Verification", use_container_width=True):
            if name and doctor and phone:
                register_hospital(
                    user_id, name, doctor, address, city, area, phone, int(emergency)
                )
                st.success(
                    "✅ Registration submitted! Admin will verify your hospital "
                    "within 24–48 hours. You will be live on BloodSetu once approved."
                )
            else:
                st.warning("Please fill all required fields.")
                