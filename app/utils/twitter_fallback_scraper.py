import httpx
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urlparse
from app.models import Post, Comment, Source
from app.utils.credibility import compute_advanced_score

def load_cookie_dict(cookie_path: str) -> dict:
    """Load cookies from JSON file."""
    with open(cookie_path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_tweet_id(url: str) -> str | None:
    """Extract tweet ID from URL."""
    match = re.search(r"status/(\d+)", url)
    return match.group(1) if match else None

def fetch_tweet_html(url: str, cookies: dict) -> str | None:
    """Fetch the tweet HTML page using cookies."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }

    cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    headers["Cookie"] = cookie_str

    with httpx.Client(headers=headers, follow_redirects=True) as client:
        response = client.get(url)
        if response.status_code != 200:
            print(f"❌ Failed to fetch tweet HTML: {response.status_code}")
            return None
        return response.text

def parse_tweet(html: str):
    """Parse tweet HTML to extract content and links."""
    soup = BeautifulSoup(html, "html.parser")

    # Extract tweet text
    tweet_text_divs = soup.find_all("div", attrs={"data-testid": "tweetText"})
    text = " ".join([div.get_text(" ", strip=True) for div in tweet_text_divs]) if tweet_text_divs else None

    # Extract embedded links
    links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("http")]
    external_links = [l for l in links if not l.startswith("https://x.com")]

    # Extract author name
    author_tag = soup.find("div", attrs={"data-testid": "User-Name"})
    author = author_tag.get_text(" ", strip=True) if author_tag else "Unknown"

    # Extract engagement stats
    stats = {"likes": 0, "retweets": 0, "replies": 0}
    stat_spans = soup.find_all("span", string=re.compile(r"\d+"))
    for span in stat_spans:
        text = span.get_text(strip=True)
        if "like" in text.lower():
            stats["likes"] += int(re.sub(r"\D", "", text))
        elif "repost" in text.lower() or "retweet" in text.lower():
            stats["retweets"] += int(re.sub(r"\D", "", text))
        elif "reply" in text.lower():
            stats["replies"] += int(re.sub(r"\D", "", text))

    return {
        "author": author,
        "text": text or "⚠️ Could not extract tweet text.",
        "links": external_links,
        "stats": stats,
    }

def fetch_and_store_tweet(url: str, db):
    """Main entry — fetch tweet using HTML fallback and store in DB."""
    try:
        cookies = load_cookie_dict("app/twitter_session.json")
        html = fetch_tweet_html(url, cookies)
        if not html:
            return None

        tweet_data = parse_tweet(html)
        print("✅ Parsed tweet successfully:", tweet_data["text"][:100])

        # Check for external link
        article_url = tweet_data["links"][0] if tweet_data["links"] else None
        source = None
        if article_url:
            domain = urlparse(article_url).netloc
            source = db.query(Source).filter(Source.url_pattern.ilike(f"%{domain}%")).first()

        # Store post
        post = Post(
            platform="Twitter",
            post_id=extract_tweet_id(url),
            title=tweet_data["text"][:120],
            url=url,
            sentiment_score=None,
            credibility_score=None,
            source_id=source.id if source else None,
            verified_manual=False,
            upvotes=tweet_data["stats"]["likes"],
            num_comments=tweet_data["stats"]["replies"],
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        # Compute credibility score
        score, explanation = compute_advanced_score(post, db)
        post.advanced_score = score
        post.score_explanation = explanation
        db.commit()

        print(f"✅ Tweet stored and scored. ID: {post.id}")
        return post.id

    except Exception as e:
        print(f"❌ Error in fallback scraper: {e}")
        return None
