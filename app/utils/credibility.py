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
def compute_baseline_score(post: Post, db: Session) -> float | None:
    """
    Compute a credibility score based on:
    - sentiment of comments
    - sarcasm ratio
    - source reliability (if available)
    Returns None if there is insufficient data.
    """
    comments = db.query(Comment).filter_by(post_id=post.id).all()
    has_source = bool(post.source_id)

    # If no comments AND no source → insufficient data
    if not comments and not has_source:
        return None

    sentiment_score = 0.0
    sarcasm_penalty = 0.0
    reliability_bonus = 0.0

    if comments:
        # Average sentiment score
        sentiment_score = sum(
            c.sentiment_score for c in comments if c.sentiment_score is not None
        ) / max(len(comments), 1)

        # Sarcasm penalty
        sarcasm_count = sum(1 for c in comments if c.is_sarcastic)
        sarcasm_ratio = sarcasm_count / max(len(comments), 1)
        sarcasm_penalty = -0.2 * sarcasm_ratio

    # Source reliability bonus
    if post.source_id:
        source = db.query(Source).filter_by(id=post.source_id).first()
        if source and source.reliability_score is not None:
            reliability_bonus = source.reliability_score

    baseline_score = sentiment_score + sarcasm_penalty + reliability_bonus
    return max(-1, min(1, baseline_score))  # clamp between -1 and 1


# -------------------------------
# Google Fact Check Adjustment
# -------------------------------
def apply_fact_check_adjustment(title: str, baseline_score: float | None) -> float | None:
    """
    Query Google Fact Check API and adjust credibility score:
    - If a claim review is found with 'False' → decrease score
    - If 'True' or 'Correct' → increase score
    If baseline_score is None, still return None unless fact-check yields a strong result.
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
                            return (baseline_score or 0.0) - 0.3
                        elif (
                            "true" in rating
                            or "correct" in rating
                            or "accurate" in rating
                        ):
                            return (baseline_score or 0.0) + 0.3
    except Exception as e:
        print(f"⚠️ Fact check API error: {e}")

    return baseline_score


def compute_advanced_score(post: Post, db: Session) -> float | None:
    """
    Weighted credibility scoring formula:
    - Sentiment (scaled by comment volume)
    - Sarcasm penalty
    - Source reliability
    - Fact check adjustment (stronger weight)
    """

    comments = db.query(Comment).filter_by(post_id=post.id).all()
    if not comments and not post.source_id:
        return None  # insufficient data

    # ---- Sentiment (scaled by number of comments) ----
    if comments:
        avg_sentiment = sum(
            c.sentiment_score for c in comments if c.sentiment_score is not None
        ) / max(len(comments), 1)

        # Scale by comment volume (more comments = more reliable)
        volume_factor = min(1.0, (len(comments) / 20))  
        sentiment_component = avg_sentiment * volume_factor
    else:
        sentiment_component = 0

    # ---- Sarcasm penalty ----
    sarcasm_ratio = (
        sum(1 for c in comments if c.is_sarcastic) / max(len(comments), 1)
    ) if comments else 0
    sarcasm_component = -sarcasm_ratio  

    # ---- Source reliability ----
    source_component = 0
    if post.source_id:
        source = db.query(Source).filter_by(id=post.source_id).first()
        if source and source.reliability_score is not None:
            source_component = source.reliability_score

    # ---- Fact-check adjustment (stronger) ----
    baseline_for_factcheck = sentiment_component + source_component
    factcheck_component = apply_fact_check_adjustment(
        post.title, baseline_for_factcheck
    )
    if factcheck_component is not None:
        # We only care about the delta adjustment
        factcheck_component = factcheck_component - baseline_for_factcheck
    else:
        factcheck_component = 0

    # ---- Weighted formula ----
    final_score = (
        (0.4 * sentiment_component)
        + (0.2 * sarcasm_component)
        + (0.2 * source_component)
        + (0.2 * factcheck_component)
    )

    return max(-1, min(1, final_score))



# -------------------------------
# Main Functions
# -------------------------------
def compute_credibility():
    """Recalculate credibility score for all posts"""
    db = SessionLocal()
    try:
        posts = db.query(Post).all()
        for post in posts:
            baseline_score = compute_baseline_score(post, db)
            final_score = apply_fact_check_adjustment(post.title, baseline_score)

            post.credibility_score = (
                max(-1, min(1, final_score)) if final_score is not None else None
            )

            # ✅ Advanced scoring
            post.advanced_score = compute_advanced_score(post, db)

            db.add(post)

        db.commit()
        print("✅ Credibility scores updated for all posts")
    except Exception as e:
        print(f"❌ Error updating credibility: {e}")
    finally:
        db.close()



def compute_single_post(post_id: int):
    """Recalculate credibility score for a single post"""
    db = SessionLocal()
    try:
        post = db.query(Post).filter_by(id=post_id).first()
        if not post:
            print(f"⚠️ Post {post_id} not found")
            return None

        baseline_score = compute_baseline_score(post, db)
        final_score = apply_fact_check_adjustment(post.title, baseline_score)

        post.credibility_score = (
            max(-1, min(1, final_score)) if final_score is not None else None
        )

        # ✅ Advanced scoring
        post.advanced_score = compute_advanced_score(post, db)

        db.add(post)
        db.commit()

        status = (
            "insufficient_data" if final_score is None else f"{post.credibility_score:.3f}"
        )
        print(f"✅ Updated credibility for post {post_id}: {status} "
              f"(advanced: {post.advanced_score})")

        return post.credibility_score
    except Exception as e:
        print(f"❌ Error updating credibility for post {post_id}: {e}")
        return None
    finally:
        db.close()

