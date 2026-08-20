"""
utils.py — BloodSetu Helper Functions
Blood compatibility, WhatsApp messages, area data, eligibility
"""

from datetime import date, timedelta

# ══════════════════════════════════════════
# BLOOD COMPATIBILITY MAP
# ══════════════════════════════════════════
COMPATIBILITY = {
    "A+":  ["A+", "A-", "O+", "O-"],
    "A-":  ["A-", "O-"],
    "B+":  ["B+", "B-", "O+", "O-"],
    "B-":  ["B-", "O-"],
    "O+":  ["O+", "O-"],
    "O-":  ["O-"],
    "AB+": ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"],
    "AB-": ["A-", "B-", "O-", "AB-"],
}

ALL_BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]


def get_compatible_groups(blood_group: str) -> list:
    """Return list of blood groups compatible as donors for the given group."""
    return COMPATIBILITY.get(blood_group, [blood_group])


# ══════════════════════════════════════════
# GUJARAT AREAS DATA
# ══════════════════════════════════════════
GUJARAT_AREAS = {
    "Ahmedabad": [
        "Satellite", "Bopal", "Maninagar", "Vastrapur", "Navrangpura",
        "SG Highway", "Gota", "Chandkheda", "Prahlad Nagar", "Thaltej",
        "Ambawadi", "Paldi", "Ellis Bridge", "Shahibaug", "Nikol"
    ],
    "Vadodara": [
        "Alkapuri", "Fatehgunj", "Manjalpur", "Gotri", "Waghodia Road",
        "Karelibaug", "Atladra", "Sama", "Sayajigunj", "Raopura",
        "Race Course", "Akota", "Vasna", "Gorwa", "Harni"
    ],
    "Surat": [
        "Adajan", "Vesu", "Citylight", "Katargam", "Udhna",
        "Piplod", "Bhatar", "Varachha", "Althan", "Athwa",
        "Palanpur Patia", "Pal", "Dumas", "Kamrej", "Sachin"
    ],
    "Rajkot": [
        "Kalawad Road", "150 Feet Ring Road", "University Road",
        "Yagnik Road", "Gondal Road", "Bhavnath Road",
        "Mavdi", "Raiya Road", "Aji Dam Road", "Kothariya"
    ],
    "Gandhinagar": [
        "Sector 1", "Sector 5", "Sector 7", "Sector 11",
        "Sector 16", "Sector 21", "Sector 28", "Infocity",
        "Kudasan", "Sargasan"
    ],
    "Bhavnagar": [
        "Ghogha Circle", "Kumbharwada", "Waghawadi Road",
        "Kalanala", "Crescent Circle", "Ganga Nagar"
    ],
    "Jamnagar": [
        "Bedi Gate", "Digvijay Plot", "Shivaji Nagar",
        "Indira Marg", "Ranjit Sagar", "Lal Bungalow"
    ],
    "Anand": [
        "Anand Town", "Vallabh Vidyanagar", "Karamsad",
        "Anklav", "Borsad", "Petlad"
    ],
    "Nadiad": ["Nadiad Town", "Mahudha", "Kheda", "Kapadvanj"],
    "Mehsana": ["Mehsana Town", "Unjha", "Visnagar", "Kheralu"],
}

GUJARAT_CITIES = sorted(GUJARAT_AREAS.keys())


def get_areas(city: str) -> list:
    return GUJARAT_AREAS.get(city, [])


# ══════════════════════════════════════════
# ELIGIBILITY
# ══════════════════════════════════════════
def check_eligibility(last_donated_str: str):
    """
    Returns (is_eligible, days_since, days_remaining)
    WHO rule: 90 days between whole blood donations
    """
    if not last_donated_str:
        return True, None, 0
    try:
        last = date.fromisoformat(last_donated_str)
        today = date.today()
        days_since = (today - last).days
        days_remaining = max(0, 90 - days_since)
        is_eligible = days_since >= 90
        return is_eligible, days_since, days_remaining
    except Exception:
        return True, None, 0


