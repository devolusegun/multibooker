import json

with open("sportybet_fixtures.json", "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned_data = []

for i, item in enumerate(data):
    if isinstance(item, str):
        try:
            cleaned_data.append(json.loads(item))
        except Exception as e:
            print(f"❌ Failed to parse item #{i+1}: {e}")
    elif isinstance(item, dict):
        cleaned_data.append(item)

with open("cleaned_sportybet_fixtures.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2)

print(f"✅ Cleaned {len(cleaned_data)} fixtures and saved to cleaned_sportybet_fixtures.json")
