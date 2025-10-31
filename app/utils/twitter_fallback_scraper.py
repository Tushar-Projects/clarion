# app/utils/twitter_fallback_scraper.py
import os
import httpx
import re
import random
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from app.models import Post, Comment, Source
from app.utils.credibility import compute_advanced_score

load_dotenv()  # Load .env file


def extract_tweet_id(url: str) -> str | None:
    """Extract numeric tweet ID from URL."""
    match = re.search(r"(?:status|statuses)/(\d+)", url)
    return match.group(1) if match else None


# -----------------------------------------------------------------------------
# 🟢 Primary: Twitter Syndication API
# -----------------------------------------------------------------------------
def fetch_tweet_json(tweet_id: str):
    """Try fetching tweet JSON via Twitter syndication API."""
    api_url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://platform.twitter.com/",
    }

    # Proxy support (older httpx compatible)
    use_proxy = os.getenv("USE_PROXY", "false").lower() == "true"
    proxy_url = os.getenv("PROXY_URL", "")
    client_args = {"headers": headers, "timeout": 20.0, "follow_redirects": True}

    if use_proxy and proxy_url:
        print(f"🌐 Using proxy: {proxy_url}")
        client_args["transport"] = httpx.HTTPTransport(proxy=proxy_url)
    else:
        print("🌐 Fetching directly (no proxy)...")

    try:
        with httpx.Client(**client_args) as client:
            resp = client.get(api_url)
            if resp.status_code == 200:
                return resp.json()
            print(f"❌ Network error during syndication: {resp.status_code} {resp.text[:100]}")
    except Exception as e:
        print(f"❌ Network error during syndication: {e}")

    # Fall back to Nitter mirrors if syndication fails
    return fetch_from_nitter(tweet_id)


