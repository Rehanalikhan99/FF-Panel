import json
import datetime

# Database file ka naam (agar aap ki file ka naam kuch aur hai to change kar dein)
JSON_FILE_PATH = "database.json" 

def process_hwid_management():
    try:
        with open(JSON_FILE_PATH, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
        return

    today = datetime.datetime.utcnow().date()
    updated = False

    for category in ["EREN", "INSANE"]:
        if category in data:
            for username, user_data in data[category].items():
                hwid = user_data.get("hwid", "")
                expiry = user_data.get("expiryDate", "")

                # 1. Free Users ko skip kar do
                if hwid == "free":
                    continue

                # 2. Expiry Check
                is_expired = False
                if expiry != "No Expiry":
                    try:
                        exp_date = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
                        if today > exp_date:
                            is_expired = True
                    except ValueError:
                        pass

                # Expired account ko skip kar do
                if is_expired:
                    print(f"⛔ Skipped expired user: {username}")
                    continue

                # 3. Agar User ne naya login kiya hai aur HWID save hua hai to Dates add karo
                if hwid != "" and "hwid_bind_date" not in user_data:
                    bind_date = today
                    reset_date = bind_date + datetime.timedelta(days=30)
                    
                    user_data["hwid_bind_date"] = bind_date.strftime("%Y-%m-%d")
                    user_data["hwid_reset_date"] = reset_date.strftime("%Y-%m-%d")
                    if "last_reset_date" not in user_data:
                        user_data["last_reset_date"] = "None"
                    
                    updated = True
                    print(f"📅 Added HWID Dates for new login: {username} (Next Reset: {user_data['hwid_reset_date']})")

                # 4. Agar 30 Din (Reset Date) poore ho gaye hain to HWID Blank kar do
                if hwid != "" and "hwid_reset_date" in user_data:
                    try:
                        target_reset_date = datetime.datetime.strptime(user_data["hwid_reset_date"], "%Y-%m-%d").date()
                        
                        if today >= target_reset_date:
                            print(f"🔄 HWID Reset Date reached for active user: {username}")
                            
                            user_data["hwid"] = ""  # C# App ke liye HWID clean kar diya
                            user_data["last_reset_date"] = today.strftime("%Y-%m-%d")
                            
                            # Purani bind dates remove kar do taake next login par fresh generate hon
                            user_data.pop("hwid_bind_date", None)
                            user_data.pop("hwid_reset_date", None)
                            
                            updated = True
                    except ValueError:
                        pass

    if updated:
        with open(JSON_FILE_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print("✅ Database updated successfully on GitHub.")
    else:
        print("ℹ️ No changes needed today.")

if __name__ == "__main__":
    process_hwid_management()
