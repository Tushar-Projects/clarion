from app.utils.database import SessionLocal
from app.models import Post, Comment, Source

def compute_credibility():
    db = SessionLocal()

    posts = db.query(Post).all()
    for post in posts:
        # ✅ Step 1: Get source trust score
        source_score = 5  # default
        if post.source_id:
            source = db.query(Source).filter_by(id=post.source_id).first()
            if source:
                source_score = source.trust_score  # 1–10

        # ✅ Step 2: Average comment sentiment
        comments = db.query(Comment).filter_by(post_id=post.id).all()
        if comments:
            avg_sentiment = sum(c.sentiment_score or 0 for c in comments) / len(comments)
        else:
            avg_sentiment = 0

        # ✅ Step 3: Sarcasm penalty
        sarcastic_comments = [c for c in comments if getattr(c, "is_sarcastic", 0) == 1]
        sarcasm_ratio = len(sarcastic_comments) / len(comments) if comments else 0
        sarcasm_penalty = 1 - sarcasm_ratio  # more sarcasm = lower credibility

        # ✅ Step 4: Combine into credibility score
        # Scale: (source reliability * (1 + avg_sentiment)) * sarcasm factor
        raw_score = (source_score / 10) * (1 + avg_sentiment) * sarcasm_penalty

        # Normalize to 0–1 range
        credibility = max(0, min(raw_score, 1))

        # ✅ Save back to DB
        post.credibility_score = credibility
        db.add(post)

    db.commit()
    db.close()
    print("✅ Credibility scores updated!")

if __name__ == "__main__":
    compute_credibility()
