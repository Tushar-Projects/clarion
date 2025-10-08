import os
import re
from dotenv import load_dotenv
from urllib.parse import urlparse

from app.utils.database import SessionLocal
from app.models import Post, Comment, Source

# Load env vars
load_dotenv()

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_SECRET")
USER_AGENT = "clarion-app"

# Reddit import lazy so module doesn't fail if PRAW not installed in some contexts
try:
    import praw
    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)
except Exception as e:
    reddit = None
    print(f"⚠️ Warning: praw not available ({e})")


def clean_text(text: str) -> str:
    """Remove unsupported characters (like emojis)"""
    if not text:
        return ""
    return text.encode("ascii", "ignore").decode("ascii").strip()


def _is_valid_comment(text: str) -> bool:
    """
    Return True if comment text is worth storing:
      - not [removed] / [deleted]
      - not empty or only whitespace
      - not link-only (http(s) or markdown link)
      - not extremely short (after removing whitespace)
    """
    if not text:
        return False

    txt = text.strip()
    if not txt:
        return False

    low = txt.lower()
    if low in ("[removed]", "[deleted]"):
        return False

    # markdown link only: [title](http...)
    if re.match(r"^\[.*\]\(https?://\S+\)$", txt):
        return False

    # plain URL only: http://... or www....
    if re.match(r"^(https?://\S+|www\.\S+)$", txt):
        return False

    # image hosting short links (i.redd.it, v.redd.it) — treat as link-only
    if re.match(r"^(https?://)?(i|v)\.redd\.it/\S+$", txt):
        return False

    # too short (only punctuation or <5 non-space chars) — skip
    non_space_len = len(re.sub(r"\s+", "", txt))
    if non_space_len < 5:
        return False

    return True


def fetch_and_store_posts(subreddit_name="news", limit=10):
    """Fetch newest posts from a subreddit and store/update them and filtered comments."""
    if reddit is None:
        print("⚠️ reddit client not initialized.")
        return

    db = SessionLocal()
    try:
        subreddit = reddit.subreddit(subreddit_name)
        for submission in subreddit.new(limit=limit):
            # check existing post
            existing_post = db.query(Post).filter_by(post_id=submission.id).first()

            # match source domain if possible
            source_id = None
            if submission.url:
                domain = urlparse(submission.url).netloc.replace("www.", "")
                source = db.query(Source).filter(Source.url_pattern.ilike(f"%{domain}%")).first()
                if source:
                    source_id = source.id

            # ✅ updated: track upvotes and comment counts
            if existing_post:
                existing_post.title = clean_text(submission.title)
                existing_post.url = submission.url
                existing_post.source_id = source_id
                existing_post.upvotes = submission.score or 0
                existing_post.num_comments = submission.num_comments or 0
                db.add(existing_post)
                post_record = existing_post
            else:
                new_post = Post(
                    platform="Reddit",
                    post_id=submission.id,
                    title=clean_text(submission.title),
                    url=submission.url,
                    source_id=source_id,
                    upvotes=submission.score or 0,
                    num_comments=submission.num_comments or 0,
                )
                db.add(new_post)
                db.commit()
                db.refresh(new_post)
                post_record = new_post

            # Refresh comments: remove old stored comments and insert filtered ones
            submission.comments.replace_more(limit=0)
            db.query(Comment).filter_by(post_id=post_record.id).delete()  # delete old comments

            # iterate top-level comments (limit to 20 by default here)
            for comment in submission.comments[:20]:
                body = getattr(comment, "body", None)
                if not _is_valid_comment(body):
                    continue
                new_comment = Comment(
                    comment_id=comment.id,
                    text=clean_text(body),
                    post_id=post_record.id
                )
                db.add(new_comment)

            # commit after each post processed to keep DB consistent
            db.commit()

        print("✅ Fetched and stored subreddit posts (filtered comments).")
    except Exception as e:
        print(f"⚠️ Error fetching posts: {e}")
    finally:
        db.close()


def fetch_post_by_url(url: str, comment_limit: int = 20):
    """Fetch a single Reddit post and its comments by URL, store filtered comments only."""
    if reddit is None:
        print("⚠️ reddit client not initialized.")
        return None

    db = SessionLocal()
    try:
        submission = reddit.submission(url=url)

        # Check if post already exists in DB
        existing_post = db.query(Post).filter_by(post_id=submission.id).first()

        # Match source domain if available
        source_id = None
        if submission.url:
            domain = urlparse(submission.url).netloc.replace("www.", "")
            source = db.query(Source).filter(Source.url_pattern.ilike(f"%{domain}%")).first()
            if source:
                source_id = source.id

        # ✅ updated: include upvotes and num_comments
        if existing_post:
            existing_post.title = clean_text(submission.title)
            existing_post.url = submission.url
            existing_post.source_id = source_id
            existing_post.upvotes = submission.score or 0
            existing_post.num_comments = submission.num_comments or 0
            db.add(existing_post)
            db.commit()
            db.refresh(existing_post)
            post_record = existing_post
        else:
            new_post = Post(
                platform="Reddit",
                post_id=submission.id,
                title=clean_text(submission.title),
                url=submission.url,
                source_id=source_id,
                upvotes=submission.score or 0,
                num_comments=submission.num_comments or 0,
            )
            db.add(new_post)
            db.commit()
            db.refresh(new_post)
            post_record = new_post

        # Refresh comments and insert filtered ones
        submission.comments.replace_more(limit=0)
        db.query(Comment).filter_by(post_id=post_record.id).delete()  # clear old

        # Use top-level comments up to comment_limit
        for comment in submission.comments[:comment_limit]:
            body = getattr(comment, "body", None)
            if not _is_valid_comment(body):
                continue
            new_comment = Comment(
                comment_id=comment.id,
                text=clean_text(body),
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


# If run directly, sync some sample posts for quick testing
if __name__ == "__main__":
    if reddit:
        fetch_and_store_posts("news", limit=5)
    else:
        print("praw not configured.")
