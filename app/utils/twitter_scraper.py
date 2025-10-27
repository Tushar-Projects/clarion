import re
import os
import asyncio
from twikit import Client
from sqlalchemy.orm import Session
from app.models import Post, Comment, Source
from app.utils.credibility import compute_advanced_score


# -------------------------------
# Async Twikit initialization
# -------------------------------
async def async_init_twitter_client() -> Client:
    client = Client('en-US')
    session_file = 'twitter_session.json'

    if not os.path.exists(session_file):
        raise Exception("twitter_session.json not found. Please export your X cookies first.")

    with open(session_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cookies = data.get("cookies", {})
    if not cookies:
        raise Exception("No cookies found in twitter_session.json")

    for name, value in cookies.items():
        client.cookies.set(name, value, domain=".x.com", path="/")

    print("✅ Cookies loaded successfully from twitter_session.json")
    return client



def extract_tweet_id(url: str) -> str | None:
    """Extract tweet ID from URL."""
    match = re.search(r"status/(\d+)", url)
    return match.group(1) if match else None


# -------------------------------
# Async main fetch
# -------------------------------
async def async_fetch_tweet_data(tweet_id: str, db: Session) -> int | None:
    client = await async_init_twitter_client()

    try:
        tweet = await client.get_tweet_by_id(tweet_id)
        if not tweet:
            print("❌ Tweet not found or private.")
            return None

        # Extract external URLs
        urls = re.findall(r'(https?://[^\s]+)', tweet.text)
        article_url = urls[0] if urls else None

        # Create or get Source
        source = None
        if article_url:
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)/?', article_url)
            domain = domain_match.group(1) if domain_match else None
            if domain:
                source = db.query(Source).filter(Source.url_pattern.ilike(f"%{domain}%")).first()

        # Create Post
        post = Post(
            platform="Twitter",
            post_id=str(tweet_id),
            title=(tweet.text[:120] + '...') if len(tweet.text) > 120 else tweet.text,
            url=f"https://x.com/i/status/{tweet_id}",
            source_id=source.id if source else None,
            verified_manual=False,
            upvotes=getattr(tweet, "favorite_count", 0),
            num_comments=getattr(tweet, "reply_count", 0)
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        # Fetch replies (try/catch for API restrictions)
        try:
            replies = await tweet.get_replies(limit=10)
            for r in replies:
                text = r.text.strip()
                if not text:
                    continue
                db.add(Comment(
                    post_id=post.id,
                    text=text,
                    sentiment=None,
                    is_sarcastic=False
                ))
            db.commit()
        except Exception as e:
            print(f"⚠️ Could not fetch replies: {e}")

        # Compute credibility
        score, explanation = compute_advanced_score(post, db)
        post.advanced_score = score
        post.score_explanation = explanation
        db.commit()

        print(f"✅ Stored tweet '{post.title[:50]}...' with score {score}")
        return post.id

    except Exception as e:
        print(f"❌ Error fetching tweet: {e}")
        return None


# -------------------------------
# Sync wrapper for Flask
# -------------------------------
def fetch_and_store_tweet(url: str, db: Session) -> int | None:
    """Sync wrapper for Flask to call async Twikit code."""
    tweet_id = extract_tweet_id(url)
    if not tweet_id:
        print("❌ Invalid tweet URL")
        return None

    try:
        return asyncio.run(async_fetch_tweet_data(tweet_id, db))
    except Exception as e:
        print(f"❌ Async fetch failed: {e}")
        return None
