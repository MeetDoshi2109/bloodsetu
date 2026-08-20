"""
pages/eligibility.py — Public Eligibility Checker
No login needed. WHO 90-day rule check.
"""

import streamlit as st
from datetime import date, timedelta
from utils import check_eligibility, eligibility_progress, get_msg, ALL_BLOOD_GROUPS


def show():
    st.markdown("""
    <div class='sec-header'>✅ Donor Eligibility Calculator</div>
    <p class='sec-sub'>Verify if your body is ready to donate whole blood today according to WHO guidelines.</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='msg-box'>
      <b>WHO Medical Standard (90-Day Protocol):</b> Following a whole blood donation, the body requires 90 days (3 months) to safely replenish iron stores and hemoglobin levels. BloodSetu strictly enforces this check to safeguard donor health.<br><br>
      <span style='color:rgba(255,255,255,0.45)'>
      WHO 90-દિવસ નિયમ: લોહી દાન કર્યા પછી, તમારા શરીરને હિમોગ્લોબિનનું સ્તર પૂરું કરવા 90 દિવસની જરૂર છે.
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("<div class='form-glass'>", unsafe_allow_html=True)
        st.markdown("### 📅 Check Your Status")

        blood_group = st.selectbox(
            "Select Your Blood Group",
            ALL_BLOOD_GROUPS,
            key="elig_bg"
        )

        never_donated = st.checkbox("First-time donor (Never donated whole blood before)", key="elig_never")

        last_donated = None
        if not never_donated:
            last_donated = st.date_input(
                "When was your last donation?",
                max_value=date.today(),
                value=date.today() - timedelta(days=60),
                key="elig_date"
            )

        check_btn = st.button("✅ Calculate Eligibility", use_container_width=True, key="elig_check")
        st.markdown("</div>", unsafe_allow_html=True)

        if check_btn:
            if never_donated:
                st.markdown("""
                <div class='msg-box-success'>
                  <h3 style='color:#2ecc71;margin:0 0 8px'>🎉 You are 100% Eligible!</h3>
                  <p style='margin:0'>As a first-time donor, your single donation can save up to <b>3 lives</b>!</p>
                  <p style='color:rgba(255,255,255,0.45);margin:6px 0 0'>
                  તમે પ્રથમ વાર દાન કરી રહ્યા છો — તમારું એક દાન 3 જીવ બચાવી શકે છે!
                  </p>
                </div>
                """, unsafe_allow_html=True)

            else:
                last_str = last_donated.isoformat()
                is_elig, days_since, days_rem = check_eligibility(last_str)
                progress = eligibility_progress(last_str)

                st.markdown(f"""
                <div style='margin-top:16px'>
                  <div style='display:flex;justify-content:space-between;font-size:12px;color:rgba(255,255,255,0.6);margin-bottom:4px'>
                    <span>Recovery Progress</span>
                    <span>{progress*100:.0f}%</span>
                  </div>
                  <div class='progress-wrap'>
                    <div class='progress-fill' style='width:{progress*100:.0f}%'></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                if is_elig:
                    st.markdown(f"""
                    <div class='msg-box-success'>
                      <h3 style='color:#2ecc71;margin:0 0 8px'>✅ Fully Eligible to Donate!</h3>
                      <p style='margin:0'>It has been <b>{days_since} days</b> since your last donation. Your body is fully recovered and ready!</p>
                      <p style='color:rgba(255,255,255,0.45);margin:6px 0 0'>{get_msg("eligible_again","gu")}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    next_date = (last_donated + timedelta(days=90)).isoformat()
                    st.markdown(f"""
                    <div class='msg-box'>
                      <h3 style='color:#e74c3c;margin:0 0 8px'>⏳ Recovery Period Active</h3>
                      <p style='margin:0'>Donated <b>{days_since} days ago</b>.<br>
                      Eligible to donate again in <b style='color:#e74c3c'>{days_rem} days</b>.</p>
                      <p style='color:#f0c040;margin:6px 0 0'>📅 Eligible Date: <b>{next_date}</b></p>
                    </div>
                    """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 💡 Quick Eligibility Criteria")
        facts = [
            ("🩸", "Age Requirement", "Between 18 and 65 years old"),
            ("⚖️", "Minimum Weight", "At least 45 kg for whole blood"),
            ("💉", "Hemoglobin Level", "12.5 g/dL or higher"),
            ("⏳", "Donation Frequency", "Every 90 days for males & females"),
            ("🏥", "Health Status", "Free from active infection or severe illness"),
        ]
        for icon, bold, desc in facts:
            st.markdown(f"""
            <div class='bs-card' style='display:flex;align-items:center;gap:14px;padding:14px 18px;margin-bottom:10px'>
              <span style='font-size:24px'>{icon}</span>
              <span style='font-size:13px;color:white'>
                <b style='color:#e74c3c'>{bold}:</b> {desc}</span>
            </div>
            """, unsafe_allow_html=True)

        if blood_group in ["AB-", "O-"]:
            st.markdown(f"""
            <div style='background:rgba(240,192,64,0.08);border:1px solid rgba(240,192,64,0.25);
            border-radius:14px;padding:16px;margin-top:14px'>
              <p style='color:#f0c040;font-weight:700;margin:0 0 6px'>💎 Rare Blood Type Notice ({blood_group})</p>
              <p style='font-size:12px;color:rgba(255,255,255,0.65);margin:0;line-height:1.6'>
              {blood_group} is in high demand across hospitals in Gujarat. If eligible, consider registering to receive emergency SOS alerts.
              </p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='bs-divider'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='bs-footer'>
      ✅ BloodSetu Eligibility Module · WHO Standard Compliant · Public Tool<br>
      📧 bloodsetu.help@gmail.com
    </div>
    """, unsafe_allow_html=True)