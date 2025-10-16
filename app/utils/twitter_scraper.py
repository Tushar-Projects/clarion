import os
import asyncio
from urllib.parse import urlparse
from app.utils.database import SessionLocal
from app.models import Post, Source
from twikit import Client


def extract_tweet_id(url: str) -> str | None:
    """Extracts tweet ID from URL."""
    if "status/" in url:
        return url.split("status/")[-1].split("?")[0]
    return None


def init_client() -> Client:
    """Initialize Twikit client (loads cookies if available)."""
    client = Client(language='en-US')
    cookie_path = 'twitter_cookies.json'

    if os.path.exists(cookie_path):
        client.load_cookies(cookie_path)
    else:
        client.login(
            auth_info_1=os.getenv("TWITTER_EMAIL"),
            auth_info_2=os.getenv("TWITTER_USERNAME"),
            password=os.getenv("TWITTER_PASSWORD")
        )
        client.save_cookies(cookie_path)

    return client


async def fetch_tweet_async(tweet_id: str):
    """Async helper for Twikit."""
    client = init_client()
    tweet = await client.get_tweet_by_id(tweet_id)
    return tweet


def fetch_and_store_tweet(url: str):
    """Fetch a tweet asynchronously using Twikit and store it in DB."""
    db = SessionLocal()
    try:
        tweet_id = extract_tweet_id(url)
        if not tweet_id:
            print("⚠️ Could not extract tweet ID.")
            return None

        # --- Fetch the tweet asynchronously ---
        tweet = asyncio.run(fetch_tweet_async(tweet_id))

        if not tweet:
            print("⚠️ No tweet data found.")
            return None

        text = getattr(tweet, "text", None)
        author = getattr(tweet.user, "name", "Unknown")
        if not text:
            print("⚠️ Empty tweet text.")
            return None

        print(f"🐦 Tweet by {author}: {text[:60]}...")

        # --- Extract source domain if tweet includes link ---
        source_id = None
        if getattr(tweet, "links", None):
            link = tweet.links[0].expanded_url
            domain = urlparse(link).netloc.replace("www.", "")
            source = db.query(Source).filter(Source.url_pattern.ilike(f"%{domain}%")).first()
            if not source:
                source = Source(name=domain.title(), url_pattern=domain)
                db.add(source)
                db.commit()
                db.refresh(source)
            source_id = source.id

        # --- Check if tweet already exists ---
        existing_post = db.query(Post).filter_by(post_id=tweet_id).first()
        if existing_post:
            existing_post.title = text
            existing_post.platform = "Twitter"
            existing_post.url = url
            existing_post.source_id = source_id
            db.add(existing_post)
            db.commit()
            return existing_post.id

        # --- Create new Post ---
        new_post = Post(
            platform="Twitter",
            post_id=tweet_id,
            title=text,
            url=url,
            source_id=source_id
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post.id

    except Exception as e:
        print(f"❌ Error fetching tweet: {e}")
        return None
    finally:
        db.close()
