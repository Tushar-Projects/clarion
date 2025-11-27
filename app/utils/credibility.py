import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import JSON
from urllib.parse import urlparse


from app.utils.database import SessionLocal
from app.models import Post, Comment, Source

# Load env vars
load_dotenv()
FACT_CHECK_API_KEY = os.getenv("GOOGLE_FACTCHECK_API_KEY")

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
def apply_fact_check_adjustment(title: str, baseline_score: float | None, url: str | None = None) -> float | None:
    """
    Query Google Fact Check API and adjust credibility score.
    """
    print(f"🔍 Applying fact check adjustment for title: {title}, url: {url}")  # Debug log
    if not FACT_CHECK_API_KEY:
        print("⚠️ FACT_CHECK_API_KEY not set")  # Debug log
        return baseline_score

    # --- Step 1: Auto-detect known fact-checking domains ---
    known_factcheck_domains = [
        "factly.in", "boomlive.in", "altnews.in", "snopes.com",
        "politifact.com", "factcheck.org", "afp.com", "apnews.com/fact-check",
        "reuters.com/fact-check", "thequint.com/news/webqoof", "bbc.com/realitycheck"
    ]

    if url:
        # Extract the domain name from the URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()  # Normalize to lowercase
        domain = domain.replace("www.", "")  # Remove 'www.' if present

        if any(known_domain in domain for known_domain in known_factcheck_domains):
            print(f"✅ Fact-check site detected ({domain}) — auto credibility boost.")
            return (baseline_score or 0.0) + 0.4

    # --- Step 2: Google Fact Check API call ---
    api_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    query_text = " ".join(title.split()[:6])
    params = {"query": f"{query_text} fact check", "key": FACT_CHECK_API_KEY}

    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # --- Step 3: Handle empty responses gracefully ---
        if "claims" not in data or len(data["claims"]) == 0:
            print("ℹ️ No claims found — neutral fallback.")
            return (baseline_score or 0.0) + 0.05

        # --- Step 4: Parse claim reviews for truth / falsity indicators ---
        for claim in data["claims"]:
            if "claimReview" not in claim:
                continue

            for review in claim["claimReview"]:
                rating = (
                    review.get("textualRating")
                    or review.get("rating", {}).get("text")
                    or ""
                ).lower()

                if any(k in rating for k in ["false", "pants on fire", "fake", "incorrect", "misleading"]):
                    print(f"❌ Fact-check verdict: {rating}")
                    return (baseline_score or 0.0) - 0.4
                elif any(k in rating for k in ["true", "correct", "accurate", "mostly true", "verified"]):
                    print(f"✅ Fact-check verdict: {rating}")
                    return (baseline_score or 0.0) + 0.4

        # --- Step 5: If no recognizable verdict, apply mild bump ---
        print("ℹ️ No definitive verdict — soft neutral bump.")
        return (baseline_score or 0.0) + 0.05

    except Exception as e:
        print(f"⚠️ Fact check API error: {e}")  # Debug log
        return (baseline_score or 0.0)