def eligibility_progress(last_donated_str: str) -> float:
    """Returns 0.0 to 1.0 progress toward next eligibility."""
    if not last_donated_str:
        return 1.0
    try:
        last = date.fromisoformat(last_donated_str)
        days_since = (date.today() - last).days
        return min(1.0, days_since / 90)
    except Exception:
        return 1.0


# ══════════════════════════════════════════
# WHATSAPP MESSAGES
# ══════════════════════════════════════════
def wa_sos_message(blood_group: str, area: str, city: str, contact: str) -> str:
    return f"""🚨 *URGENT BLOOD NEEDED* 🚨

Blood Group: *{blood_group}*
Location: *{area}, {city}*
Contact: *{contact}*

⏰ This is a critical emergency.
If you or anyone you know can help,
please contact immediately.

Every second counts.
One call can save a life. 🩸

🔗 BloodSetu Portal — Gujarat's Blood Network
Share this message. You could be someone's last hope. ❤️"""


def wa_event_message(organizer: str, city: str, area: str,
                     camp_date: str, timings: str,
                     doctor: str, phone: str) -> str:
    return f"""❤️ *BLOOD DONATION DRIVE*

🏥 {organizer}
📍 {area}, {city}
📅 {camp_date}
⏰ {timings}
👨‍⚕️ {doctor}
📞 {phone}

🩸 Donors needed urgently.
1 donation = up to 3 lives saved.

Be a hero. Show up.
Register on *BloodSetu* — Gujarat's Blood Network

Share with your family & friends.
Together we can save lives. 🙏"""


def wa_awareness_message() -> str:
    return """💉 *Did you know?*

Every 2 seconds someone in India needs blood.
Only 7% of Indians donate.
You could be someone's miracle.

🩸 Register as a donor on *BloodSetu*
Gujarat's AI-powered Blood Connection Portal

✅ One drop of yours = Three lives saved. ❤️

Share this. Spread hope. Be a hero."""


# ══════════════════════════════════════════
# BADGE SYSTEM
# ══════════════════════════════════════════
BADGES = [
    {
        "id": "first_drop",
        "icon": "🩸",
        "name": "First Drop Hero",
        "name_gu": "પ્રથમ ટીપું હીરો",
        "condition": "First donation",
        "min_donations": 1,
        "sos_required": False,
        "rare_blood": False,
    },
    {
        "id": "life_saver",
        "icon": "❤️",
        "name": "Life Saver",
        "name_gu": "જીવ બચાવનાર",
        "condition": "3 donations",
        "min_donations": 3,
        "sos_required": False,
        "rare_blood": False,
    },
    {
        "id": "emergency",
        "icon": "⚡",
        "name": "Emergency Responder",
        "name_gu": "કટોકટી પ્રતિસાદ",
        "condition": "Responded to SOS",
        "min_donations": 1,
        "sos_required": True,
        "rare_blood": False,
    },
    {
        "id": "fast",
        "icon": "🚀",
        "name": "Fast Responder",
        "name_gu": "ઝડપી પ્રતિસાદ",
        "condition": "Responded within 1 hour",
        "min_donations": 1,
        "sos_required": True,
        "rare_blood": False,
    },
    {
        "id": "rare_blood",
        "icon": "💎",
        "name": "Rare Blood Hero",
        "name_gu": "દુર્લભ લોહીના હીરો",
        "condition": "AB- or O- donor",
        "min_donations": 1,
        "sos_required": False,
        "rare_blood": True,
    },
    {
        "id": "legend",
        "icon": "👑",
        "name": "Daata Legend",
        "name_gu": "દાતા દંતકથા",
        "condition": "5+ donations",
        "min_donations": 5,
        "sos_required": False,
        "rare_blood": False,
    },
]


def get_earned_badges(donations_count: int, blood_group: str) -> list:
    earned = []
    rare = blood_group in ["AB-", "O-"]
    for b in BADGES:
        if b["rare_blood"] and not rare:
            continue
        if b["sos_required"]:
            continue  # simplified — SOS tracking not implemented yet
        if donations_count >= b["min_donations"]:
            earned.append(b)
    return earned


