import subprocess
import sys  # ✅ add this

steps = [
    ("Reddit Fetcher", "app.utils.reddit_api"),
    ("NLP Pipeline", "app.utils.nlp_pipeline"),
    ("Credibility Scoring", "app.utils.credibility"),
    ("Fact Check (Optional)", "app.utils.fact_check"),
]

def run_pipeline():
    for name, module in steps:
        print(f"\n🚀 Running {name}...")
        try:
            # ✅ Use sys.executable instead of plain "python"
            subprocess.run([sys.executable, "-m", module], check=True)
            print(f"✅ {name} completed.\n")
        except subprocess.CalledProcessError as e:
            print(f"❌ {name} failed: {e}\n")
            break

if __name__ == "__main__":
    run_pipeline()
