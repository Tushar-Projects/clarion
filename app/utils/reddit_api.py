import os
import praw
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Reddit API credentials from .env
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_SECRET")
USER_AGENT = "clarion-app"

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def fetch_reddit_posts(subreddit_name="news", limit=5):
    """Fetch latest posts from a subreddit"""
    subreddit = reddit.subreddit(subreddit_name)
    posts = []

    for submission in subreddit.hot(limit=limit):
        post_data = {
            "id": submission.id,
            "title": submission.title,
            "url": submission.url,
            "score": submission.score,
            "num_comments": submission.num_comments
        }
        posts.append(post_data)

    return posts


if __name__ == "__main__":
    # Test fetching
    results = fetch_reddit_posts("news", limit=5)
    for post in results:
        print(f"📰 {post['title']} ({post['url']})")
