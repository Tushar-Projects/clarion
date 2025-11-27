from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from app.utils.database import SessionLocal
from app.models import Post, Source, Comment
from app.utils import reddit_api, nlp_pipeline, credibility, news_scraper

app = Flask(__name__)
CORS(app)


# ---------------------------
# Helpers (serializer)
# ---------------------------
def comment_to_dict(comment):
    return {
        "id": comment.id,
        "text": comment.text,
        "sentiment_score": comment.sentiment_score,
        "is_sarcastic": bool(getattr(comment, "is_sarcastic", 0)),
    }


def post_to_dict(post, include_comments=False):
    """
    IMPORTANT: We surface `advanced_score` as the primary score for the UI.
    The field name the frontend reads is still `credibility_score` (per your UI),
    but its value comes from `advanced_score` when available.
    """
    chosen_score = post.advanced_score if post.advanced_score is not None else post.credibility_score

    data = {
        "id": post.id,
        "platform": post.platform,
        "title": post.title,
        "url": post.url,
        "post_id": post.post_id,

        # Frontend reads this field; we feed it advanced_score by default:
        "credibility_score": chosen_score,

        # Also include the raw advanced_score for charts, etc.
        "advanced_score": post.advanced_score,

        "community_sentiment": post.community_sentiment,
        "score_explanation": post.score_explanation,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "status": "scored" if chosen_score is not None else "insufficient_data",
        
        # --- New Reliability Fields ---
        "sensationalism_score": post.sensationalism_score,
        "llm_verdict": post.llm_verdict,
        "corroboration_score": post.corroboration_score,
        "image_provenance_status": post.image_provenance_status,
        "original_image_date": post.original_image_date.isoformat() if post.original_image_date else None,
    }

    if include_comments:
        data["comments"] = [comment_to_dict(c) for c in post.comments]

    return data


# ---------------------------
# Home
# ---------------------------
@app.route("/")
def home():
    return jsonify({"message": "Fake News Credibility API is running ✅"})


# ---------------------------
# Posts + Post (with comments)
# ---------------------------
@app.route("/posts", methods=["GET"])
def get_posts():
    db = SessionLocal()
    try:
        posts = db.query(Post).order_by(Post.created_at.desc()).all()
        results = [post_to_dict(p, include_comments=True) for p in posts]
        return jsonify(results)
    finally:
        db.close()


@app.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    db = SessionLocal()
    try:
        post = db.query(Post).filter_by(id=post_id).first()
        if not post:
            return jsonify({"error": "Post not found"}), 404
        result = post_to_dict(post, include_comments=True)
        return jsonify(result)
    finally:
        db.close()


# ---------------------------
# Search
# ---------------------------
@app.route("/search", methods=["GET"])
def search_posts():
    query = request.args.get("q", "")
    db = SessionLocal()
    try:
        posts = db.query(Post).filter(Post.title.ilike(f"%{query}%")).all()
        results = [post_to_dict(p, include_comments=False) for p in posts]
        return jsonify(results)
    finally:
        db.close()


# ---------------------------
# Check a single URL (legacy path kept)
# ---------------------------
@app.route("/check_url", methods=["POST"])
def check_url():
    data = request.get_json()
    url = (data.get("url") or "").strip() if data else ""

    if not url:
        return jsonify({"error": "Please provide a valid URL"}), 400

    db = SessionLocal()
    platform = "Unknown"
    post_id = None

    try:
        if "reddit.com" in url:
            platform = "Reddit"
            post_id = reddit_api.fetch_post_by_url(url)
            if not post_id:
                return jsonify({"error": "Could not fetch Reddit post"}), 500
            nlp_pipeline.process_single_post(post_id)
            credibility.compute_single_post(post_id)

        elif "twitter.com" in url or "x.com" in url:
            from app.utils.twitter_fallback_scraper import fetch_and_store_tweet
            platform = "Twitter"
            post_id = fetch_and_store_tweet(url, db)
            if not post_id:
                return jsonify({"error": "Could not fetch tweet"}), 500
            credibility.compute_single_post(post_id)

        else:
            platform = "News"
            post_id = news_scraper.fetch_and_store_article(url)
            if not post_id:
                return jsonify({"error": "Could not fetch article"}), 500
            credibility.compute_single_post(post_id)

        # mark + respond
        post = db.query(Post).filter_by(id=post_id).first()
        if post:
            post.verified_manual = True
            post.platform = platform
            db.add(post)
            db.commit()

            result = post_to_dict(post, include_comments=False)
            result["platform"] = platform
            return jsonify(result)
        else:
            return jsonify({"error": "Post not found after processing", "platform": platform}), 404

    except Exception as e:
        print(f"❌ Error in /check_url: {e}")
        return jsonify({"error": str(e), "platform": platform}), 500
    finally:
        db.close()


