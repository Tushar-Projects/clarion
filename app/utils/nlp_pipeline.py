import os
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from sqlalchemy.orm import Session
from langdetect import detect, DetectorFactory
from functools import lru_cache
import html

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

SARCASM_MODEL = "cardiffnlp/twitter-roberta-base-irony"
sarcasm_tokenizer = AutoTokenizer.from_pretrained(SARCASM_MODEL)
sarcasm_model = AutoModelForSequenceClassification.from_pretrained(SARCASM_MODEL)
sarcasm_pipeline = pipeline("text-classification", model=sarcasm_model, tokenizer=sarcasm_tokenizer)

# simple cache to avoid repeated model calls for identical texts
@lru_cache(maxsize=2048)
def _model_predict_sarcasm(text: str):
    """Return (label, score) from sarcasm model; safe wrapper."""
    try:
        out = sarcasm_pipeline(text[:512])[0]
        return out.get("label", "").lower(), float(out.get("score", 0.0))
    except Exception:
        return None, 0.0

def _strip_markup_and_urls(text: str) -> str:
    # remove HTML entities, block quotes, markdown links and URLs
    t = html.unescape(text)
    t = re.sub(r"^>.*$", "", t, flags=re.MULTILINE)  # drop quoted lines
    # convert markdown links [text](url) -> text
    t = re.sub(r"\[([^\]]+)\]\((?:http[s]?:\/\/[^\)]+)\)", r"\1", t)
    # remove plain URLs
    t = re.sub(r"http\S+|www\.\S+", "", t)
    # collapse whitespace
    return re.sub(r"\s+", " ", t).strip()

def _all_caps_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper()) / len(letters)

# -------------------------------
# Sarcasm Detection
# -------------------------------
def detect_sarcasm(text: str) -> bool:
    """
    Ensemble sarcasm detector:
    - Strong rule-based checks for high-precision detection
    - Heuristic scoring for medium-confidence cases
    - Transformer model only as a tie-breaker (and only when useful)
    This function is deliberately conservative to minimize false positives.
    """
    try:
        if not text or not text.strip():
            return False

        # 1) Pre-cleaning
        raw = text
        cleaned = _strip_markup_and_urls(raw)
        lc = cleaned.lower()

        # 2) Quick negative filters (avoid false positives)
        # If the comment is extremely short and not an explicit '/s', unlikely sarcasm
        word_tokens = re.findall(r"\w+", lc)
        if len(word_tokens) <= 3 and not lc.strip().endswith("/s"):
            return False

        # If comment is essentially only a URL or "source: xyz", skip
        if len(re.sub(r"\W+", "", lc)) == 0:
            return False

        # 3) Strong explicit markers (very high precision)
        strong_markers = [
            "/s", "yeah right", "oh sure", "as if", "sure thing", "i'm sure", "right…", "right...", "totally", "nice one", "good one"
        ]
        for m in strong_markers:
            if m in lc:
                return True

        # 4) Heuristic cues (build a small score)
        h = 0.0
        # repeated punctuation (e.g., "!!", "...", "?!")
        if re.search(r"(\.{3,}|!!|!\?|\\\?\!|\?\!)", cleaned):
            h += 0.4
        # emoticons/emoji that often convey irony (eye-roll, smirk, etc.)
        if re.search(r"🙄|😒|😑|😏|/s", raw):
            h += 0.7
        # all-caps shouting (long enough)
        caps_ratio = _all_caps_ratio(cleaned)
        if caps_ratio > 0.6 and len(cleaned) > 8:
            h += 0.5
        # secondary phrases
        secondary_phrases = ["what a surprise", "yeah, right", "as if that would", "i bet", "imagine that"]
        for p in secondary_phrases:
            if p in lc:
                h += 0.6

        # 5) If heuristics are very confident -> accept
        if h >= 1.5:
            return True

        # 6) If heuristics strongly negative -> reject
        if h == 0.0 and len(word_tokens) <= 6:
            # no signals and short ⇒ avoid model call / return False
            return False

        # 7) Language gating: transformer's most reliable on English; skip heavy model for other languages
        try:
            lang = detect(raw)
        except Exception:
            lang = "unknown"

        # 8) Transformer (tie-breaker / recall enhancer)
        # Only use the model if heuristics suggest possible sarcasm OR text is long enough
        use_model = (h > 0.0) or (len(word_tokens) > 8)
        if lang in ("en", "unknown") and use_model:
            label, score = _model_predict_sarcasm(cleaned)
            if label is None:
                # model failure → fallback to heuristics threshold
                return h >= 1.0

            is_irony = any(k in label for k in ("irony", "ironic", "iron"))
            # Require high model confidence for short texts; allow moderate confidence for longer text with heuristic support
            if is_irony and score >= 0.85:
                return True
            if is_irony and score >= 0.65 and h >= 0.8:
                return True

        # default conservative decision
        return False

    except Exception as e:
        # keep pipeline robust: on unexpected errors, default to non-sarcastic
        print(f"⚠️ Sarcasm detection error: {e}")
        return False
    

# -------------------------------
# Language Detection
# -------------------------------
def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "unknown"

# -------------------------------
# Process ALL Posts & Comments (Batched)
# -------------------------------
def process_posts_and_comments(batch_size: int = 16):
    db = SessionLocal()
    try:
        posts = db.query(Post).all()
        for post in posts:
            _process_post_comments(db, post, batch_size)
        db.commit()
        print("\n✅ NLP pipeline finished processing all posts and comments")
    except Exception as e:
        print(f"❌ NLP pipeline failed: {e}")
    finally:
        db.close()

# -------------------------------
# Process ONE Post by ID
# -------------------------------
def process_single_post(post_id: int, batch_size: int = 16):
    db = SessionLocal()
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            print(f"⚠️ Post {post_id} not found")
            return
        _process_post_comments(db, post, batch_size)
        db.commit()
        print(f"\n✅ NLP pipeline finished processing post {post.id}")
    except Exception as e:
        print(f"❌ NLP pipeline failed on single post {post_id}: {e}")
    finally:
        db.close()

# -------------------------------
# Shared Processing Logic
# -------------------------------
def _process_post_comments(db, post, batch_size: int):
    print(f"\n📰 Processing Post: {post.title[:80]}...")

    comments = db.query(Comment).filter(Comment.post_id == post.id).all()
    if not comments:
        print("⚠️ No comments found for this post")
        return

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

# -------------------------------
# Main Entrypoint
# -------------------------------
if __name__ == "__main__":
    process_posts_and_comments(batch_size=16)
