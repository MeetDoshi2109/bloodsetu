"""
app.py — BloodSetu Main Entry Point
Smart Blood Network Portal — All Gujarat
Mini Project-II | Python with AI, ML, DS
BCA (Hons) | Parul University
"""

import streamlit as st
import os
from database import init_db
from auth import init_session

# ── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="BloodSetu — Connect Blood. Save Lives.",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Export handler / app variable for serverless deployment
app = st
application = st
handler = st


# ── LOAD CSS ───────────────────────────────────────────────
css_path = os.path.join("assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── INIT DATABASE & SESSION ────────────────────────────────
init_db()
init_session()

# ── SIDEBAR NAVIGATION ─────────────────────────────────────
with st.sidebar:
    # Logo + mascot with glowing animation
    st.markdown("""
    <div style='text-align:center;padding:16px 0 12px'>
      <svg width='76' height='90' viewBox='0 0 80 96' fill='none'
           style='animation:float 3.5s ease-in-out infinite;filter:drop-shadow(0 0 16px rgba(231,76,60,0.85))'>
        <path d='M40 8C40 8 8 44 8 64C8 82 22 88 40 88C58 88 72 82 72 64C72 44 40 8 40 8Z'
              fill='url(#sg)'/>
        <circle cx='30' cy='60' r='6' fill='white' opacity='.95'/>
        <circle cx='50' cy='60' r='6' fill='white' opacity='.95'/>
        <circle cx='31.5' cy='58.5' r='2.5' fill='#1a0505'/>
        <circle cx='51.5' cy='58.5' r='2.5' fill='#1a0505'/>
        <circle cx='32.5' cy='57.5' r='1' fill='white'/>
        <circle cx='52.5' cy='57.5' r='1' fill='white'/>
        <path d='M30 70 Q40 78 50 70' stroke='white' stroke-width='2.5'
              fill='none' stroke-linecap='round'/>
        <circle cx='24' cy='66' r='5' fill='#ff9999' opacity='.45'/>
        <circle cx='56' cy='66' r='5' fill='#ff9999' opacity='.45'/>
        <defs>
          <linearGradient id='sg' x1='40' y1='8' x2='40' y2='88'
                          gradientUnits='userSpaceOnUse'>
            <stop offset='0%' stop-color='#ff4b4b'/>
            <stop offset='50%' stop-color='#e74c3c'/>
            <stop offset='100%' stop-color='#7b241c'/>
          </linearGradient>
        </defs>
      </svg>
      <div style='font-family:"Playfair Display",serif;font-size:24px;
                  font-weight:900;color:white;margin-top:10px;letter-spacing:1px'>BloodSetu</div>
      <div style='font-size:10px;color:rgba(255,255,255,0.45);
                  letter-spacing:2px;text-transform:uppercase;font-weight:600;margin-top:2px'>
        Connect Blood. Save Lives.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='height:1px;background:linear-gradient(90deg,transparent,
    rgba(231,76,60,0.4),transparent);margin:8px 0 16px'></div>
    """, unsafe_allow_html=True)

    # Navigation pages map
    pages = {
        "🏠 Home":              "Home",
        "🔍 Find Blood":        "Find Blood",
        "✅ Eligibility Check": "Eligibility",
        "🗺️ Map View":          "Map",
        "📊 Analytics":         "Analytics",
        "🏆 Daata Wall":        "Daata Wall",
        "🩸 Donor Portal":      "Donor",
        "🏥 Hospital Portal":   "Hospital",
        "🏦 Blood Bank Portal": "Blood Bank",
        "🏕️ Blood Camp Portal": "Camp",
        "👑 Admin Panel":       "Admin",
    }

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    for label, page_key in pages.items():
        is_active = st.session_state.current_page == page_key
        if st.button(
            label,
            key=f"nav_{page_key}",
            use_container_width=True,
        ):
            st.session_state.current_page = page_key
            st.rerun()

    st.markdown("""
    <div style='height:1px;background:linear-gradient(90deg,transparent,
    rgba(231,76,60,0.3),transparent);margin:16px 0 14px'></div>
    """, unsafe_allow_html=True)

    # Login status card
    if st.session_state.get("logged_in"):
        user = st.session_state.get("user", {})
        role = st.session_state.get("role", "")
        st.markdown(f"""
        <div style='background:rgba(46,204,113,0.08);border:1px solid rgba(46,204,113,0.25);
        border-radius:12px;padding:12px;text-align:center;backdrop-filter:blur(8px)'>
          <p style='color:#2ecc71;font-weight:600;font-size:11px;margin:0;letter-spacing:1px;text-transform:uppercase'>
          ✅ Logged in as</p>
          <p style='color:white;font-size:14px;font-weight:700;margin:3px 0 1px'>
          {user.get("username","")}</p>
          <p style='color:rgba(255,255,255,0.5);font-size:10px;
                    text-transform:uppercase;margin:0;font-weight:600'>{role}</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            from auth import logout
            logout()
            st.session_state.current_page = "Home"
            st.rerun()
    else:
        st.markdown("""
        <p style='font-size:11px;color:rgba(255,255,255,0.4);
                   text-align:center;margin:0;line-height:1.5'>
        Seekers need no login 🩸<br><span style='color:rgba(255,255,255,0.25)'>Login for donors & providers</span></p>
        """, unsafe_allow_html=True)

    # SOS quick button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚨 EMERGENCY SOS", use_container_width=True, key="sidebar_sos"):
        st.session_state.current_page = "Find Blood"
        st.rerun()

    # Footer
    st.markdown("""
    <div style='margin-top:24px;text-align:center;font-size:10px;
                color:rgba(255,255,255,0.25);line-height:1.6'>
      BloodSetu · Parul University<br>
      BCA (Hons) · Mini Project-II<br>
      📧 bloodsetu.help@gmail.com
    </div>
    """, unsafe_allow_html=True)

# ── PAGE ROUTER ────────────────────────────────────────────
page = st.session_state.current_page

if page == "Home":
    from pages.home import show
    show()

elif page == "Find Blood":
    from pages.find_blood import show
    show()

elif page == "Eligibility":
    from pages.eligibility import show
    show()

elif page == "Map":
    from map_handler import build_map, show_map
    from database import get_all_hospitals, get_all_blood_banks, get_all_camps
    from utils import GUJARAT_CITIES, get_areas

    st.markdown("""
    <div class='sec-header'>🗺️ Map View</div>
    <p class='sec-sub'>See all verified hospitals, blood banks and camps across Gujarat</p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        city = st.selectbox("Select City", GUJARAT_CITIES, key="map_city")
    with col2:
        areas = get_areas(city)
        area  = st.selectbox("Select Area", areas if areas else ["—"], key="map_area")

    hospitals = get_all_hospitals()
    banks     = get_all_blood_banks()
    camps     = get_all_camps()

    city_hospitals = [h for h in hospitals if h["city"] == city]
    city_banks     = [b for b in banks     if b["city"] == city]
    city_camps     = [c for c in camps     if c["city"] == city]

    m = build_map(
        area, city,
        hospitals=city_hospitals or None,
        banks=city_banks or None,
        camps=city_camps or None,
        zoom=12,
    )
    show_map(m, height=520)

    col1, col2, col3 = st.columns(3)
    col1.metric("🏥 Hospitals", len(city_hospitals))
    col2.metric("🏦 Blood Banks", len(city_banks))
    col3.metric("🏕️ Camps", len(city_camps))

elif page == "Analytics":
    from pages.analytics import show
    show()

elif page == "Daata Wall":
    from pages.daata_wall import show
    show()

elif page == "Donor":
    from pages.donor import show
    show()

elif page == "Hospital":
    from pages.hospital import show
    show()

elif page == "Blood Bank":
    from pages.blood_bank import show
    show()

elif page == "Camp":
    from pages.camp import show
    show()

elif page == "Admin":
    from pages.admin import show
    show()