@app.route("/check", methods=["GET"])
def check_page():
    return render_template("check_url.html")


# ---------------------------
# Top Posts (with light auto-ingestion)
# ---------------------------
def _auto_ingest_top_posts_if_possible(source: str, db, limit: int = 5) -> int:
    """
    Try to ingest a few top posts to avoid empty 'Top Posts' pages.
    We only touch Reddit here because your reddit_api is already configured.
    This is safe and will no-op if the helper isn’t present in your module.
    Returns how many items were ingested.
    """
    ingested = 0

    try:
        want_reddit = source in ("all", "reddit")

        if want_reddit:
            # Try a few possible helper names without breaking anything if absent.
            fetcher = None
            for name in ("fetch_top_posts", "fetch_top_post_urls", "get_top_post_urls"):
                if hasattr(reddit_api, name):
                    fetcher = getattr(reddit_api, name)
                    break

            if fetcher:
                try:
                    urls = fetcher(limit=limit)  # expect a list of post URLs
                except TypeError:
                    # fallback if function has no 'limit' parameter
                    urls = fetcher()

                if urls:
                    for url in urls[:limit]:
                        try:
                            pid = reddit_api.fetch_post_by_url(url)
                            if pid:
                                nlp_pipeline.process_single_post(pid)
                                credibility.compute_single_post(pid)
                                ingested += 1
                        except Exception as e:
                            print(f"⚠️ Ingest error for {url}: {e}")
            else:
                print("ℹ️ reddit_api has no top-posts fetch helper; skipping auto-ingest.")

    except Exception as e:
        print(f"⚠️ Auto-ingest failed: {e}")

    return ingested