def compute_advanced_score(post: Post, db: Session) -> tuple[float | None, dict]:
    """
    Truth-focused advanced scoring with:
    - Reddit: comment-based credibility + sarcasm awareness
    - News: source reliability + fact check + contextual article boost
    """
    print(f"🔍 Computing advanced score for post: {post.id}, url: {post.url}")  # Debug log
    explanation = {}

    # 📰 --- NEWS ARTICLE MODE ---
    if post.platform and post.platform.lower() == "news":
        explanation["mode"] = "news_article_mode"

        # --- Step 1: Source reliability ---
        source_component = 0.0
        source_domain = None
        if post.source_id:
            source = db.query(Source).filter_by(id=post.source_id).first()
            if source:
                source_component = source.reliability_score or 0.2
                source_domain = source.url_pattern
        else:
            source_component = 0.1  # minimal baseline

        explanation["source_component"] = round(source_component, 3)
        if source_domain:
            explanation["source_domain"] = source_domain

        # --- Step 2: Fact check adjustment ---
        factcheck_component = 0.0
        # Skip fact check for raw images (title is just "Image Verification")
        if post.platform == "Image":
            print("ℹ️ Skipping fact check for Image platform")
        else:
            try:
                factchecked_score = apply_fact_check_adjustment(post.title, source_component, post.url)
                print(f"✅ Fact-checked score: {factchecked_score}")  # Debug log
                if factchecked_score is not None:
                    factcheck_component = factchecked_score - source_component
                else:
                    factcheck_component = 0
                print(f"🔎 Fact-check component: {factcheck_component}")  # Debug log
            except Exception as e:
                print(f"⚠️ Fact check error (news mode): {e}")  # Debug log
                explanation["factcheck_error"] = str(e)

        explanation["factcheck_component"] = round(factcheck_component, 3)

        # --- Step 3: Sentiment influence (if available) ---
        sentiment_component = 0.0
        if getattr(post, "sentiment_score", None) is not None:
            sentiment_component = post.sentiment_score * 0.1
            explanation["sentiment_component"] = round(sentiment_component, 3)

        # --- Step 4: Article trust boost ---
        article_boost = 0.0
        boost_reason = None
        if post.url:
            trusted_sources = [
                "reuters.com", "bbc.com", "nytimes.com", "apnews.com",
                "aljazeera.com", "theguardian.com", "washingtonpost.com"
            ]
            if any(domain in post.url for domain in trusted_sources):
                article_boost = 0.3
                boost_reason = f"Trusted domain ({post.url})"
            elif post.url.startswith("http") and not post.url.endswith((".jpg", ".png", ".gif")):
                article_boost = 0.1
                boost_reason = f"External article link ({post.url})"
            else:
                article_boost = 0.05
                boost_reason = "Minimal boost (unrecognized domain)"

        explanation["article_boost"] = round(article_boost, 3)
        if boost_reason:
            explanation["article_reason"] = boost_reason

        # --- Step 5: Weighted final score ---
        final_score = (
            (0.55 * source_component) +
            (0.25 * factcheck_component) +
            (0.1 * sentiment_component) +
            article_boost
        )

        final_score = max(-1, min(1, final_score))
        explanation["final_score"] = round(final_score, 3)

        # --- Step 6: Fallback when data is minimal ---
        if source_component == 0.0 and factcheck_component == 0.0:
            explanation["reason"] = "minimal_info_fallback"
            final_score = 0.1
            explanation["final_score"] = final_score

        return final_score, explanation

    # 🧩 --- REDDIT / OTHER PLATFORM MODE ---
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

    # ---- Step 2: Detect fake/true signals (LLM Enhanced) ----
    from app.utils.llm_analysis import classify_comments_batch
    
    fake_votes, true_votes, sarcasm_count = 0.0, 0.0, 0
    
    # Extract text for classification
    comment_texts = [c.text for c in valid_comments]
    
    # Batch classify using LLM
    print(f"🤖 Classifying {len(comment_texts)} comments...")
    classifications = classify_comments_batch(comment_texts)
    
    for i, c in enumerate(valid_comments):
        classification = classifications.get(i, "neutral")
        
        # Store classification in DB if needed (optional, but good for debugging)
        c.classification = classification
        
        sarcastic = bool(c.is_sarcastic)
        if sarcastic:
            sarcasm_count += 1
            
        if classification == "refuting":
            fake_votes += 0.5 if sarcastic else 1.0
        elif classification == "supporting":
            true_votes += 0.5 if sarcastic else 1.0
        elif classification == "questioning":
            # Questioning counts slightly towards fake/skepticism
            fake_votes += 0.2

    total_comments = len(valid_comments)
    fake_ratio = fake_votes / total_comments if total_comments else 0
    true_ratio = true_votes / total_comments if total_comments else 0
    sarcasm_ratio = sarcasm_count / total_comments if total_comments else 0

    explanation.update({
        "fake_ratio": round(fake_ratio, 3),
        "true_ratio": round(true_ratio, 3),
        "sarcasm_ratio": round(sarcasm_ratio, 3),
        "method": "llm_classification"
    })

    # ---- Step 3: Comment-driven credibility ----
    comment_component = 0
    if fake_ratio >= 0.3:
        comment_component -= 0.6
    elif fake_ratio >= 0.2:
        comment_component -= 0.4

    if true_ratio >= 0.3:
        comment_component += 0.6
    elif true_ratio >= 0.2:
        comment_component += 0.4

    if sarcasm_ratio > 0.3:
        comment_component *= 0.8

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

    # ---- Step 5: Fact check ----
    baseline_for_factcheck = comment_component + source_component
    factcheck_component = apply_fact_check_adjustment(post.title, baseline_for_factcheck,post.url)
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

    # ---- Step 7: Breaking News Cross-Reference ----
    corroboration_component = 0.0
    if post.platform != "Image":
        from app.utils.news_cross_check import check_breaking_news
        from datetime import datetime, timedelta

        # Only check if post is recent (< 24h) and not already corroborated
        is_recent = post.created_at and post.created_at > datetime.now() - timedelta(hours=24)
        
        print(f"🕒 Post: {post.title[:20]}... | Recent: {is_recent} | Curr Score: {post.corroboration_score}")

        # Force check for debugging (removed 'not post.corroboration_score')
        if is_recent:
            print(f"📰 Checking breaking news for: {post.title}")
            news_result = check_breaking_news(post.title)
            
            if news_result:
                post.corroboration_score = news_result["score_modifier"]
                explanation["news_corroboration"] = {
                    "matches": news_result["match_count"],
                    "sources": news_result["sources"]
                }
        
        if post.corroboration_score:
            corroboration_component = post.corroboration_score
            explanation["corroboration_component"] = corroboration_component

    # ---- Step 8: Intrinsic Content Analysis (LLM) ----
    llm_component = 0.0
    if post.platform != "Image":
        from app.utils.llm_analysis import analyze_content_with_llm
        
        # Only run LLM analysis if not already done (to save API calls/time)
        if not post.llm_verdict:
            print(f"🤖 Running LLM analysis for post: {post.id}")
            llm_result = analyze_content_with_llm(post.title, post.url or "") # Passing URL as text snippet for now if no body
            if llm_result:
                post.llm_verdict = llm_result
                post.sensationalism_score = llm_result.get("sensationalism_score")
        
        if post.llm_verdict:
            # High credibility rating (0-1) -> Positive score
            # High sensationalism (0-1) -> Negative score
            cred_rating = post.llm_verdict.get("credibility_rating", 0.5)
            sensationalism = post.llm_verdict.get("sensationalism_score", 0.0)
            
            # Formula: Credibility - (Sensationalism * 0.5)
            # Map 0.5 to 0, 1.0 to 0.5, 0.0 to -0.5
            llm_component = (cred_rating - 0.5) * 2  # -1 to 1 range
            
            # Penalize for sensationalism ONLY if not corroborated
            if corroboration_component > 0:
                 explanation["sensationalism_waived"] = True
            else:
                llm_component -= (sensationalism * 0.5)
            
            explanation["llm_verdict"] = post.llm_verdict.get("reasoning")
            explanation["sensationalism"] = sensationalism

    explanation["llm_component"] = round(llm_component, 3)

    # ---- Step 9: Image Provenance Check ----
    image_component = 0.0
    from app.utils.image_check import check_image_provenance
    
    # Check if URL is an image (ignoring query params)
    parsed_url = urlparse(post.url)
    path = parsed_url.path.lower()
    is_image = path.endswith(('.jpg', '.jpeg', '.png', '.webp'))
    
    if is_image and not post.image_provenance_status:
        print(f"🖼️ Checking image provenance for: {post.url}")
        image_result = check_image_provenance(post.url)
        
        if image_result:
            post.image_provenance_status = image_result["status"]
            # If recycled, apply heavy penalty
            if image_result.get("is_recycled"):
                image_component = image_result["score_modifier"]
                explanation["image_provenance"] = image_result.get("reason", "Recycled image detected")
            else:
                # Slight boost for original
                image_component = image_result["score_modifier"]
    
    elif post.image_provenance_status == "recycled":
        # Re-apply penalty if already checked
        image_component = -0.8
        explanation["image_provenance"] = "Previously detected as recycled"

    explanation["image_component"] = image_component

    # ---- Step 10: Final weighted formula ----
    # Adjusted weights to prioritize Corroboration and Fact Check
    # If strongly corroborated, reduce impact of negative sentiment/LLM
    
    weight_corroboration = 0.25
    weight_factcheck = 0.25
    weight_llm = 0.15
    weight_comments = 0.15
    weight_source = 0.1
    weight_image = 0.1
    
    # Dynamic weighting: If strong corroboration, boost its weight
    if corroboration_component >= 0.4:
        weight_corroboration = 0.4
        weight_llm = 0.1 # Reduce LLM impact (it might be wrong about tone)
        weight_comments = 0.1 # Reduce comment impact (skeptics)
        explanation["weight_adjustment"] = "Strong corroboration boost"

    final_score = (
        (weight_comments * comment_component) +
        (weight_source * source_component) +
        (weight_factcheck * factcheck_component) +
        (weight_llm * llm_component) +
        (weight_corroboration * corroboration_component) +
        (weight_image * image_component) +
        article_boost
    )

    # Corroboration Override: If 3+ trusted sources confirm it, score should be positive
    if corroboration_component >= 0.4 and final_score < 0.2:
        final_score = 0.3
        explanation["override"] = "Corroboration override (3+ sources)"

    final_score = max(-1, min(1, final_score))
    explanation["final_score"] = round(final_score, 3)

    # ---- Step 11: Fallback ----
    if fake_ratio == 0 and true_ratio == 0 and llm_component == 0 and corroboration_component == 0 and image_component == 0:
        explanation["reason"] = "no_strong_signals"
        final_score = (
            (0.4 * source_component) +
            (0.3 * factcheck_component) +
            (0.3 * llm_component) +
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
