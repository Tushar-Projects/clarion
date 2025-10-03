from flask import Flask, jsonify, request, render_template
from app.utils.database import SessionLocal
from app.models import Post, Source, Comment
from app.utils import reddit_api, nlp_pipeline, credibility

app = Flask(__name__)

# Utility: Convert Comment object to dict
def comment_to_dict(comment):
    return {
        "id": comment.id,
        "text": comment.text,
        "sentiment_score": comment.sentiment_score,
        "is_sarcastic": bool(getattr(comment, "is_sarcastic", 0))
    }

# Utility: Convert Post object to dict
def post_to_dict(post, include_comments=False):
    data = {
        "id": post.id,
        "platform": post.platform,
        "title": post.title,
        "url": post.url,
        "credibility_score": post.credibility_score,
        "advanced_score": post.advanced_score,
        "community_sentiment": post.community_sentiment,
        "score_explanation": post.score_explanation,
        "created_at": post.created_at.isoformat() if post.created_at else None,
    }
    if post.credibility_score is None:
        data["credibility_score"] = None
        data["status"] = "insufficient_data"
    else:
        data["credibility_score"] = post.credibility_score
        data["advanced_score"] = post.advanced_score
        data["status"] = "scored"

    if include_comments:
        data["comments"] = [comment_to_dict(c) for c in post.comments]

    return data

@app.route("/")
def home():
    return jsonify({"message": "Fake News Credibility API is running ✅"})

# 1️⃣ Get all posts with comments
@app.route("/posts", methods=["GET"])
def get_posts():
    db = SessionLocal()
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    results = [post_to_dict(p, include_comments=True) for p in posts]
    db.close()
    return jsonify(results)

# 2️⃣ Get single post by ID (with comments)
@app.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    db = SessionLocal()
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        db.close()
        return jsonify({"error": "Post not found"}), 404
    result = post_to_dict(post, include_comments=True)
    db.close()
    return jsonify(result)

# 3️⃣ Search posts by keyword
@app.route("/search", methods=["GET"])
def search_posts():
    query = request.args.get("q", "")
    db = SessionLocal()
    posts = db.query(Post).filter(Post.title.ilike(f"%{query}%")).all()
    results = [post_to_dict(p, include_comments=False) for p in posts]
    db.close()
    return jsonify(results)

# 4️⃣ Check credibility for a pasted Reddit URL
@app.route("/check_url", methods=["POST"])
def check_url():
    data = request.get_json()
    url = data.get("url")

    if not url or "reddit.com" not in url:
        return jsonify({"error": "Only Reddit URLs are supported for now"}), 400

    # ✅ Fetch exact Reddit post by URL
    post_id = reddit_api.fetch_post_by_url(url)
    if not post_id:
        return jsonify({"error": "Could not fetch Reddit post"}), 500

    # ✅ Force NLP pipeline for this post
    nlp_pipeline.process_single_post(post_id)

    # ✅ Force credibility calculation for this post
    credibility.compute_single_post(post_id)

    # ✅ Query DB for updated post
    db = SessionLocal()
    post = db.query(Post).filter_by(id=post_id).first()
    result = post_to_dict(post, include_comments=True)
    db.close()

    return jsonify(result)


@app.route("/check", methods=["GET"])
def check_page():
    return render_template("check_url.html")

if __name__ == "__main__":
    app.run(debug=True)
