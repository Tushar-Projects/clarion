from sqlalchemy import desc
from app.utils.database import SessionLocal
from app.models import Post
from app.utils import nlp_pipeline, credibility


def run_pipeline_for_new_posts(limit: int = 5):
    db = SessionLocal()
    try:
        # Step 1: Fetch only posts that need processing
        posts_query = db.query(Post).filter(
            (Post.credibility_score == None) | 
            (Post.advanced_score == None)
        ).filter(Post.verified_manual == False)

        # Step 2: Check if upvotes/num_comments exist in schema
        columns = [col.name for col in Post.__table__.columns]
        has_upvotes = "upvotes" in columns
        has_comments = "num_comments" in columns

        # Step 3: Apply sorting logic
        if has_upvotes and has_comments:
            posts_query = posts_query.order_by(
                desc(Post.upvotes + Post.num_comments)
            )
        else:
            # Fallback: newest posts by ID
            posts_query = posts_query.order_by(desc(Post.id))

        # Step 4: Limit to top N posts
        posts = posts_query.limit(limit).all()

        if not posts:
            print("✅ No new posts to process.")
            return

        print(f"🧠 Found {len(posts)} top posts to process.")
        for post in posts:
            print(f"🔹 Processing post {post.id}: {post.title[:80]}...")
            nlp_pipeline.process_single_post(post.id)
            credibility.compute_single_post(post.id)

        print("✅ Finished processing top posts.")
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_pipeline_for_new_posts(limit=5)
