from app.utils.database import SessionLocal
from app.models import Post
from app.utils import nlp_pipeline, credibility
import subprocess
import sys

def run_pipeline_for_new_posts():
    db = SessionLocal()
    try:
        posts = db.query(Post).filter(
            (Post.credibility_score == None) | 
            (Post.advanced_score == None)
        ).filter(Post.verified_manual == False).all()

        if not posts:
            print("✅ No new posts to process.")
            return

        print(f"🧠 Found {len(posts)} new/unprocessed posts.")
        for post in posts:
            print(f"🔹 Processing post {post.id}: {post.title[:80]}...")
            nlp_pipeline.process_single_post(post.id)
            credibility.compute_single_post(post.id)

        print("✅ Finished processing new posts.")
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_pipeline_for_new_posts()

