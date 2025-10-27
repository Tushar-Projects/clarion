import json

# Read your exported cookies file
with open("twitter_session.json", "r", encoding="utf-8") as f:
    raw_cookies = json.load(f)

# Convert format
converted = []
for c in raw_cookies:
    converted.append({
        "name": c.get("Name raw"),
        "value": c.get("Content raw"),
        "domain": "x.com",
        "path": "/",
        "secure": c.get("Send for") == "Encrypted connections only"
    })

# Save new cookie file
with open("twitter_session_fixed.json", "w", encoding="utf-8") as f:
    json.dump(converted, f, indent=2)

print("✅ Converted cookies saved to twitter_session_fixed.json")
