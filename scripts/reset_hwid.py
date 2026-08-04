import json
from datetime import datetime

DATABASE = "users.json"

today = datetime.utcnow().date()

with open(DATABASE, "r", encoding="utf-8") as f:
    data = json.load(f)

changed = False

for category, users in data.items():

    for username, user in users.items():

        # Skip free users
        if str(user.get("hwid", "")).lower() == "free":
            continue

        # Skip No Expiry users
        if user.get("expiryDate") == "No Expiry":
            continue

        next_reset = user.get("next_hwid_reset", "")

        if next_reset == "":
            continue

        try:
            reset_date = datetime.strptime(
                next_reset,
                "%Y-%m-%d"
            ).date()
        except:
            continue

        if today >= reset_date:

            print(f"Resetting HWID: {username}")

            user["hwid"] = ""
            user["hwid_bind_date"] = ""
            user["next_hwid_reset"] = ""
            user["last_hwid_reset"] = today.strftime("%Y-%m-%d")

            changed = True

if changed:

    with open(DATABASE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Database Updated")

else:
    print("Nothing to reset")
