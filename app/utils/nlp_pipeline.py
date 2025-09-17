from app.utils.database import SessionLocal
from app.models import Post, Comment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

# Initialize VADER
vader = SentimentIntensityAnalyzer()

# Initialize Hugging Face sentiment pipeline (default: DistilBERT)
hf_sentiment = pipeline("sentiment-analysis")

def analyze_vader(text: str) -> float:
    """Return sentiment score (-1 to +1) using VADER."""
    result = vader.polarity_scores(text)
    return result["compound"]

def analyze_hf(text: str) -> str:
    """Return Hugging Face sentiment label (POSITIVE/NEGATIVE/NEUTRAL)."""
    try:
        result = hf_sentiment(text[:512])[0]  # Truncate long comments to 512 tokens
        return result["label"]
    except Exception:
        return "NEUTRAL"

def detect_sarcasm(vader_score: float, hf_label: str) -> bool:
    """Flag sarcasm when VADER and Hugging Face strongly disagree."""
    if vader_score > 0.2 and hf_label == "NEGATIVE":
        return True
    if vader_score < -0.2 and hf_label == "POSITIVE":
        return True
    return False

def process_posts_and_comments():
    db = SessionLocal()

    # Process posts
    posts = db.query(Post).filter(Post.sentiment_score == None).all()
    for post in posts:
        if post.title:
            vader_score = analyze_vader(post.title)
            hf_label = analyze_hf(post.title)

            post.sentiment_score = vader_score
            # store HF sentiment in credibility_score temporarily (or make new column if you want)
            post.credibility_score = 1 if hf_label == "POSITIVE" else -1 if hf_label == "NEGATIVE" else 0

            db.add(post)

    # Process comments
    comments = db.query(Comment).filter(Comment.sentiment_score == None).all()
    for comment in comments:
        if comment.text:
            vader_score = analyze_vader(comment.text)
            hf_label = analyze_hf(comment.text)
            sarcastic = detect_sarcasm(vader_score, hf_label)

            comment.sentiment_score = vader_score
            # You can add a sarcasm flag column in DB, but for now let's just print
            if sarcastic:
                print(f"⚠️ Possible sarcasm detected in comment: {comment.text[:80]}...")

            db.add(comment)

    db.commit()
    db.close()
    print("✅ Sentiment + sarcasm analysis completed!")

if __name__ == "__main__":
    process_posts_and_comments()
