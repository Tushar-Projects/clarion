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

# --- Fix for Windows encoding issues ---
def clean_text(text: str) -> str:
    """Remove characters (like emojis) PostgreSQL can't store on Windows."""
    return text.encode("ascii", "ignore").decode("ascii")


def fetch_and_store_posts(subreddit_name="news", limit=5):
    db = SessionLocal()
    subreddit = reddit.subreddit(subreddit_name)

    for submission in subreddit.hot(limit=limit):
        # Skip if already stored
        existing_post = db.query(Post).filter_by(post_id=submission.id).first()
        if existing_post:
            continue

        # Match post source if possible
        source_id = None
        if submission.url:
            domain = urlparse(submission.url).netloc.replace("www.", "")
            source = db.query(Source).filter(Source.url_pattern.ilike(f"%{domain}%")).first()
            if source:
                source_id = source.id

        # Store post
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

        # Fetch comments (limit to 5 for testing)
        submission.comments.replace_more(limit=0)
        for comment in submission.comments[:5]:
            try:
                new_comment = Comment(
                    comment_id=comment.id,
                    text=clean_text(comment.body),
                    post_id=new_post.id
                )
                db.add(new_comment)
            except Exception as e:
                print(f"⚠️ Skipped a comment due to error: {e}")
        
    db.commit()

    db.close()
    print(f"✅ Stored {limit} posts from r/{subreddit_name}")


if __name__ == "__main__":
    fetch_and_store_posts("news", limit=5)
