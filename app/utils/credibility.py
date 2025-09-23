import os
import requests
from dotenv import load_dotenv
from app.utils.database import SessionLocal
from app.models import Post, Comment, Source

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_FACTCHECK_API_KEY")
FACTCHECK_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

def get_factcheck_adjustment(title: str) -> float:
    """Query Google Fact Check API and return adjustment multiplier"""
    if not API_KEY or not title:
        return 1.0  # no change if missing API key or empty title

    params = {"query": title, "key": API_KEY, "pageSize": 1}
    try:
        response = requests.get(FACTCHECK_URL, params=params, timeout=5)
        data = response.json()

        if "claims" in data:
            claim = data["claims"][0]
            rating = claim.get("claimReview", [{}])[0].get("textualRating", "")

            if "False" in rating or "Incorrect" in rating:
                return 0.5  # reduce credibility
            elif "True" in rating or "Correct" in rating:
                return 1.2  # boost credibility
        return 1.0  # neutral adjustment if nothing useful found
    except Exception as e:
        print(f"⚠️ Fact check failed for: {title[:60]}... ({e})")
        return 1.0

def compute_credibility():
    db = SessionLocal()
    posts = db.query(Post).all()

    for post in posts:
        # ✅ Step 1: Source reliability
        source_score = 5  # default if unknown
        if post.source_id:
            source = db.query(Source).filter_by(id=post.source_id).first()
            if source:
                source_score = source.trust_score

        # ✅ Step 2: Average comment sentiment
        comments = db.query(Comment).filter_by(post_id=post.id).all()
        avg_sentiment = (sum(c.sentiment_score or 0 for c in comments) / len(comments)) if comments else 0

        # ✅ Step 3: Sarcasm penalty
        sarcastic_comments = [c for c in comments if getattr(c, "is_sarcastic", 0) == 1]
        sarcasm_ratio = len(sarcastic_comments) / len(comments) if comments else 0
        sarcasm_penalty = 1 - sarcasm_ratio

        # ✅ Step 4: Base credibility
        raw_score = (source_score / 10) * (1 + avg_sentiment) * sarcasm_penalty
        credibility = max(0, min(raw_score, 1))  # clamp to 0–1

        # ✅ Step 5: Fact check adjustment
        adjustment = get_factcheck_adjustment(post.title)
        credibility = max(0, min(credibility * adjustment, 1))

        # ✅ Save back to DB
        post.credibility_score = credibility
        db.add(post)

    db.commit()
    db.close()
    print("✅ Credibility scores updated with fact check integration!")

if __name__ == "__main__":
    compute_credibility()