# -----------------------------------------------------------------------------
# 🪶 Nitter Fallbacks
# -----------------------------------------------------------------------------
def _extract_text_from_nitter(html: str) -> str:
    """Extract tweet text robustly from Nitter HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Try main tweet content divs
    div = soup.find("div", class_="tweet-content media-body") or soup.find("div", class_="tweet-content")

    if div:
        text = div.get_text(" ", strip=True)
        if text:
            print(f"📝 Extracted text from main tweet-content div: {text[:80]}")
            return text

    # Fallback: try paragraph-based extraction (for multi-line tweets)
    paragraphs = soup.find_all("p")
    if paragraphs:
        text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
        print(f"🪶 Extracted text from <p> tags (fallback): {text[:80]}")
        return text

    # Final fallback
    print("⚠️ Could not find recognizable tweet text tags.")
    return "⚠️ Could not extract tweet text."



def fetch_from_nitter(tweet_id: str):
    """Fallback: Try multiple Nitter mirrors to extract tweet text."""
    nitter_list = [
        u.strip() for u in os.getenv("NITTER_INSTANCES", "").split(",") if u.strip()
    ]
    if not nitter_list:
        nitter_list = [
            "https://nitter.net",
            "https://nitter.cz",
            "https://nitter.poast.org",
            "https://nitter.salastil.com",
        ]
    random.shuffle(nitter_list)
    print("🪶 Falling back to Nitter mirrors...")

    for base in nitter_list:
        nitter_url = f"{base}/i/status/{tweet_id}"
        print(f"🔁 Trying Nitter instance: {nitter_url}")
        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                r = client.get(nitter_url)
                if r.status_code == 200 and "tweet-content" in r.text:
                    print(f"✅ Success via {base}")
                    text = _extract_text_from_nitter(r.text)
                    return {
                        "author": _extract_author_from_nitter(r.text),
                        "text": text,
                        "links": _extract_links_from_nitter(r.text),
                        "likes": 0,
                        "replies": 0,
                        "retweets": 0,
                        "replies_data": [],
                    }
                elif r.status_code == 429:
                    print(f"🚫 Rate-limited by {base}, skipping…")
                else:
                    print(f"⚠️ {base} returned {r.status_code}")
        except Exception as e:
            print(f"⚠️ {base} error: {e}")
        time.sleep(2)

    print("❌ All Nitter mirrors failed.")
    return None


def _extract_author_from_nitter(html: str) -> str:
    """Extract author name from Nitter HTML."""
    soup = BeautifulSoup(html, "html.parser")
    author = soup.find("a", class_="username")
    return author.get_text(strip=True) if author else "Unknown"


def _extract_links_from_nitter(html: str):
    """Extract external links from Nitter tweet."""
    soup = BeautifulSoup(html, "html.parser")
    return [
        a["href"] for a in soup.find_all("a", href=True)
        if a["href"].startswith("http") and "nitter" not in a["href"]
    ]


# -----------------------------------------------------------------------------
# 🧩 Parsing + Storage
# -----------------------------------------------------------------------------
def parse_tweet_data(tweet_json: dict):
    """Parse data from Twitter syndication JSON."""
    try:
        text = tweet_json.get("text") or tweet_json.get("full_text")
        author = tweet_json.get("user", {}).get("name") or "Unknown"
        urls = [u["expanded_url"] for u in tweet_json.get("entities", {}).get("urls", [])]
        likes = tweet_json.get("favorite_count", 0)
        replies = tweet_json.get("reply_count", 0)
        retweets = tweet_json.get("retweet_count", 0)
        return {
            "author": author,
            "text": text or "⚠️ Could not extract tweet text.",
            "links": urls,
            "likes": likes,
            "replies": replies,
            "retweets": retweets,
            "replies_data": [],
        }
    except Exception as e:
        print(f"⚠️ Parse error: {e}")
        return None


def fetch_and_store_tweet(url, db):
    """Main entry point — fetch tweet JSON, or Nitter fallback, then store."""
    tweet_id = extract_tweet_id(url)
    if not tweet_id:
        print("❌ Invalid tweet URL")
        return None

    print(f"🌐 Fetching tweet JSON for ID: {tweet_id}")
    data = fetch_tweet_json(tweet_id)

    # If syndication failed, fall back to Nitter
    if not data:
        data = fetch_from_nitter(tweet_id)
        if not data:
            print("❌ All extraction methods failed.")
            return None

    # Detect source of data (syndication JSON vs Nitter)
    if "user" in data:
        tweet = parse_tweet_data(data)
        print("🟢 Extraction method: Twitter Syndication API")
    else:
        tweet = data
        print("🪶 Extraction method: Nitter fallback")

    # Validate text content
    if not tweet or not tweet.get("text") or tweet["text"].startswith("⚠️"):
        print("⚠️ Could not extract tweet text.")
        return None

    print(f"✅ Parsed tweet successfully: {tweet['text'][:100]}")

    # Check existing post in DB
    existing = db.query(Post).filter(Post.post_id == tweet_id).first()
    if existing:
        if existing.title.startswith("⚠️ Could not extract") and not tweet["text"].startswith("⚠️"):
            print(f"🧩 Updating tweet text for existing post {existing.id}")
            existing.title = tweet["text"][:120]
            db.commit()
            return existing.id
        else:
            print(f"ℹ️ Tweet already exists (Post ID: {existing.id}). Skipping insert.")
            return existing.id

    # Extract source domain (if any)
    article_url = tweet["links"][0] if tweet["links"] else None
    source = None
    if article_url:
        domain = urlparse(article_url).netloc
        source = db.query(Source).filter(Source.url_pattern.ilike(f"%{domain}%")).first()

    # Store new post
    post = Post(
        platform="Twitter",
        post_id=tweet_id,
        title=tweet["text"][:120],
        url=url,
        sentiment_score=None,
        credibility_score=None,
        source_id=source.id if source else None,
        verified_manual=False,
        upvotes=tweet["likes"],
        num_comments=tweet["replies"],
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    # Placeholder for future comments
    db.commit()

    # Compute advanced credibility
    score, explanation = compute_advanced_score(post, db)
    post.advanced_score = score
    post.score_explanation = explanation
    db.commit()

    print(f"✅ Tweet stored and scored. ID: {post.id}")
    return post.id
