"""
pages/eligibility.py — Public Eligibility Checker
No login needed. WHO 90-day rule check.
"""

import streamlit as st
from datetime import date, timedelta
from utils import check_eligibility, eligibility_progress, get_msg, ALL_BLOOD_GROUPS


def show():
    st.markdown("""
    <div class='sec-header'>✅ Eligibility Checker</div>
    <p class='sec-sub'>Check if you can donate blood today — no login needed</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='msg-box'>
      <b>WHO 90-Day Rule:</b> After donating whole blood, your body needs at least
      90 days (3 months) to fully replenish. BloodSetu strictly follows this
      guideline to protect every donor's health. ❤️<br><br>
      <span style='color:rgba(255,255,255,0.4)'>
      WHO 90-દિવસ નિયમ: લોહી દાન કર્યા પછી, તમારા શરીરને ઓછામાં ઓછા 90 દિવસ
      (3 મહિના) ની જરૂર છે.</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 📅 Check Your Eligibility")

        blood_group = st.selectbox(
            "Your Blood Group",
            ALL_BLOOD_GROUPS,
            key="elig_bg"
        )

        never_donated = st.checkbox("I have never donated blood before", key="elig_never")

        last_donated = None
        if not never_donated:
            last_donated = st.date_input(
                "When did you last donate?",
                max_value=date.today(),
                value=date.today() - timedelta(days=60),
                key="elig_date"
            )

        if st.button("✅ Check Now", use_container_width=True, key="elig_check"):
            if never_donated:
                st.markdown("""
                <div class='msg-box-success'>
                  <h3 style='color:#2ecc71;margin:0 0 8px'>✅ You are eligible!</h3>
                  <p style='margin:0'>You have never donated before — your first donation
                  can save up to 3 lives!</p>
                  <p style='color:rgba(255,255,255,0.4);margin:6px 0 0'>
                  તમે ક્યારેય દાન કર્યું નથી — તમારું પ્રથમ દાન 3 જીવ બચાવી શકે છે!</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                <div class='msg-box'>
                  <b>Ready to be a hero?</b><br>
                  Register as a donor on BloodSetu and save lives across Gujarat. 🩸
                </div>
                """, unsafe_allow_html=True)

            else:
                last_str = last_donated.isoformat()
                is_elig, days_since, days_rem = check_eligibility(last_str)
                progress = eligibility_progress(last_str)

                st.markdown(f"""
                <div class='progress-wrap'>
                  <div class='progress-fill' style='width:{progress*100:.0f}%'></div>
                </div>
                <p style='font-size:11px;color:rgba(255,255,255,0.4);margin:4px 0 12px'>
                {progress*100:.0f}% of 90-day recovery complete</p>
                """, unsafe_allow_html=True)

                if is_elig:
                    st.markdown(f"""
                    <div class='msg-box-success'>
                      <h3 style='color:#2ecc71;margin:0 0 8px'>✅ You are eligible!</h3>
                      <p style='margin:0'>It has been <b>{days_since} days</b>
                      since your last donation. Your body is ready!</p>
                      <p style='color:rgba(255,255,255,0.4);margin:6px 0 0'>
                      {get_msg("eligible_again","gu")}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    next_date = (last_donated + timedelta(days=90)).isoformat()
                    st.markdown(f"""
                    <div class='msg-box'>
                      <h3 style='color:#e74c3c;margin:0 0 8px'>
                      ⏳ Not yet eligible</h3>
                      <p style='margin:0'>It has been <b>{days_since} days</b>
                      since your last donation.<br>
                      You can donate again in
                      <b style='color:#e74c3c'>{days_rem} more days</b>.</p>
                      <p style='color:#f0c040;margin:6px 0 0'>
                      📅 Your next eligible date: <b>{next_date}</b></p>
                      <p style='color:rgba(255,255,255,0.4);margin:6px 0 0'>
                      તમારું શરીર આગામી વીર કાર્ય માટે તૈયાર થઈ રહ્યું છે. ❤️</p>
                    </div>
                    """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 💡 Did You Know?")
        facts = [
            ("🩸", "Every 2 seconds", "someone in India needs blood"),
            ("💉", "1 donation", "can save up to 3 lives"),
            ("⏳", "Only 90 days", "between whole blood donations"),
            ("👥", "Only 7%", "of eligible Indians donate blood"),
            ("🏥", "Whole blood", "is the most common donation type"),
            ("✅", "Age 18–65", "is the eligibility range for donors"),
        ]
        for icon, bold, desc in facts:
            st.markdown(f"""
            <div style='background:rgba(255,255,255,0.03);
            border:1px solid rgba(192,57,43,0.18);border-radius:10px;
            padding:12px 14px;margin-bottom:8px;display:flex;
            align-items:center;gap:12px'>
              <span style='font-size:20px'>{icon}</span>
              <span style='font-size:13px;color:white'>
                <b style='color:#e74c3c'>{bold}</b> {desc}</span>
            </div>
            """, unsafe_allow_html=True)

        if blood_group in ["AB-", "O-"]:
            st.markdown(f"""
            <div style='background:rgba(240,192,64,0.08);
            border:1px solid rgba(240,192,64,0.3);border-radius:12px;
            padding:14px;margin-top:10px'>
              <p style='color:#f0c040;font-weight:700;margin:0 0 6px'>
              💎 Rare Blood Group Alert!</p>
              <p style='font-size:12px;color:rgba(255,255,255,0.6);margin:0'>
              {blood_group} is one of the rarest blood groups.
              Only a small percentage of people have it.
              If you are eligible, please consider registering as a donor —
              you could save lives nobody else can. 🙏</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # CTA to register
    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(192,57,43,0.15),rgba(192,57,43,0.05));
    border:1px solid rgba(192,57,43,0.25);border-radius:14px;
    padding:24px;text-align:center;margin-top:10px'>
      <p style='font-family:Playfair Display,serif;font-size:20px;
                color:white;margin:0 0 8px'>Ready to be someone's miracle?</p>
      <p style='font-size:13px;color:rgba(255,255,255,0.5);margin:0 0 16px'>
        Register as a donor on BloodSetu and join Gujarat's network of heroes. 🩸<br>
        <span style='color:rgba(255,255,255,0.3)'>
        BloodSetu ઉપર ડૉનર તરીકે નોંધણી કરો.</span>
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='bs-footer'>
      ✅ BloodSetu Eligibility Checker · WHO 90-Day Standard · No Login Needed<br>
      📧 bloodsetu.help@gmail.com
    </div>
    """, unsafe_allow_html=True)
    