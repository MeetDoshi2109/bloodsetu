"""
map_handler.py — BloodSetu Folium Map Handler
Area-based maps. No real GPS needed.
"""

import folium
from streamlit_folium import st_folium

# ── Area coordinates (approximate centers) ──────────────────
AREA_COORDS = {
    # Vadodara
    "Alkapuri":    (22.3119, 73.1723),
    "Fatehgunj":   (22.3217, 73.1851),
    "Manjalpur":   (22.2678, 73.1759),
    "Gotri":       (22.3363, 73.1612),
    "Waghodia Road":(22.2895, 73.2105),
    "Karelibaug":  (22.3044, 73.2012),
    "Atladra":     (22.2803, 73.1502),
    "Sama":        (22.3089, 73.2189),
    "Sayajigunj":  (22.3088, 73.1924),
    "Raopura":     (22.3177, 73.2050),
    "Race Course": (22.3000, 73.1800),
    "Akota":       (22.2989, 73.1654),
    "Vasna":       (22.2756, 73.1821),
    "Gorwa":       (22.3378, 73.1445),
    "Harni":       (22.3251, 73.2301),
    # Ahmedabad
    "Satellite":   (23.0300, 72.5100),
    "Bopal":       (23.0345, 72.4712),
    "Maninagar":   (22.9990, 72.6090),
    "Vastrapur":   (23.0467, 72.5273),
    "Navrangpura": (23.0389, 72.5611),
    "SG Highway":  (23.0489, 72.5074),
    "Gota":        (23.1108, 72.5342),
    "Chandkheda":  (23.1101, 72.5810),
    "Prahlad Nagar":(23.0187,72.5065),
    "Thaltej":     (23.0547, 72.4968),
    "Ambawadi":    (23.0289, 72.5643),
    "Paldi":       (23.0057, 72.5737),
    "Ellis Bridge":(23.0249, 72.5726),
    "Shahibaug":   (23.0609, 72.5967),
    "Nikol":       (23.0412, 72.6421),
    # Surat
    "Adajan":      (21.1938, 72.7937),
    "Vesu":        (21.1562, 72.7916),
    "Citylight":   (21.1667, 72.8000),
    "Katargam":    (21.2333, 72.8333),
    "Udhna":       (21.1756, 72.8422),
    "Piplod":      (21.1789, 72.7712),
    "Bhatar":      (21.1612, 72.8234),
    "Varachha":    (21.2089, 72.8612),
    "Althan":      (21.1489, 72.7689),
    "Athwa":       (21.1817, 72.8286),
    # Rajkot
    "Kalawad Road":(22.3039, 70.8022),
    "150 Feet Ring Road":(22.3101,70.7889),
    "University Road":(22.2912,70.7612),
    "Yagnik Road": (22.2845, 70.7789),
    "Gondal Road": (22.2600, 70.7512),
    # Gandhinagar
    "Sector 1":    (23.2156, 72.6369),
    "Sector 5":    (23.2234, 72.6512),
    "Sector 11":   (23.2089, 72.6678),
    "Sector 16":   (23.2012, 72.6812),
    "Sector 21":   (23.1934, 72.6956),
    "Infocity":    (23.1789, 72.6234),
}

CITY_CENTERS = {
    "Vadodara":    (22.3072, 73.1812),
    "Ahmedabad":   (23.0225, 72.5714),
    "Surat":       (21.1702, 72.8311),
    "Rajkot":      (22.3039, 70.8022),
    "Gandhinagar": (23.2156, 72.6369),
    "Bhavnagar":   (21.7645, 72.1519),
    "Jamnagar":    (22.4707, 70.0577),
    "Anand":       (22.5645, 72.9289),
    "Nadiad":      (22.6912, 72.8634),
    "Mehsana":     (23.5880, 72.3693),
}


def get_coords(area: str, city: str):
    """Return (lat, lon) for an area, fall back to city center."""
    return AREA_COORDS.get(area, CITY_CENTERS.get(city, (22.3072, 73.1812)))


def build_map(seeker_area: str, city: str,
              hospitals=None, banks=None, camps=None, donors=None,
              zoom=13):
    """Build and return a folium map with all relevant pins."""
    center = get_coords(seeker_area, city)
    m = folium.Map(
        location=center, zoom_start=zoom,
        tiles="CartoDB dark_matter"
    )

    # Seeker pin
    folium.Marker(
        location=center,
        popup=f"<b>📍 You are here</b><br>{seeker_area}, {city}",
        tooltip="Your location",
        icon=folium.Icon(color="red", icon="user", prefix="fa")
    ).add_to(m)

    # Hospital pins
    if hospitals:
        for h in hospitals:
            coords = get_coords(h.get("area", ""), city)
            folium.Marker(
                location=coords,
                popup=(
                    f"<b>🏥 {h['name']}</b><br>"
                    f"👨‍⚕️ {h.get('doctor_name','')}<br>"
                    f"📞 {h['phone']}<br>"
                    f"🩸 {h.get('blood_available','')}"
                ),
                tooltip=h["name"],
                icon=folium.Icon(color="blue", icon="hospital-o", prefix="fa")
            ).add_to(m)

    # Blood bank pins
    if banks:
        for b in banks:
            coords = get_coords(b.get("area", ""), city)
            folium.Marker(
                location=coords,
                popup=(
                    f"<b>🏦 {b['name']}</b><br>"
                    f"👨‍⚕️ {b.get('doctor_name','')}<br>"
                    f"📞 {b['phone']}"
                ),
                tooltip=b["name"],
                icon=folium.Icon(color="green", icon="tint", prefix="fa")
            ).add_to(m)

    # Camp pins
    if camps:
        for camp in camps:
            coords = get_coords(camp.get("area", ""), city)
            folium.Marker(
                location=coords,
                popup=(
                    f"<b>🏕️ {camp['organizer']}</b><br>"
                    f"📅 {camp['camp_date']}<br>"
                    f"⏰ {camp.get('timings','')}<br>"
                    f"📞 {camp['phone']}"
                ),
                tooltip=f"Blood Camp — {camp['camp_date']}",
                icon=folium.Icon(color="orange", icon="flag", prefix="fa")
            ).add_to(m)

    # Donor pins
    if donors:
        for d in donors:
            coords = get_coords(d.get("area", ""), city)
            folium.CircleMarker(
                location=coords,
                radius=8,
                color="#e74c3c",
                fill=True,
                fill_color="#e74c3c",
                fill_opacity=0.7,
                popup=(
                    f"<b>🩸 {d['name']}</b><br>"
                    f"Blood Group: {d['blood_group']}<br>"
                    f"Area: {d['area']}"
                ),
                tooltip=f"{d['name']} — {d['blood_group']}"
            ).add_to(m)

    return m


def show_map(m, height=400):
    """Render folium map in Streamlit."""
    st_folium(m, width=None, height=height, returned_objects=[])

    