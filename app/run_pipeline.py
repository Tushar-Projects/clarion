import subprocess
import sys

steps = [
    ("Reddit Fetcher", "app.utils.reddit_api"),
    ("NLP Pipeline", "app.utils.nlp_pipeline"),
    ("Credibility Scoring (with Fact Check)", "app.utils.credibility"),
]

def run_pipeline():
    print(f"🔧 Using Python interpreter: {sys.executable}\n")
    for name, module in steps:
        print(f"\n🚀 Running {name}...")
        try:
            subprocess.run([sys.executable, "-m", module], check=True)
            print(f"✅ {name} completed.\n")
        except subprocess.CalledProcessError as e:
            print(f"❌ {name} failed: {e}\n")
            break

if __name__ == "__main__":
    run_pipeline()
