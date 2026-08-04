import json
from datetime import datetime, timedelta

FILE = "users.json"

today = datetime.utcnow().date()
changed = False

with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

for owner_name, owner in data.items():

    if not isinstance(owner, dict):
        continue

    for username, user in owner.items():

        if not isinstance(user, dict):
            continue

        # ---------------------------------
        # Skip Free Users
        # ---------------------------------
        if user.get("isFreeUser", False):
            print(f"[SKIP FREE] {owner_name} -> {username}")
            continue

        # ---------------------------------
        # Skip Expired Users
        # ---------------------------------
        expiry = str(user.get("expiryDate", "")).strip()

        if expiry != "":
            try:
                expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()

                if today > expiry_date:
                    print(f"[SKIP EXPIRED] {owner_name} -> {username}")
                    continue

            except Exception:
                print(f"[INVALID EXPIRY] {owner_name} -> {username}")
                continue

        # ---------------------------------
        # Read HWID Information
        # ---------------------------------
        hwid = str(user.get("hwid", "")).strip()
        bind_date = str(user.get("hwid_bind_date", "")).strip()
        reset_date = str(user.get("hwid_reset_date", "")).strip()

        # No HWID
        if hwid == "":
            continue

        # ---------------------------------
        # Automatically Create Dates
        # ---------------------------------
        if bind_date == "" or reset_date == "":

            user["hwid_bind_date"] = today.strftime("%Y-%m-%d")
            user["hwid_reset_date"] = (
                today + timedelta(days=30)
            ).strftime("%Y-%m-%d")

            changed = True

            print(f"[DATES CREATED] {owner_name} -> {username}")

            # Next Action run me reset check hogi
            continue

        # ---------------------------------
        # Check Reset Date
        # ---------------------------------
        try:

            reset = datetime.strptime(reset_date, "%Y-%m-%d").date()

            if today >= reset:

                user["hwid"] = ""
                user["hwid_bind_date"] = ""
                user["hwid_reset_date"] = ""
                user["last_reset_date"] = today.strftime("%Y-%m-%d")

                changed = True

                print(f"[RESET] {owner_name} -> {username}")

        except Exception as e:

            print(f"[INVALID RESET DATE] {owner_name} -> {username}: {e}")

# ---------------------------------
# Save JSON
# ---------------------------------

if changed:

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("===================================")
    print("Changes Saved Successfully")
    print("===================================")

else:

    print("===================================")
    print("No User Needs Reset Today")
    print("===================================")
