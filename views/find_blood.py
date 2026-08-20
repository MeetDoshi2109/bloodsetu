"""
pages/find_blood.py — BloodSetu 5-Tier Search Page
Complete cascading search T1 → T5 with animation and privacy safeguards
"""

import streamlit as st
import time
from database import post_sos
from ml_model import tier_search
from utils import (GUJARAT_CITIES, get_areas, ALL_BLOOD_GROUPS,
                   wa_sos_message, get_compatible_groups, get_msg)
from map_handler import build_map, show_map


def show():
    st.markdown("""
    <div class='sec-header'>🔍 Find Blood — Gujarat Network</div>
    <p class='sec-sub'>No login required. Search across all hospitals, blood banks, camps and verified donors instantly.</p>
    """, unsafe_allow_html=True)

    # ── SEARCH FORM ────────────────────────────────────────
    with st.form("find_blood_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            blood_group = st.selectbox(
                "🩸 Blood Group Needed",
                ALL_BLOOD_GROUPS,
                index=ALL_BLOOD_GROUPS.index(
                    st.session_state.get("search_bg", "B+")
                ) if st.session_state.get("search_bg") in ALL_BLOOD_GROUPS else 0
            )
        with col2:
            city = st.selectbox(
                "📍 Select City",
                GUJARAT_CITIES,
                index=GUJARAT_CITIES.index(
                    st.session_state.get("search_city", "Vadodara")
                ) if st.session_state.get("search_city") in GUJARAT_CITIES else 0
            )
        with col3:
            areas = get_areas(city)
            area = st.selectbox("📍 Select Area", areas if areas else ["—"])

        confirm = st.checkbox(
            f"✅ Confirm: I need blood in **{area}, {city}**",
            value=True
        )
        urgency = st.radio(
            "⚡ Urgency Level",
            ["🔴 Critical", "🟡 Urgent", "🟢 Planned"],
            horizontal=True
        )
        search_btn = st.form_submit_button(
            "🔍 Start 5-Tier Search",
            use_container_width=True
        )

    if not search_btn and "search_bg" not in st.session_state:
        _show_compatible_hint(blood_group)
        return

    if not confirm:
        st.warning("Please confirm your location before searching.")
        return

    # ── ANIMATED LOADER ────────────────────────────────────
    st.markdown(f"""
    <div class='msg-box'>
      <b>{get_msg("search_loading","en")}</b><br>
      <span style='color:rgba(255,255,255,0.45)'>{get_msg("search_loading","gu")}</span>
    </div>
    """, unsafe_allow_html=True)

    progress = st.progress(0)
    status_txt = st.empty()

    steps = [
        (25,  "🏥 T1: Searching nearest verified hospitals..."),
        (50,  "🏦 T2: Querying blood bank inventories..."),
        (75,  "🏕️ T3: Checking upcoming local blood donation drives..."),
        (100, "🩸 T4: Matching eligible donors using KNN algorithm..."),
    ]
    for pct, msg in steps:
        status_txt.markdown(f"<p style='color:#e74c3c;font-size:13px;font-weight:600'>{msg}</p>",
                            unsafe_allow_html=True)
        progress.progress(pct)
        time.sleep(0.3)

    status_txt.empty()
    progress.empty()

    # ── TIER SEARCH ────────────────────────────────────────
    results = tier_search(blood_group, city, area)
    found_at = results["found_at"]

    # ── SEEKER DETAILS FORM ────────────────────────────────
    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='form-glass'>
      <h4 style='color:#f0c040;font-family:"Playfair Display",serif;margin:0 0 6px'>
        📋 Seeker Verification Form
      </h4>
      <p style='font-size:12px;color:rgba(255,255,255,0.55);margin:0 0 14px'>
        Please provide your contact details to unlock full contact phone numbers.
      </p>
    """, unsafe_allow_html=True)

    with st.form("seeker_details_form"):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            s_name  = st.text_input("Your Name *")
        with sc2:
            s_phone = st.text_input("Your Phone Number * (10 digits)")
        with sc3:
            s_area  = st.text_input("Your Current Location Area *", value=area)
        reveal = st.form_submit_button(
            "🔓 Unlock Provider & Donor Contact Numbers",
            use_container_width=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if not reveal and "seeker_revealed" not in st.session_state:
        return

    if reveal:
        if not s_name or not s_phone or not s_area or len(s_phone) != 10:
            st.warning("Please enter a valid name, 10-digit phone number, and location area.")
            return
        st.session_state["seeker_revealed"] = True
        st.session_state["s_name"] = s_name
        st.session_state["s_phone"] = s_phone
        st.session_state["s_area"] = s_area

        # Post active SOS record
        post_sos(blood_group, city, area, s_name, s_phone,
                 urgency.split()[1] if " " in urgency else urgency)

    s_name = st.session_state.get("s_name", "")
    s_phone = st.session_state.get("s_phone", "")
    s_area = st.session_state.get("s_area", "")

    # ── SHOW RESULTS ───────────────────────────────────────
    _show_results(results, found_at, blood_group, city, area,
                  s_name, s_phone, s_area, urgency)


def _show_compatible_hint(blood_group: str):
    compatible = get_compatible_groups(blood_group)
    if len(compatible) > 1:
        st.info(
            f"💡 **Compatibility Rule Active:** Searching for **{blood_group}** "
            f"automatically includes compatible groups: **{', '.join(compatible)}**."
        )


def _show_results(results, found_at, blood_group, city, area,
                  s_name, s_phone, s_area, urgency):

    # T1 — Hospitals
    if results["T1_hospitals"]:
        st.markdown("""
        <div class='msg-box-success'>
          ✅ <b>Match Found at Tier 1 (Hospitals)! Reach out immediately.</b><br>
          <span style='color:rgba(255,255,255,0.5)'>આશા મળી. સિવિલ અથવા ખાનગી હોસ્પિટલમાં જથ્થો ઉપલબ્ધ છે. ❤️</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style='background:rgba(41,128,185,0.12);border-left:4px solid #2980b9;
        border-radius:8px;padding:8px 14px;margin-bottom:14px'>
          <span style='color:#5dade2;font-weight:700;font-size:12px;letter-spacing:1px'>
          🏥 TIER 1 · VERIFIED HOSPITALS</span>
        </div>
        """, unsafe_allow_html=True)
        for h in results["T1_hospitals"]:
            _hospital_card(h, s_name, s_phone, s_area)

    # T2 — Blood Banks
    if results["T2_banks"]:
        st.markdown("""
        <div style='background:rgba(46,204,113,0.12);border-left:4px solid #27ae60;
        border-radius:8px;padding:8px 14px;margin-bottom:14px'>
          <span style='color:#2ecc71;font-weight:700;font-size:12px;letter-spacing:1px'>
          🏦 TIER 2 · REGISTERED BLOOD BANKS</span>
        </div>
        """, unsafe_allow_html=True)
        for b in results["T2_banks"]:
            _bank_card(b, s_name, s_phone, s_area)

    # T3 — Camps
    if results["T3_camps"]:
        st.markdown("""
        <div style='background:rgba(230,126,34,0.12);border-left:4px solid #e67e22;
        border-radius:8px;padding:8px 14px;margin-bottom:14px'>
          <span style='color:#e67e22;font-weight:700;font-size:12px;letter-spacing:1px'>
          🏕️ TIER 3 · ACTIVE BLOOD CAMPS</span>
        </div>
        """, unsafe_allow_html=True)
        for c in results["T3_camps"]:
            _camp_card(c, s_name, s_phone, s_area)

    # T4 — Donors
    if results["T4_donors"]:
        st.markdown("""
        <div style='background:rgba(192,57,43,0.12);border-left:4px solid #c0392b;
        border-radius:8px;padding:8px 14px;margin-bottom:14px'>
          <span style='color:#e74c3c;font-weight:700;font-size:12px;letter-spacing:1px'>
          🩸 TIER 4 · EMERGENCY COMMUNITY DONORS (KNN RANKED)</span>
        </div>
        """, unsafe_allow_html=True)
        st.warning(
            "⏱️ **Privacy & Security Window:** Donor numbers are displayed for emergency use only. "
            "Please call with respect and care."
        )
        shown = set()
        for d in results["T4_donors"]:
            if d["id"] not in shown:
                shown.add(d["id"])
                _donor_card(d, s_name, s_phone, s_area)

    # T5 — WhatsApp SOS
    if found_at == "T5":
        st.markdown("""
        <div class='msg-box'>
          <b>No direct stock found in system. Generating Emergency WhatsApp SOS Broadcast...</b><br>
          <span style='color:rgba(255,255,255,0.45)'>અમે બધે શોધ્યું. આ SOS મેસેજ તમારા ગ્રુપમાં શેર કરો. ❤️</span>
        </div>
        """, unsafe_allow_html=True)
        msg = wa_sos_message(blood_group, area, city, s_phone)
        st.markdown("<div class='wa-box'>", unsafe_allow_html=True)
        st.code(msg, language=None)
        st.markdown("</div>", unsafe_allow_html=True)
        st.info("📋 Copy the text above and broadcast to your WhatsApp contacts and groups immediately.")

    # MAP VIEW
    if found_at != "T5":
        st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)
        st.markdown("### 🗺️ Geographic Location Pins")
        m = build_map(
            area, city,
            hospitals=results["T1_hospitals"] or None,
            banks=results["T2_banks"] or None,
            camps=results["T3_camps"] or None,
            donors=results["T4_donors"] or None,
        )
        show_map(m, height=420)


def _hospital_card(h, s_name, s_phone, s_area):
    st.markdown(f"""
    <div class='result-card'>
      <h4>🏥 {h["name"]} <span class='tag-verified'>Verified</span></h4>
      <p>👨‍⚕️ <b>Doctor:</b> {h.get("doctor_name","—")} &nbsp;|&nbsp; 📍 <b>Address:</b> {h["area"]}, {h["city"]}</p>
      <p>🩸 <b>Stock Available:</b> <b style='color:#e74c3c'>{h.get("blood_available","—")}</b></p>
      <p>⏰ <b>24×7 Emergency:</b> {"✅ Available" if h["emergency_24x7"] else "❌ Standard Hours"}</p>
      <p style='color:#f0c040;font-size:15px !important;font-weight:700;margin-top:6px !important'>📞 Contact: {h["phone"]}</p>
    </div>
    """, unsafe_allow_html=True)


def _bank_card(b, s_name, s_phone, s_area):
    st.markdown(f"""
    <div class='result-card'>
      <h4>🏦 {b["name"]} <span class='tag-verified'>Verified</span></h4>
      <p>👨‍⚕️ <b>Director:</b> {b.get("doctor_name","—")} &nbsp;|&nbsp; 📍 <b>Location:</b> {b["area"]}, {b["city"]}</p>
      <p>🩸 <b>Blood Groups Stocked:</b> <b style='color:#e74c3c'>{b.get("groups_available","—")}</b></p>
      <p style='color:#f0c040;font-size:15px !important;font-weight:700;margin-top:6px !important'>📞 Contact: {b["phone"]}</p>
    </div>
    """, unsafe_allow_html=True)


def _camp_card(c, s_name, s_phone, s_area):
    st.markdown(f"""
    <div class='result-card'>
      <h4>🏕️ {c["organizer"]} <span class='tag-verified'>Verified Drive</span></h4>
      <p>👨‍⚕️ <b>Organizer:</b> {c.get("doctor_name","—")} &nbsp;|&nbsp; 📍 <b>Venue:</b> {c["area"]}, {c["city"]}</p>
      <p>📅 <b>Date:</b> {c["camp_date"]} &nbsp;|&nbsp; ⏰ <b>Timings:</b> {c.get("timings","—")}</p>
      <p style='color:#f0c040;font-size:15px !important;font-weight:700;margin-top:6px !important'>📞 Contact: {c["phone"]}</p>
    </div>
    """, unsafe_allow_html=True)


def _donor_card(d, s_name, s_phone, s_area):
    st.markdown(f"""
    <div class='result-card' style='border-left-color:#e74c3c'>
      <h4>🩸 {d["name"]} <span class='badge-pill badge-earned'>Matched Donor</span></h4>
      <p>💉 <b>Blood Group:</b> <b style='color:#e74c3c'>{d["blood_group"]}</b> &nbsp;|&nbsp; 📍 <b>Area:</b> {d["area"]}, {d["city"]}</p>
      <p>💉 <b>Donations Given:</b> {d.get("donations_count", 0)} times</p>
      <p style='color:#f0c040;font-size:15px !important;font-weight:700;margin-top:6px !important'>📞 Phone: {d["phone"]}</p>
    </div>
    """, unsafe_allow_html=True)