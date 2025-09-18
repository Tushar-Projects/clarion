import os
import requests
from dotenv import load_dotenv
from app.utils.database import SessionLocal
from app.models import Post

load_dotenv()
API_KEY = os.getenv("GOOGLE_FACTCHECK_API_KEY")
BASE_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

def fact_check_post_titles():
    db = SessionLocal()
    posts = db.query(Post).all()

    for post in posts:
        if not post.title:
            continue

        params = {
            "query": post.title,
            "key": API_KEY,
            "pageSize": 1  # just fetch top result
        }
        try:
            response = requests.get(BASE_URL, params=params)
            data = response.json()

            if "claims" in data:
                claim = data["claims"][0]
                text_rating = claim.get("claimReview", [{}])[0].get("textualRating", "")

                # ✅ Adjust credibility score based on fact-check result
                if "False" in text_rating:
                    post.credibility_score = max(0, (post.credibility_score or 0) * 0.5)
                elif "True" in text_rating:
                    post.credibility_score = min(1, (post.credibility_score or 0) * 1.2)

                db.add(post)

        except Exception as e:
            print(f"⚠️ Fact check failed for: {post.title[:60]}... ({e})")

    db.commit()
    db.close()
    print("✅ Fact check completed and credibility updated!")

if __name__ == "__main__":
    fact_check_post_titles()
