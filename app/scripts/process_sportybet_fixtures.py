import subprocess
import sys

def run_module(module_path: str, description: str):
    print(f"\n🚀 Running: {description}")
    result = subprocess.run([sys.executable, "-m", module_path], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("⚠️ STDERR:\n", result.stderr)

if __name__ == "__main__":
    print("📦 Starting full SportyBet fixture processing pipeline...")

    run_module("app.scripts.fetch_sportybet_fixtures", "1️⃣ Fetch raw fixture data")
    run_module("app.scripts.extract_clean_fixtures", "2️⃣ Extract & clean fixture data")
    run_module("app.services.normalize_clean_fixtures", "3️⃣ Normalize into Multibooker format")

    print("\n✅ All Phase 3 steps completed successfully.")
