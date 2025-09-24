import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.utils.database import SessionLocal
from app.models import Post, Comment, Source

# Load env vars
load_dotenv()
FACT_CHECK_API_KEY = os.getenv("FACT_CHECK_API_KEY")

# -------------------------------
# Baseline Credibility Calculation
# -------------------------------
def compute_baseline_score(post: Post, db: Session) -> float:
    """
    Compute a credibility score based on:
    - sentiment of comments
    - sarcasm ratio
    - source reliability (if available)
    """
    comments = db.query(Comment).filter_by(post_id=post.id).all()
    if not comments:
        return 0.0

    # Average sentiment score
    sentiment_score = sum(c.sentiment_score for c in comments if c.sentiment_score is not None) / max(len(comments), 1)

    # Sarcasm penalty (more sarcasm = less credible)
    sarcasm_count = sum(1 for c in comments if c.is_sarcastic)
    sarcasm_ratio = sarcasm_count / max(len(comments), 1)
    sarcasm_penalty = -0.2 * sarcasm_ratio

    # Source reliability bonus
    reliability_bonus = 0
    if post.source_id:
        source = db.query(Source).filter_by(id=post.source_id).first()
        if source and source.reliability_score is not None:
            reliability_bonus = source.reliability_score

    # Final baseline score
    baseline_score = sentiment_score + sarcasm_penalty + reliability_bonus
    return max(-1, min(1, baseline_score))  # clamp between -1 and 1


# -------------------------------
# Google Fact Check Adjustment
# -------------------------------
def apply_fact_check_adjustment(title: str, baseline_score: float) -> float:
    """
    Query Google Fact Check API and adjust credibility score:
    - If a claim review is found with 'False' → decrease score
    - If 'True' or 'Correct' → increase score
    """
    if not FACT_CHECK_API_KEY:
        return baseline_score

    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {"query": title, "key": FACT_CHECK_API_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "claims" in data:
            for claim in data["claims"]:
                if "claimReview" in claim:
                    for review in claim["claimReview"]:
                        rating = review.get("textualRating", "").lower()
                        if "false" in rating or "pants on fire" in rating:
                            return baseline_score - 0.3
                        elif "true" in rating or "correct" in rating or "accurate" in rating:
                            return baseline_score + 0.3
    except Exception as e:
        print(f"⚠️ Fact check API error: {e}")

    return baseline_score


# -------------------------------
# Main Function
# -------------------------------
def compute_credibility():
    """Recalculate credibility score for all posts"""
    db = SessionLocal()
    try:
        posts = db.query(Post).all()
        for post in posts:
            baseline_score = compute_baseline_score(post, db)
            final_score = apply_fact_check_adjustment(post.title, baseline_score)

            post.credibility_score = max(-1, min(1, final_score))  # clamp
            db.add(post)

        db.commit()
        print("✅ Credibility scores updated")
    except Exception as e:
        print(f"❌ Error updating credibility: {e}")
    finally:
        db.close()
