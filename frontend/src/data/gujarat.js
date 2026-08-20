// Embedded Gujarat city/area data — no API call needed, always available
export const GUJARAT_AREAS = {
  Ahmedabad: [
    "Satellite", "Bopal", "Maninagar", "Vastrapur", "Navrangpura",
    "SG Highway", "Gota", "Chandkheda", "Prahlad Nagar", "Thaltej",
    "Ambawadi", "Paldi", "Ellis Bridge", "Shahibaug", "Nikol",
    "Naranpura", "Vastral", "Naroda", "Odhav", "Isanpur",
    "Asarwa", "Bapunagar", "Rakhial", "Sarkhej", "Makarba",
  ],
  Vadodara: [
    "Alkapuri", "Fatehgunj", "Manjalpur", "Gotri", "Waghodia Road",
    "Karelibaug", "Atladra", "Sama", "Sayajigunj", "Raopura",
    "Race Course", "Akota", "Vasna", "Gorwa", "Harni",
    "Makarpura", "Subhanpura", "Tarsali", "Nizampura", "Old Padra Road",
    "Waghodia", "Vadodara City", "Laxmipura", "Sevasi", "Ajwa Road",
  ],
  Surat: [
    "Adajan", "Vesu", "Citylight", "Katargam", "Udhna",
    "Piplod", "Bhatar", "Varachha", "Althan", "Athwa",
    "Palanpur Patia", "Pal", "Dumas", "Kamrej", "Sachin",
    "Rander", "Majura Gate", "Nanpura", "Limbayat", "Utran",
    "Puna", "Bhestan", "Chhapra", "Jahangirabad", "Mota Varachha",
  ],
  Rajkot: [
    "Kalawad Road", "150 Feet Ring Road", "University Road",
    "Yagnik Road", "Gondal Road", "Bhavnath Road",
    "Mavdi", "Raiya Road", "Aji Dam Road", "Kothariya",
    "Kalavad Road", "Metoda", "Bhaktinagar", "Rajkot Airport Area", "Pedak Road",
  ],
  Gandhinagar: [
    "Sector 1", "Sector 5", "Sector 7", "Sector 11",
    "Sector 16", "Sector 21", "Sector 28", "Infocity",
    "Kudasan", "Sargasan", "Pethapur", "Koba", "Randesan",
  ],
  Bhavnagar: [
    "Ghogha Circle", "Kumbharwada", "Waghawadi Road",
    "Kalanala", "Crescent Circle", "Ganga Nagar",
    "Sardarnagar", "Atabhai Chowk", "Rupani Circle", "Takhteshwar",
  ],
  Jamnagar: [
    "Bedi Gate", "Digvijay Plot", "Shivaji Nagar",
    "Indira Marg", "Ranjit Sagar", "Lal Bungalow",
    "Khambhalia Road", "Saru Section Road", "Park Colony", "Patel Colony",
  ],
  Anand: [
    "Anand Town", "Vallabh Vidyanagar", "Karamsad",
    "Anklav", "Borsad", "Petlad", "Umreth", "Tarapur",
  ],
  Nadiad: ["Nadiad Town", "Mahudha", "Kheda", "Kapadvanj", "Matar", "Vaso"],
  Mehsana: ["Mehsana Town", "Unjha", "Visnagar", "Kheralu", "Vadnagar", "Sidhpur"],
}

export const GUJARAT_CITIES = Object.keys(GUJARAT_AREAS).sort()

export const ALL_BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
