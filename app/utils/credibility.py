import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import JSON


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
    Community-driven baseline credibility:
    - Focus on whether comments claim the post is fake/true
    - Requires multiple people for consensus shift
    - Adds small popularity boost if highly engaged post but no consensus
    - Ignores emotional sentiment (that is tracked separately as community_sentiment)
    """

    comments = db.query(Comment).filter_by(post_id=post.id).all()
    if not comments:
        return None

    total_comments = len(comments)
    if total_comments == 0:
        return None

    # ---- Step 1: Detect "fake/true" claims in comments ----
    fake_keywords = ["fake", "false", "misinformation", "propaganda", "hoax", "scam", "made up", "not true"]
    true_keywords = ["real", "true", "confirmed", "fact", "evidence", "source", "proven", "legit"]

    fake_votes = 0
    true_votes = 0

    for c in comments:
        text = c.text.lower()
        if any(word in text for word in fake_keywords):
            fake_votes += 1
        if any(word in text for word in true_keywords):
            true_votes += 1

    # ---- Step 2: Calculate proportions ----
    fake_ratio = fake_votes / total_comments
    true_ratio = true_votes / total_comments

    # ---- Step 3: Apply thresholds ----
    score = 0.0

    if fake_ratio >= 0.3:       # strong fake consensus
        score -= 0.7
    elif fake_ratio >= 0.2:     # mild fake consensus
        score -= 0.5

    if true_ratio >= 0.3:       # strong true consensus
        score += 0.7
    elif true_ratio >= 0.2:     # mild true consensus
        score += 0.5

    # ---- Step 4: Popularity fallback ----
    # If no consensus shift, but post is very active (lots of comments/upvotes),
    # assume slight positive credibility because people accept it by default
    if score == 0.0:
        if total_comments > 100 or (post.url and "reddit.com" not in post.url):
            score = 0.2

    return max(-1, min(1, score))


def compute_community_sentiment(post: Post, db: Session) -> float | None:
    """
    Emotional sentiment of the community toward the post
    (positive/negative reaction, sarcasm included).
    Independent of truthfulness.
    """
    comments = db.query(Comment).filter_by(post_id=post.id).all()
    if not comments:
        return None

    sentiment_score = 0.0
    sarcasm_penalty = 0.0

    if comments:
        sentiment_score = sum(
            c.sentiment_score for c in comments if c.sentiment_score is not None
        ) / max(len(comments), 1)

        sarcasm_count = sum(1 for c in comments if c.is_sarcastic)
        sarcasm_ratio = sarcasm_count / max(len(comments), 1)
        sarcasm_penalty = -0.2 * sarcasm_ratio

    return max(-1, min(1, sentiment_score + sarcasm_penalty))

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


def compute_advanced_score(post: Post, db: Session) -> tuple[float | None, dict]:
    """
    Truth-focused advanced scoring with:
    - Comment-based fake/true signal detection
    - Sarcasm-aware weighting
    - Fallback to source reliability, fact check, and article boost
    """
    comments = db.query(Comment).filter_by(post_id=post.id).all()
    if not comments and not post.source_id and not post.url:
        return None, {"reason": "insufficient_data"}

    explanation = {}

    # ---- Step 1: Filter out noise ----
    valid_comments = [
        c for c in comments
        if c.text
        and c.text.lower() not in ["[removed]", "[deleted]"]
        and not c.text.strip().startswith("http")
        and len(c.text.strip()) > 5
    ]

    if not valid_comments:
        explanation["reason"] = "no_valid_comments"
        valid_comments = []

    # ---- Step 2: Detect fake/true signals ----
    fake_keywords = [
        "fake", "false", "misinformation", "propaganda", "hoax",
        "scam", "made up", "not true", "incorrect", "wrong info",
        "debunked", "fact check", "misleading", "clickbait"
    ]
    true_keywords = [
        "real", "true", "confirmed", "fact", "evidence", "source",
        "proven", "legit", "accurate", "verified", "authentic",
        "checked", "supported"
    ]

    fake_votes = 0.0
    true_votes = 0.0
    sarcasm_count = 0

    for c in valid_comments:
        text = c.text.lower()
        sarcastic = bool(c.is_sarcastic)
        if sarcastic:
            sarcasm_count += 1

        # Detect fake/true claims with sarcasm-weighted impact
        if any(word in text for word in fake_keywords):
            fake_votes += 0.3 if sarcastic else 1.0
        elif any(word in text for word in true_keywords):
            true_votes += 0.3 if sarcastic else 1.0

    total_comments = len(valid_comments)
    fake_ratio = fake_votes / total_comments if total_comments else 0
    true_ratio = true_votes / total_comments if total_comments else 0
    sarcasm_ratio = sarcasm_count / total_comments if total_comments else 0

    explanation["fake_ratio"] = round(fake_ratio, 3)
    explanation["true_ratio"] = round(true_ratio, 3)
    explanation["sarcasm_ratio"] = round(sarcasm_ratio, 3)

    # ---- Step 3: Compute comment-driven credibility ----
    comment_component = 0
    if fake_ratio >= 0.2:
        comment_component -= 0.4
    elif fake_ratio >= 0.3:
        comment_component -= 0.6

    if true_ratio >= 0.2:
        comment_component += 0.4
    elif true_ratio >= 0.3:
        comment_component += 0.6

    # Apply sarcasm dampening (Option 2)
    if sarcasm_ratio > 0.3:
        comment_component *= 0.8  # reduce confidence

    explanation["comment_component"] = round(comment_component, 3)

    # ---- Step 4: Source reliability ----
    source_component = 0
    source_domain = None
    if post.source_id:
        source = db.query(Source).filter_by(id=post.source_id).first()
        if source and source.reliability_score is not None:
            source_component = source.reliability_score
            source_domain = source.url_pattern
    explanation["source_component"] = round(source_component, 3)
    if source_domain:
        explanation["source_domain"] = source_domain

    # ---- Step 5: Google Fact Check ----
    baseline_for_factcheck = comment_component + source_component
    factcheck_component = apply_fact_check_adjustment(
        post.title, baseline_for_factcheck
    )
    if factcheck_component is not None:
        factcheck_component = factcheck_component - baseline_for_factcheck
    else:
        factcheck_component = 0
    explanation["factcheck_component"] = round(factcheck_component, 3)

    # ---- Step 6: Article boost ----
    article_boost = 0
    boost_reason = None
    if post.url:
        trusted_sources = [
            "reuters.com", "bbc.com", "nytimes.com", "apnews.com",
            "aljazeera.com", "theguardian.com", "washingtonpost.com"
        ]
        if any(domain in post.url for domain in trusted_sources):
            article_boost = 0.3
            boost_reason = f"Trusted domain ({post.url})"
        elif post.url.startswith("http") and not post.url.endswith((".jpg", ".png", ".gif")) \
             and "redd.it" not in post.url:
            article_boost = 0.1
            boost_reason = f"External article link ({post.url})"
    explanation["article_boost"] = article_boost
    if boost_reason:
        explanation["article_reason"] = boost_reason

    # ---- Step 7: Final weighted formula ----
    final_score = (
        (0.4 * comment_component) +
        (0.2 * source_component) +
        (0.3 * factcheck_component) +
        article_boost
    )

    final_score = max(-1, min(1, final_score))
    explanation["final_score"] = round(final_score, 3)

    # ---- Step 8: Fallback for no truth/fake comments ----
    if fake_ratio == 0 and true_ratio == 0:
        explanation["reason"] = "no_truth_or_fake_mentions"
        final_score = (
            (0.5 * source_component) +
            (0.4 * factcheck_component) +
            article_boost
        )
        final_score = max(-1, min(1, final_score))
        explanation["fallback_score"] = round(final_score, 3)

    return final_score, explanation





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
            community_sentiment = compute_community_sentiment(post, db)
            final_score = apply_fact_check_adjustment(post.title, baseline_score)

            post.credibility_score = (
                max(-1, min(1, final_score)) if final_score is not None else None
            )
            # Corrected assignment: call compute_advanced_score once, then assign the float
            advanced_score, explanation = compute_advanced_score(post, db)
            post.advanced_score = advanced_score
            post.community_sentiment = community_sentiment
            post.score_explanation = explanation
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
        community_sentiment = compute_community_sentiment(post, db)
        final_score = apply_fact_check_adjustment(post.title, baseline_score)

        post.credibility_score = (
            max(-1, min(1, final_score)) if final_score is not None else None
        )
        # Corrected assignment: call compute_advanced_score once, then assign the float
        advanced_score, explanation = compute_advanced_score(post, db)
        post.advanced_score = advanced_score
        post.community_sentiment = community_sentiment
        post.score_explanation = explanation  # ✅ Save JSON into DB
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