@app.route("/top-posts", methods=["GET"])
def top_posts():
    source = request.args.get("source", "all").lower()
    force_refresh = request.args.get("force_refresh", "false").lower() == "true"
    
    # Determine what to fetch if we need to fetch
    fetch_source = source
    if fetch_source == "all":
        fetch_source = "news"

    db = SessionLocal()
    try:
        # 1. Check if we have recent posts for this source
        import datetime
        now = datetime.datetime.utcnow()
        # Filter by time (last 1.2 hours = 72 mins) to ensure we only show currently active posts
        # If a post was deleted, it won't be in the fresh fetch, so its created_at won't be updated.
        cutoff = now - datetime.timedelta(minutes=72)

        base_query = db.query(Post).filter(Post.platform == "Reddit")
        
        # Only filter by subreddit if not "all"
        if source != "all":
             base_query = base_query.filter(Post.subreddit.ilike(source))

        # Filter by time
        base_query = base_query.filter(Post.created_at >= cutoff)

        latest_post = base_query.order_by(Post.created_at.desc()).first()
        
        should_fetch = False
        if force_refresh:
            should_fetch = True
            print(f"ℹ️ Force refresh requested for r/{fetch_source}...")
        elif not latest_post:
            should_fetch = True
            print(f"ℹ️ No posts found for r/{fetch_source} — fetching fresh data...")
        else:
            # Check age
            import datetime
            now = datetime.datetime.utcnow()
            # If latest post is older than 1 hour (60 mins)
            age = now - latest_post.created_at
            if age.total_seconds() > 3600: # 1 hour
                should_fetch = True
                print(f"ℹ️ Data for r/{fetch_source} is stale ({age}) — fetching fresh data...")

        if should_fetch:
            from app.utils.reddit_api import fetch_and_store_posts
            # Fetch fresh posts
            fetch_and_store_posts(fetch_source, limit=10)
            
            # 🔥 CRITICAL: Expire session to see changes made by fetch_and_store_posts (which used a different session)
            db.expire_all()
            
            # Re-score newly inserted posts
            # We query specifically for the fetched source to ensure we score them
            score_query = db.query(Post).filter(Post.platform == "Reddit")
            if source != "all":
                score_query = score_query.filter(Post.subreddit.ilike(source))
            else:
                # If source was all, we fetched 'news', so maybe just score recent reddit posts generally
                pass 
            
            recent_posts = score_query.order_by(Post.created_at.desc()).limit(10).all()
            
            for p in recent_posts:
                # Run pipeline if scores are missing
                if p.advanced_score is None and p.credibility_score is None:
                    print(f"🔍 Scoring new post: {p.id}...")
                    nlp_pipeline.process_single_post(p.id)
                    credibility.compute_single_post(p.id)
            
            # Commit the scores
            db.commit()

        # 2. Return results
        posts = (
            base_query.order_by(Post.advanced_score.desc().nullslast(), Post.created_at.desc())
            .limit(20)
            .all()
        )

        results = [post_to_dict(p, include_comments=False) for p in posts]
        return jsonify({"source": source, "results": results})
    except Exception as e:
        print(f"❌ Error in top_posts: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()



# ---------------------------
# Check Post (GET or POST)
# ---------------------------
@app.route("/check-post", methods=["GET", "POST"])
def check_post():
    recalculate = False
    if request.method == "GET":
        url = (request.args.get("url") or "").strip()
        recalculate = request.args.get("recalculate", "false").lower() == "true"
    else:
        body = request.get_json(silent=True) or {}
        url = (body.get("url") or "").strip()
        recalculate = body.get("recalculate", False)

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    from app.utils.reddit_api import fetch_post_by_url
    from app.utils.credibility import compute_single_post
    from app.utils.nlp_pipeline import process_single_post
    from app.utils.twitter_fallback_scraper import fetch_and_store_tweet
    from app.utils import news_scraper

    db = SessionLocal()
    platform = "Unknown"
    post_id = None
    previous_result = None

    try:
        # 1. Check if we have this URL exactly in DB
        existing_post = db.query(Post).filter(Post.url == url).first()

        if existing_post:
            if not recalculate:
                # Return existing immediately
                print(f"⚡ Returning cached result for {url}")
                return jsonify(post_to_dict(existing_post))
            else:
                # Capture previous state for diff
                previous_result = post_to_dict(existing_post)
                print(f"🔄 Recalculating for {url}...")

        if "reddit.com" in url:
            platform = "Reddit"
            post_id = fetch_post_by_url(url)
            process_single_post(post_id)
            compute_single_post(post_id)

        elif "twitter.com" in url or "x.com" in url:
            platform = "Twitter"
            post_id = fetch_and_store_tweet(url, db)
            compute_single_post(post_id)

        elif url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')) or ".jpg?" in url.lower() or ".png?" in url.lower():
            # Handle direct image links
            platform = "Image"
            # Create a dummy post for the image if it doesn't exist
            existing_post = db.query(Post).filter_by(url=url).first()
            if existing_post:
                post_id = existing_post.id
            else:
                new_post = Post(
                    platform="Image",
                    title="Image Verification", # Placeholder title
                    url=url,
                    source_id=None # No specific source for raw images
                )
                db.add(new_post)
                db.commit()
                db.refresh(new_post)
                post_id = new_post.id
            
            compute_single_post(post_id)

        else:
            platform = "News"
            post_id = news_scraper.fetch_and_store_article(url)
            compute_single_post(post_id)

        # Refresh session to ensure we see updates from compute_single_post (which uses a separate session)
        db.expire_all()
        post = db.query(Post).filter_by(id=post_id).first()
        if not post:
            return jsonify({"error": "Post not found after scoring"}), 404

        # Return advanced score as the primary "credibility_score"
        result = {
            "title": post.title,
            "platform": platform,
            "credibility_score": post.advanced_score if post.advanced_score is not None else post.credibility_score,
            "advanced_score": post.advanced_score,
            "community_sentiment": post.community_sentiment,
            "url": post.url, # Ensure we return the canonical URL
        }
        
        if previous_result:
            result["previous_result"] = previous_result

        return jsonify(result)

    finally:
        db.close()


# ---------------------------
# History
# ---------------------------
@app.route("/history", methods=["GET"])
def history():
    db = SessionLocal()
    try:
        posts = db.query(Post).order_by(Post.created_at.desc()).limit(50).all()
        results = [post_to_dict(p) for p in posts]
        return jsonify(results)
    finally:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