# ══════════════════════════════════════════
# EMOTIONAL MESSAGES (English + Gujarati)
# ══════════════════════════════════════════
MESSAGES = {
    "search_loading": {
        "en": "Hang on... we're finding hope for you. Don't worry. You are not alone. 🩸",
        "gu": "રાહ જુઓ... અમે તમારા માટે આશા શોધી રહ્યા છીએ. ચિંતા ન કરો. 🩸"
    },
    "blood_found": {
        "en": "Hope found. Someone is ready to help you. Please reach out to them with kindness. ❤️",
        "gu": "આશા મળી. કોઈ તમારી મદદ કરવા તૈયાર છે. ❤️"
    },
    "nothing_found": {
        "en": "We searched everywhere. Don't give up yet. Share this SOS — miracles come from unexpected places. ❤️",
        "gu": "અમે બધે શોધ્યું. હજી હાર ન માનો. આ SOS શેર કરો. ❤️"
    },
    "donor_welcome": {
        "en": "You are about to do something most people never will. You are about to save a life. Welcome to BloodSetu family. 🩸",
        "gu": "તમે એક જીવ બચાવવા જઈ રહ્યા છો. BloodSetu પરિવારમાં આપનું સ્વાગત છે. 🩸"
    },
    "slot_booked": {
        "en": "Your slot is confirmed. Someone, somewhere, is going to live because YOU showed up. That is everything. ❤️",
        "gu": "તમારો સ્લોટ નિશ્ચિત થયો. કોઈ જીવશે કારણ કે તમે આવ્યા. ❤️"
    },
    "eligible_again": {
        "en": "You're ready again, hero. Your blood can save up to 3 more lives. No pressure. Just gratitude. 🙏",
        "gu": "તમે ફરી તૈયાર છો, હીરો. તમારું લોહી 3 વધુ જીવ બચાવી શકે છે. 🙏"
    },
    "badge_unlocked": {
        "en": "You gave someone their tomorrow. Thank you for being you. ❤️",
        "gu": "તમે કોઈને તેમનો આવતીકાલ આપ્યો. આભાર. ❤️"
    },
    "critical_stock": {
        "en": "Lives are at risk right now. This blood group is critically low. If you can donate, please do it today. 🙏",
        "gu": "અત્યારે જીવ જોખમમાં છે. આ બ્લડ ગ્રુપ ખૂબ ઓછું છે. આજે જ દાન કરો. 🙏"
    },
    "homepage_quote": {
        "en": "Every drop saves a life.",
        "gu": "દરેક ટીપું એક જીવ બચાવે છે."
    },
    "hero_tagline": {
        "en": "You don't need a cape to be a hero. You just need to say YES.",
        "gu": "હીરો બનવા માટે ઝભ્ભો નથી જોઈતો. ફક્ત 'હા' કહો."
    },
}


def get_msg(key: str, lang: str = "en") -> str:
    msg = MESSAGES.get(key, {})
    return msg.get(lang, msg.get("en", ""))


# ══════════════════════════════════════════
# ROTATING QUOTES
# ══════════════════════════════════════════
QUOTES = [
    {
        "en": "The blood you donate gives someone another chance at life.",
        "gu": "તમારું દાન કરેલ લોહી કોઈને ફરીથી જીવવાની તક આપે છે."
    },
    {
        "en": "Be someone's reason to smile today. Donate blood.",
        "gu": "આજે કોઈના સ્મિતનું કારણ બનો. લોહી દાન કરો."
    },
    {
        "en": "You don't have to be a doctor to save lives. Just donate.",
        "gu": "જીવ બચાવવા ડૉક્ટર હોવું જરૂરી નથી. ફક્ત દાન કરો."
    },
    {
        "en": "One donation. Three lives. One hero.",
        "gu": "એક દાન. ત્રણ જીવ. એક હીરો."
    },
    {
        "en": "In the end, it's not the years in your life that count — it's the lives you touched.",
        "gu": "અંતે, તમારી ઉંમર નહીં — તમે કેટલા જીવ સ્પર્શ્યા તે ગણાય."
    },
]

