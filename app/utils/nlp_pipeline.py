import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sqlalchemy.orm import Session
from langdetect import detect, DetectorFactory

from app.utils.database import SessionLocal
from app.models import Post, Comment

# Fix randomness in langdetect
DetectorFactory.seed = 0

# -------------------------------
# Load Multilingual Sentiment Model
# -------------------------------
SENTIMENT_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL, use_fast=False)  # safer with SentencePiece
model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

# -------------------------------
# Dummy Sarcasm Detection
# -------------------------------
def detect_sarcasm(text: str) -> bool:
    sarcastic_keywords = ["yeah right", "totally", "as if", "sure thing", "/s"]
    return any(keyword in text.lower() for keyword in sarcastic_keywords)

# -------------------------------
# Language Detection
# -------------------------------
def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "unknown"

# -------------------------------
# Process Posts & Comments (Batched)
# -------------------------------
def process_posts_and_comments(batch_size: int = 16):
    db = SessionLocal()
    try:
        posts = db.query(Post).all()

        for post in posts:
            print(f"\n📰 Processing Post: {post.title[:80]}...")

            comments = db.query(Comment).filter(Comment.post_id == post.id).all()
            if not comments:
                continue

            texts = [c.text[:512] for c in comments]  # truncate to 512 tokens

            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_results = sentiment_pipeline(batch_texts)

                for comment, result in zip(comments[i:i + batch_size], batch_results):
                    try:
                        # Language detection
                        comment.language = detect_language(comment.text)

                        # Sentiment
                        label = result["label"].lower()
                        score = result["score"]

                        if "negative" in label:
                            comment.sentiment_score = -score
                        elif "positive" in label:
                            comment.sentiment_score = score
                        else:
                            comment.sentiment_score = 0

                        # Sarcasm Detection
                        comment.is_sarcastic = detect_sarcasm(comment.text)

                        db.add(comment)

                        # 🔎 Debug print
                        print(
                            f"💬 Comment {comment.id} → Lang: {comment.language}, "
                            f"Sentiment: {comment.sentiment_score:.3f}, "
                            f"Sarcasm: {comment.is_sarcastic}, "
                            f"Text: {comment.text[:60]}..."
                        )

                    except Exception as e:
                        print(f"⚠️ Error processing comment {comment.id}: {e}")

        db.commit()
        print("\n✅ NLP pipeline finished processing all posts and comments")

    except Exception as e:
        print(f"❌ NLP pipeline failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    process_posts_and_comments(batch_size=16)
