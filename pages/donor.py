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
    <div class='sec-header'>🩸 Donor Portal</div>
    <p class='sec-sub'>Your personal blood donation hub</p>
    """, unsafe_allow_html=True)

    # Check login
    if not require_login("donor"):
        st.markdown("---")
        st.markdown("### 📝 New donor? Register here")
        _register_flow()
        return

    user = current_user()
    donor = get_donor_by_user(user["id"])

    if not donor:
        st.warning("Please complete your donor profile first.")
        _complete_profile(user["id"])
        return

    # ── DASHBOARD ─────────────────────────────────────────
    _profile_card(donor)
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "⏳ Eligibility",
        "📅 Upcoming Slots",
        "📊 History",
        "🚨 SOS Near Me",
        "🏆 Badges",
        "⚙️ Settings",
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
    border-radius:12px;padding:16px;text-align:center'>
      <div style='font-size:32px;margin-bottom:6px'>🩸</div>
      <div style='font-family:Playfair Display,serif;font-size:18px;
                  font-weight:700;color:white'>{donor["name"]}</div>
      <div style='font-size:13px;color:#e74c3c;font-weight:600'>
          {donor["blood_group"]}</div>
      <div style='font-size:11px;color:rgba(255,255,255,0.5);margin-top:4px'>
          📍 {donor["area"]}, {donor["city"]}</div>
    </div>
    """, unsafe_allow_html=True)

    col2.metric("💉 Total Donations", donor["donations_count"])
    col3.metric("❤️ Lives Potentially Saved", lives)
    col4.metric(
        "⏳ Eligibility",
        "✅ Eligible" if is_elig else f"⏳ {days_rem} days"
    )

    # Status toggle
    st.markdown("<br>", unsafe_allow_html=True)
    new_status = st.radio(
        "🟢 Your Availability Status",
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
          <span style='color:rgba(255,255,255,0.4)'>{get_msg("eligible_again","gu")}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='msg-box'>
          ⏳ Your body is preparing for its next act of heroism.<br>
          <b style='color:#e74c3c'>{days_rem} days</b> remaining until
          you can donate again. We're counting down with you. ❤️<br>
          <span style='color:rgba(255,255,255,0.4)'>
          તમારું શરીર આગામી વીર કાર્ય માટે તૈયાર થઈ રહ્યું છે.</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class='progress-wrap'>
      <div class='progress-fill' style='width:{pct}%'></div>
    </div>
    <p style='font-size:11px;color:rgba(255,255,255,0.4);margin-top:4px'>
    WHO 90-day rule · {pct:.0f}% complete</p>
    """.format(pct=progress*100), unsafe_allow_html=True)

    if donor.get("next_eligible"):
        st.info(f"📅 Next eligible date: **{donor['next_eligible']}**")

    if is_elig:
        st.markdown("---")
        st.markdown("**📅 Book a donation slot now:**")
        _book_slot_form(donor)


# ── SLOTS TAB ─────────────────────────────────────────────
def _slots_tab(donor):
    st.markdown("### 📅 Upcoming Donation Slots")
    slots = get_donor_slots(donor["id"])

    if not slots:
        st.info("No upcoming slots. Book one below!")
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
              <p style='font-size:14px;font-weight:600;color:white;margin:0 0 6px'>
                {icon} {loc_type} Slot</p>
              <p style='font-size:12px;color:rgba(255,255,255,0.5);margin:0'>
                📅 {slot["slot_date"]} &nbsp;|&nbsp; ⏰ {slot["slot_time"]}</p>
              <p style='font-size:11px;margin:4px 0 0'>
                Status: <span style='color:{status_color};font-weight:600'>
                {slot["status"]}</span></p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if slot["status"] == "Pending":
                if st.button("❌ Cancel", key=f"cancel_{slot['id']}"):
                    cancel_slot(slot["id"])
                    st.success("Slot cancelled. Hospital has been notified.")
                    st.rerun()

    st.markdown("---")
    st.markdown("**➕ Book Another Slot:**")
    _book_slot_form(donor)


def _book_slot_form(donor):
    st.markdown("""
    <div style='background:rgba(255,255,255,0.03);border:1px solid rgba(192,57,43,0.2);
    border-radius:12px;padding:18px'>
    """, unsafe_allow_html=True)

    loc_type = st.selectbox(
        "Where do you want to donate?",
        ["Hospital", "Blood Bank", "Blood Camp"],
        key="slot_loc_type"
    )

    loc_id = None
    loc_name = ""

    if loc_type == "Hospital":
        hospitals = get_all_hospitals()
        options = {f"🏥 {h['name']} — {h['area']}, {h['city']}": h["id"]
                   for h in hospitals}
        sel = st.selectbox("Select Hospital", list(options.keys()), key="slot_hosp")
        if sel:
            loc_id = options[sel]
            loc_name = sel

    elif loc_type == "Blood Bank":
        banks = get_all_blood_banks()
        options = {f"🏦 {b['name']} — {b['area']}, {b['city']}": b["id"]
                   for b in banks}
        sel = st.selectbox("Select Blood Bank", list(options.keys()), key="slot_bank")
        if sel:
            loc_id = options[sel]
            loc_name = sel

    else:
        camps = get_all_camps()
        options = {f"🏕️ {c['organizer']} — {c['camp_date']}": c["id"]
                   for c in camps}
        if options:
            sel = st.selectbox("Select Camp", list(options.keys()), key="slot_camp")
            if sel:
                loc_id = options[sel]
                loc_name = sel
        else:
            st.info("No upcoming camps available.")

    slot_date = st.date_input(
        "📅 Preferred Date",
        min_value=date.today(),
        value=date.today() + timedelta(days=1),
        key="slot_date"
    )
    slot_time = st.selectbox(
        "⏰ Preferred Time",
        ["Morning (9AM – 12PM)", "Afternoon (12PM – 4PM)", "Evening (4PM – 7PM)"],
        key="slot_time"
    )

    if st.button("📅 Book Slot", use_container_width=True, key="book_slot_btn"):
        if loc_id:
            book_slot(
                donor["id"], loc_type, loc_id,
                slot_date.isoformat(), slot_time
            )
            st.success("✅ Slot booked!")
            st.markdown(f"""
            <div class='msg-box-success'>
              <b>{get_msg("slot_booked","en")}</b><br>
              <span style='color:rgba(255,255,255,0.4)'>
              {get_msg("slot_booked","gu")}</span>
            </div>
            """, unsafe_allow_html=True)
            st.rerun()
        else:
            st.warning("Please select a location first.")

    st.markdown("</div>", unsafe_allow_html=True)


# ── HISTORY TAB ───────────────────────────────────────────
def _history_tab(donor):
    st.markdown("### 📊 Donation History")
    donations = get_donor_donations(donor["id"])

    if not donations:
        st.info("No confirmed donations yet. Book your first slot! 🩸")
        return

    for d in donations:
        lives = 3
        st.markdown(f"""
        <div class='bs-card'>
          <p style='font-size:13px;font-weight:600;color:white;margin:0 0 4px'>
            ✅ {d["donation_date"]}
            &nbsp;—&nbsp; {d["location_name"]}</p>
          <p style='font-size:11px;color:rgba(255,255,255,0.4);margin:0'>
            Confirmed by: {d["confirmed_by_type"]} &nbsp;|&nbsp;
            ❤️ Potentially saved {lives} lives
          </p>
        </div>
        """, unsafe_allow_html=True)

    total_lives = donor["donations_count"] * 3
    st.markdown(f"""
    <div style='background:rgba(192,57,43,0.08);border:1px solid rgba(192,57,43,0.25);
    border-radius:12px;padding:16px;text-align:center;margin-top:12px'>
      <div style='font-family:Playfair Display,serif;font-size:32px;
                  color:#e74c3c'>{total_lives}</div>
      <div style='font-size:13px;color:rgba(255,255,255,0.6)'>
      Lives potentially saved by you ❤️</div>
    </div>
    """, unsafe_allow_html=True)


# ── SOS TAB ───────────────────────────────────────────────
def _sos_tab(donor):
    st.markdown("### 🚨 SOS Alerts Near You")
    is_elig, _, _ = check_eligibility(donor.get("last_donated"))

    if not is_elig:
        st.warning(
            "⏳ You are currently not eligible to donate (within 90-day period). "
            "SOS alerts are hidden to protect your health."
        )
        return

    sos_list = get_active_sos()
    nearby = [s for s in sos_list if s["city"] == donor["city"]]

    if not nearby:
        st.info("✅ No active SOS requests in your city right now.")
        return

    for s in nearby:
        urgency_color = {
            "Critical": "#e74c3c",
            "Urgent": "#f0c040",
            "Planned": "#2ecc71"
        }.get(s["urgency"], "#888")

        st.markdown(f"""
        <div class='result-card' style='border-left-color:{urgency_color}'>
          <h4>🚨 {s["blood_group"]} blood needed urgently</h4>
          <p>📍 {s["area"]}, {s["city"]} &nbsp;|&nbsp;
             ⚡ <span style='color:{urgency_color}'>{s["urgency"]}</span></p>
          <p>📞 Seeker: <b>{s["seeker_name"]}</b> — {s["seeker_phone"]}</p>
          <p style='font-size:11px;color:rgba(255,255,255,0.35)'>
          Posted: {s["posted_at"][:16]} · Expires: {s["expires_at"][:16]}</p>
        </div>
        """, unsafe_allow_html=True)


# ── BADGES TAB ────────────────────────────────────────────
def _badges_tab(donor):
    st.markdown("### 🏆 Your Badges & Achievements")
    earned = get_earned_badges(donor["donations_count"], donor["blood_group"])
    earned_ids = {b["id"] for b in earned}

    cols = st.columns(3)
    for i, badge in enumerate(BADGES):
        col = cols[i % 3]
        is_earned = badge["id"] in earned_ids
        style = "border:1px solid #f0c040;background:rgba(240,192,64,0.1)" \
                if is_earned else \
                "border:1px solid rgba(255,255,255,0.1);filter:grayscale(0.8);opacity:0.5"

        col.markdown(f"""
        <div style='{style};border-radius:14px;padding:18px;text-align:center;margin-bottom:10px'>
          <div style='font-size:32px;margin-bottom:8px'>{badge["icon"]}</div>
          <div style='font-size:13px;font-weight:700;
                      color:{"#f0c040" if is_earned else "rgba(255,255,255,0.4)"};
                      margin-bottom:4px'>{badge["name"]}</div>
          <div style='font-size:10px;color:rgba(255,255,255,0.4);margin-bottom:4px'>
            {badge["name_gu"]}</div>
          <div style='font-size:10px;color:rgba(255,255,255,0.35)'>
            {badge["condition"]}</div>
          {"<div style='color:#2ecc71;font-size:11px;margin-top:6px'>✅ Earned!</div>" if is_earned else ""}
        </div>
        """, unsafe_allow_html=True)

    if not earned:
        st.info("Make your first donation to start earning badges! 🩸")


# ── SETTINGS TAB ──────────────────────────────────────────
def _settings_tab(donor):
    st.markdown("### ⚙️ Settings")

    # Daata Wall opt-in
    from database import get_conn
    current_opt = bool(donor.get("daata_wall_opt", 0))
    new_opt = st.checkbox(
        "🏆 Show me on the Daata Wall of Honor",
        value=current_opt,
        key="daata_opt"
    )
    if new_opt != current_opt:
        conn = get_conn()
        conn.execute("UPDATE donors SET daata_wall_opt=? WHERE id=?",
                     (int(new_opt), donor["id"]))
        conn.commit()
        conn.close()
        st.success("Preference saved!")

    st.markdown("---")

    # WhatsApp awareness share
    st.markdown("**📤 Share Awareness on WhatsApp:**")
    with st.expander("Generate Awareness Message"):
        st.code(wa_awareness_message(), language=None)
        st.caption("Copy and share in your WhatsApp groups to spread awareness 🩸")

    st.markdown("---")
    st.warning(
        "⚠️ To deactivate your account, email us at: "
        "**bloodsetu.help@gmail.com**"
    )


# ── REGISTER FLOW ─────────────────────────────────────────
def _register_flow():
    success, user_id = register_form("donor")
    if success and user_id:
        _complete_profile(user_id)


def _complete_profile(user_id):
    st.markdown("### 🩸 Complete Your Donor Profile")
    st.markdown(f"""
    <div class='msg-box'>
      {get_msg("donor_welcome","en")}<br>
      <span style='color:rgba(255,255,255,0.4)'>{get_msg("donor_welcome","gu")}</span>
    </div>
    """, unsafe_allow_html=True)

    # Consent
    consent = st.checkbox(
        "✅ I agree that my name, blood group, area and phone number will be "
        "visible to blood seekers in my area for 2 hours when matched."
    )

    if not consent:
        st.info("Please read and accept the consent above to register as a donor.")
        return

    with st.form("donor_profile_form"):
        name        = st.text_input("Full Name *")
        blood_group = st.selectbox("Blood Group *", ALL_BLOOD_GROUPS)
        city        = st.selectbox("City *", GUJARAT_CITIES)
        areas       = get_areas(city)
        area        = st.selectbox("Area *", areas if areas else ["—"])
        phone       = st.text_input("Phone Number * (10 digits)")

        if st.form_submit_button("✅ Register as Donor", use_container_width=True):
            if name and phone and len(phone) == 10 and phone.isdigit():
                register_donor(user_id, name, blood_group, city, area, phone)
                st.success("✅ Profile complete! Welcome to BloodSetu family. 🩸")
                st.rerun()
            else:
                st.warning("Please fill all fields with a valid 10-digit phone number.")
                