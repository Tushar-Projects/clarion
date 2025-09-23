import os
import praw
from dotenv import load_dotenv
from urllib.parse import urlparse

from app.utils.database import SessionLocal
from app.models import Post, Comment, Source

# Load env vars
load_dotenv()

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_SECRET")
USER_AGENT = "clarion-app"

# Reddit API
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def clean_text(text: str) -> str:
    """Remove unsupported characters (like emojis)"""
    return text.encode("ascii", "ignore").decode("ascii")

def fetch_and_store_posts(subreddit_name="news", limit=10):
    db = SessionLocal()
    subreddit = reddit.subreddit(subreddit_name)

    for submission in subreddit.new(limit=limit):  # ✅ fetch newest posts
        existing_post = db.query(Post).filter_by(post_id=submission.id).first()

        # Match post source if possible
        source_id = None
        if submission.url:
            domain = urlparse(submission.url).netloc.replace("www.", "")
            source = db.query(Source).filter(Source.url_pattern.ilike(f"%{domain}%")).first()
            if source:
                source_id = source.id

        if existing_post:
            existing_post.title = clean_text(submission.title)
            existing_post.url = submission.url
            existing_post.source_id = source_id
            db.add(existing_post)
            post_record = existing_post
        else:
            new_post = Post(
                platform="Reddit",
                post_id=submission.id,
                title=clean_text(submission.title),
                url=submission.url,
                source_id=source_id
            )
            db.add(new_post)
            db.commit()
            db.refresh(new_post)
            post_record = new_post

        # ✅ Refresh comments (limit to top 20)
        submission.comments.replace_more(limit=0)
        db.query(Comment).filter_by(post_id=post_record.id).delete()
        for comment in submission.comments[:20]:
            new_comment = Comment(
                comment_id=comment.id,
                text=clean_text(comment.body),
                post_id=post_record.id
            )
            db.add(new_comment)

        db.commit()

    db.close()
    print(f"✅ Synced {limit} latest posts from r/{subreddit_name}")

def fetch_post_by_url(url: str):
    """Fetch a single Reddit post and its comments by URL"""
    db = SessionLocal()

    try:
        submission = reddit.submission(url=url)
        existing_post = db.query(Post).filter_by(post_id=submission.id).first()

        # Match source domain if available
        source_id = None
        if submission.url:
            domain = urlparse(submission.url).netloc.replace("www.", "")
            source = db.query(Source).filter(Source.url_pattern.ilike(f"%{domain}%")).first()
            if source:
                source_id = source.id

        if existing_post:
            existing_post.title = clean_text(submission.title)
            existing_post.url = submission.url
            existing_post.source_id = source_id
            db.add(existing_post)
            post_record = existing_post
        else:
            new_post = Post(
                platform="Reddit",
                post_id=submission.id,
                title=clean_text(submission.title),
                url=submission.url,
                source_id=source_id
            )
            db.add(new_post)
            db.commit()
            db.refresh(new_post)
            post_record = new_post

        # ✅ Refresh comments (limit to top 20)
        submission.comments.replace_more(limit=0)
        db.query(Comment).filter_by(post_id=post_record.id).delete()
        for comment in submission.comments[:20]:
            new_comment = Comment(
                comment_id=comment.id,
                text=clean_text(comment.body),
                post_id=post_record.id
            )
            db.add(new_comment)

        db.commit()
        return post_record.id

    except Exception as e:
        print(f"⚠️ Error fetching Reddit post: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    fetch_and_store_posts("news", limit=10)
