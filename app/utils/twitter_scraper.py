import re
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.models import Post, Comment, Source
from app.utils.credibility import compute_advanced_score


def extract_tweet_id(url: str) -> str | None:
    """Extract tweet ID from a valid tweet URL."""
    match = re.search(r"status/(\d+)", url)
    return match.group(1) if match else None


def fetch_and_store_tweet(url: str, db: Session) -> int | None:
    """
    Fetch tweet details via BeautifulSoup (no Twikit).
    Extracts text, embedded links, and basic metadata.
    Skips video/image-only tweets.
    """
    print(f"🌐 Fetching tweet: {url}")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # --- Extract tweet text from meta tags ---
        tweet_text = None
        meta_candidates = [
            soup.find("meta", attrs={"property": "og:description"}),
            soup.find("meta", attrs={"name": "twitter:description"}),
            soup.find("meta", attrs={"property": "og:title"}),
            soup.find("meta", attrs={"name": "twitter:title"})
        ]
        for tag in meta_candidates:
            if tag and tag.get("content"):
                tweet_text = tag["content"].strip()
                break

        if not tweet_text:
            print("⚠️ Could not extract tweet text — possibly video-only or removed.")
            tweet_text = "⚠️ Could not extract tweet text."

        # --- Extract external URLs (t.co links or full URLs) ---
        print("🔍 Extracting embedded links...")
        links = re.findall(r'https?://t\.co/\w+|https?://[^\s]+', response.text)
        article_url = links[0] if links else None

        # --- Create or find Source entry ---
        source = None
        if article_url:
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)/?', article_url)
            domain = domain_match.group(1) if domain_match else None
            if domain:
                source = db.query(Source).filter(Source.url_pattern.ilike(f"%{domain}%")).first()

        # --- Create Post record ---
        # --- Create Post record ---
        existing_post = db.query(Post).filter_by(post_id=extract_tweet_id(url)).first()
        if existing_post:
            print(f"ℹ️ Tweet already exists in database (Post ID: {existing_post.id}). Skipping insert.")
            return existing_post.id

        post = Post(
            platform="Twitter",
            post_id=extract_tweet_id(url),
            title=tweet_text[:120] + "..." if len(tweet_text) > 120 else tweet_text,
            url=url,
            credibility_score=None,
            sentiment_score=None,
            source_id=source.id if source else None,
            advanced_score=None,
            verified_manual=False,
            upvotes=0,
            num_comments=0
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        print(f"✅ Stored tweet: {post.title[:60]}...")

        # --- Comments placeholder ---
        # (In future, you can add sentiment scraping here)
        dummy_comments = [
            "This seems fake!",
            "True news, I saw it earlier.",
            "Can't believe this happened.",
            "Is this verified?"
        ]
        for text in dummy_comments:
            comment = Comment(
                post_id=post.id,
                text=text,
                sentiment_score=None,
                is_sarcastic=False
            )
            db.add(comment)
        db.commit()

        # --- Compute advanced credibility score ---
        print(f"🔍 Computing advanced score for post {post.id}...")
        score, explanation = compute_advanced_score(post, db)
        post.advanced_score = score
        post.score_explanation = explanation
        db.commit()

        print(f"✅ Tweet stored and scored successfully (Score: {score})")
        return post.id

    except Exception as e:
        print(f"❌ Error fetching tweet: {e}")
        return None
