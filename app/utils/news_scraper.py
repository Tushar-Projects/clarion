import re
import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from newspaper import Article
from app.utils.database import SessionLocal
from app.models import Post, Source

def clean_text(text: str) -> str:
    """Cleans article text by removing unwanted characters and extra whitespace."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)  # normalize spaces
    text = re.sub(r"http\S+", "", text)  # remove URLs
    return text.strip()

def extract_domain(url: str) -> str:
    """Extracts clean domain from URL (without www)."""
    return urlparse(url).netloc.replace("www.", "")

def scrape_article_content(url: str) -> dict:
    """
    Scrape article text and metadata.
    Uses newspaper3k when available, otherwise falls back to BeautifulSoup.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        title = clean_text(article.title)
        text = clean_text(article.text)
        if text and len(text) > 100:
            return {"title": title, "text": text}
    except Exception:
        pass  # fallback below if newspaper3k fails

    # Fallback to BeautifulSoup
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Try extracting <title>
        title = soup.title.string if soup.title else ""

        # Extract main paragraphs
        paragraphs = [p.get_text() for p in soup.find_all("p") if len(p.get_text()) > 40]
        text = clean_text(" ".join(paragraphs))

        return {"title": title, "text": text}
    except Exception as e:
        print(f"⚠️ Error scraping article: {e}")
        return {"title": "", "text": ""}

def fetch_and_store_article(url: str):
    """
    Fetch a news article and store it in the database.
    Returns post_id if successful, else None.
    """
    db = SessionLocal()
    try:
        domain = extract_domain(url)
        data = scrape_article_content(url)
        if not data["title"] and not data["text"]:
            print("⚠️ No valid content found in article.")
            return None
        elif len(data["text"]) < 100:
            print(f"⚠️ Article text short ({len(data['text'])} chars), keeping anyway.")


        # Match or create Source
        source = db.query(Source).filter(Source.url_pattern.ilike(f"%{domain}%")).first()
        if not source:
            try:
        # Some DB schemas have reliability_score, others don’t
                source = Source(name=domain.title(), url_pattern=domain)
                if hasattr(Source, "reliability_score"):
                    setattr(source, "reliability_score", 0.0)
                db.add(source)
                db.commit()
                db.refresh(source)
            except Exception as e:
                print(f"⚠️ Error creating source entry: {e}")

        # Check if post already exists
        existing_post = db.query(Post).filter_by(url=url).first()
        if existing_post:
            existing_post.title = data["title"]
            existing_post.platform = "News"
            existing_post.source_id = source.id
            db.add(existing_post)
            db.commit()
            print(f"🔁 Updated existing article: {existing_post.title}")
            return existing_post.id

        # Otherwise, create new post
        new_post = Post(
            platform="News",
            title=data["title"],
            url=url,
            source_id=source.id
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        print(f"📰 Stored new article: {new_post.title}")
        return new_post.id

    except Exception as e:
        print(f"❌ Error storing article: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    # Test with an example article
    test_url = "https://www.bbc.com/news/world-67215728"
    post_id = fetch_and_store_article(test_url)
    print(f"✅ Stored post id: {post_id}")
