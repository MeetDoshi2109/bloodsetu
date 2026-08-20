"""
pages/blood_bank.py — BloodSetu Blood Bank Portal
Register, update availability, manage slots, announce events
"""

import streamlit as st
from datetime import date
from auth import require_login, register_form, current_user
from database import (register_blood_bank, get_all_blood_banks,
                      confirm_donation, get_eligible_donors)
from utils import (ALL_BLOOD_GROUPS, GUJARAT_CITIES, get_areas,
                   wa_event_message, get_compatible_groups)
from fraud import show_report_button


def show():
    st.markdown("""
    <div class='sec-header'>🏦 Blood Bank Portal</div>
    <p class='sec-sub'>Manage your blood bank profile, availability and donor slots</p>
    """, unsafe_allow_html=True)

    if not require_login("blood_bank"):
        st.markdown("---")
        st.markdown("### 📝 Register Your Blood Bank")
        _register_flow()
        return

    user = current_user()

    from database import get_conn
    conn = get_conn()
    bank = conn.execute(
        "SELECT * FROM blood_banks WHERE user_id=?", (user["id"],)
    ).fetchone()
    conn.close()

    if not bank:
        _complete_profile(user["id"])
        return

    bank = dict(bank)

    if not bank["is_verified"]:
        st.warning(
            "⏳ Your blood bank registration is **pending admin verification**. "
            "You will be visible on BloodSetu once approved."
        )
        return

    st.success(f"✅ Verified Blood Bank — Welcome, **{bank['name']}**!")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🩸 Availability",
        "📅 Donor Slots",
        "🔍 Find Donors",
        "📣 Announce Event",
        "🚩 Reports",
    ])

    with tab1:
        _availability_tab(bank)
    with tab2:
        _slots_tab(bank)
    with tab3:
        _find_donors_tab(bank)
    with tab4:
        _announce_tab(bank)
    with tab5:
        show_report_button("Blood Bank", bank["id"], f"bank_{bank['id']}")


def _availability_tab(bank):
    st.markdown("### 🩸 Update Blood Availability")

    if bank.get("last_updated"):
        last = date.fromisoformat(bank["last_updated"])
        days_since = (date.today() - last).days
        if days_since > 15:
            st.error(
                f"⚠️ Last updated **{days_since} days ago**. "
                "Please update your availability — it may be outdated!"
            )
        else:
            st.info(f"Last updated: **{bank['last_updated']}** ({days_since} days ago)")

    current = bank.get("groups_available", "") or ""
    current_groups = [g.strip() for g in current.split(",") if g.strip()]

    available = st.multiselect(
        "Blood groups currently in stock:",
        ALL_BLOOD_GROUPS,
        default=current_groups
    )

    if st.button("💾 Update Availability", use_container_width=True):
        from database import get_conn
        conn = get_conn()
        today = date.today().isoformat()
        conn.execute(
            "UPDATE blood_banks SET groups_available=?, last_updated=? WHERE id=?",
            (",".join(available), today, bank["id"])
        )
        conn.commit()
        conn.close()
        st.success("✅ Availability updated!")
        st.rerun()


def _slots_tab(bank):
    st.markdown("### 📅 Donor Slots")

    from database import get_conn
    conn = get_conn()
    slots = conn.execute("""
        SELECT ds.*, d.name as donor_name, d.blood_group,
               d.phone as donor_phone, d.area as donor_area
        FROM donation_slots ds
        JOIN donors d ON ds.donor_id = d.id
        WHERE ds.location_type='Blood Bank' AND ds.location_id=?
        AND ds.status != 'Cancelled'
        ORDER BY ds.slot_date ASC
    """, (bank["id"],)).fetchall()
    conn.close()

    if not slots:
        st.info("No donor slots booked yet.")
        return

    st.markdown(f"**{len(slots)} upcoming slot(s):**")
    for slot in [dict(s) for s in slots]:
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
                if st.button("✅ Mark Done", key=f"bank_done_{slot['id']}"):
                    confirm_donation(
                        slot["donor_id"], "Blood Bank",
                        bank["id"], bank["name"]
                    )
                    st.success("Donation confirmed!")
                    st.rerun()


def _find_donors_tab(bank):
    st.markdown("### 🔍 Find Eligible Donors")
    col1, col2 = st.columns(2)
    with col1:
        bg = st.selectbox("Blood Group", ALL_BLOOD_GROUPS, key="bb_find_bg")
    with col2:
        city = st.selectbox(
            "City", GUJARAT_CITIES,
            index=GUJARAT_CITIES.index(bank["city"])
            if bank["city"] in GUJARAT_CITIES else 0,
            key="bb_find_city"
        )
    areas = get_areas(city)
    area = st.selectbox("Area", areas if areas else ["—"], key="bb_find_area")

    if st.button("🔍 Find Donors", use_container_width=True, key="bb_find_btn"):
        compatible = get_compatible_groups(bg)
        donors = get_eligible_donors(compatible, city, area)
        if donors:
            st.success(f"✅ Found {len(donors)} eligible donor(s):")
            for d in donors:
                st.markdown(f"""
                <div class='result-card'>
                  <h4>🩸 {d["name"]} — {d["blood_group"]}</h4>
                  <p>📍 {d["area"]}, {d["city"]}</p>
                  <p style='color:#f0c040'>📞 {d["phone"]}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No eligible donors found right now.")


def _announce_tab(bank):
    st.markdown("### 📣 Announce Blood Donation Drive")
    with st.form("bb_announce_form"):
        event_date = st.date_input("📅 Event Date", min_value=date.today())
        timings    = st.text_input("⏰ Timings", placeholder="e.g. 10AM – 3PM")
        submitted  = st.form_submit_button(
            "📣 Generate WhatsApp Message", use_container_width=True
        )

    if submitted:
        msg = wa_event_message(
            bank["name"], bank["city"], bank["area"],
            str(event_date), timings,
            bank.get("doctor_name", "Bank Team"), bank["phone"]
        )
        st.code(msg, language=None)
        st.caption("Copy and share on WhatsApp")


def _register_flow():
    success, user_id = register_form("blood_bank")
    if success and user_id:
        _complete_profile(user_id)


def _complete_profile(user_id):
    st.markdown("### 🏦 Complete Blood Bank Profile")
    with st.form("bb_profile_form"):
        name   = st.text_input("Blood Bank Name *")
        doctor = st.text_input("Director / Doctor Name *")
        city   = st.selectbox("City *", GUJARAT_CITIES)
        areas  = get_areas(city)
        area   = st.selectbox("Area *", areas if areas else ["—"])
        phone  = st.text_input("Contact Number *")

        if st.form_submit_button("📝 Submit for Verification", use_container_width=True):
            if name and doctor and phone:
                register_blood_bank(user_id, name, doctor, city, area, phone)
                st.success(
                    "✅ Registration submitted! Admin will verify within 24–48 hours."
                )
            else:
                st.warning("Please fill all required fields.")
                