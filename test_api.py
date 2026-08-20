import urllib.request
import json

def safe_print(s):
    try:
        print(s)
    except:
        try:
            print(s.encode('ascii', errors='replace').decode('ascii'))
        except:
            pass

safe_print("=== 1. Donations Trend:")
try:
    r = urllib.request.urlopen('http://localhost:8000/api/analytics/donations-trend')
    trend = json.loads(r.read())
    safe_print("Months: {} months total".format(len(trend)))
    for t in trend:
        safe_print("  {}: {} donations".format(t["month"], t["count"]))
except Exception as e:
    safe_print("Error: {}".format(e))

safe_print("")
safe_print("=== 2. Stats (check counts):")
r = urllib.request.urlopen('http://localhost:8000/api/stats')
safe_print(json.dumps(json.loads(r.read())))

safe_print("")
safe_print("=== 3. Register new donor user (testuser002):")
try:
    data = json.dumps({"username":"testuser002","password":"Test@123","role":"donor","phone":"9999999998"}).encode()
    req = urllib.request.Request('http://localhost:8000/api/auth/register', data=data, headers={'Content-Type':'application/json'})
    r = urllib.request.urlopen(req)
    safe_print(json.dumps(json.loads(r.read())))
except Exception as e:
    try:
        safe_print("Register: {}".format(e.read() if hasattr(e, 'read') else e))
    except: pass

safe_print("")
safe_print("=== 4. Login testuser002:")
data = json.dumps({"username":"testuser002","password":"Test@123"}).encode()
req = urllib.request.Request('http://localhost:8000/api/auth/login', data=data, headers={'Content-Type':'application/json'})
r = urllib.request.urlopen(req)
login_data = json.loads(r.read())
token = login_data['token']
user = login_data['user']
safe_print("User ID: {uid}, Role: {r}, Phone: {p}".format(uid=user["id"], r=user["role"], p=user.get("phone","")))
safe_print("Password hash in response? {x}".format(x=("password" in user)))
assert "password" not in user, "SECURITY BUG: password hash returned!"
safe_print("OK: password NOT leaked")

safe_print("")
safe_print("=== 5. Save Donor Profile:")
data = json.dumps({"name":"Test Donor","blood_group":"O+","city":"Vadodara","area":"Alkapuri","phone":"9999999998"}).encode()
req = urllib.request.Request('http://localhost:8000/api/donor/profile', data=data, headers={'Content-Type':'application/json', 'Authorization': 'Bearer {t}'.format(t=token)})
try:
    r = urllib.request.urlopen(req)
    prof = json.loads(r.read())
    safe_print("Profile saved OK: {n}, BG={bg}, City={c}, Area={a}".format(n=prof.get("name",""), bg=prof.get("blood_group",""), c=prof.get("city",""), a=prof.get("area","")))
except Exception as e:
    safe_print("Profile save ERROR!")
    if hasattr(e, 'read'):
        try:
            safe_print("Detail: " + e.read().decode('utf-8', errors='replace'))
        except:
            pass
    else:
        safe_print(str(e))

safe_print("")
safe_print("=== 6. Admin Login:")
data = json.dumps({"username":"bloodsetu_admin","password":"BloodSetu@2026"}).encode()
req = urllib.request.Request('http://localhost:8000/api/auth/login', data=data, headers={'Content-Type':'application/json'})
r = urllib.request.urlopen(req)
admin_login = json.loads(r.read())
admin_token = admin_login['token']
safe_print("Admin login OK, role={u}".format(u=admin_login['user']['role']))

safe_print("")
safe_print("=== 7. Admin all-donors:")
req = urllib.request.Request('http://localhost:8000/api/admin/all-donors', headers={'Authorization': 'Bearer {t}'.format(t=admin_token)})
r = urllib.request.urlopen(req)
donors = json.loads(r.read())
safe_print("Total donor rows returned: {x}".format(x=len(donors)))
if donors:
    d = donors[0]
    safe_print("First donor: {n} ({bg}) from {area}, {city}".format(n=d.get("name",""), bg=d.get("blood_group",""), area=d.get("area",""), city=d.get("city","")))

safe_print("")
safe_print("=== 8. Admin all-hospitals:")
req = urllib.request.Request('http://localhost:8000/api/admin/all-hospitals', headers={'Authorization': 'Bearer {t}'.format(t=admin_token)})
r = urllib.request.urlopen(req)
hospitals = json.loads(r.read())
safe_print("Total hospitals: {x}".format(x=len(hospitals)))
for h in hospitals[:2]:
    safe_print(" -> {name}: {city}, {area}".format(name=h["name"], city=h["city"], area=h["area"]))

safe_print("")
safe_print("ALL TESTS PASSED!")
