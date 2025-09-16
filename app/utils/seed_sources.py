from app.utils.database import SessionLocal, init_db
from app.models import Source

def seed_sources():
    # Initialize DB
    init_db()
    db = SessionLocal()

    sources = [
        {"name": "BBC News", "url_pattern": "bbc.com", "trust_score": 9},
        {"name": "The New York Times", "url_pattern": "nytimes.com", "trust_score": 9},
        {"name": "The Guardian", "url_pattern": "theguardian.com", "trust_score": 8},
        {"name": "Fox News", "url_pattern": "foxnews.com", "trust_score": 6},
        {"name": "NDTV", "url_pattern": "ndtv.com", "trust_score": 7},
        {"name": "Hindustan Times", "url_pattern": "hindustantimes.com", "trust_score": 7},
        {"name": "Random Blog", "url_pattern": "randomblog.net", "trust_score": 2},
        {"name": "Satire News", "url_pattern": "satiretimes.com", "trust_score": 1},
    ]

    for src in sources:
        existing = db.query(Source).filter_by(url_pattern=src["url_pattern"]).first()
        if not existing:
            new_source = Source(
                name=src["name"],
                url_pattern=src["url_pattern"],
                trust_score=src["trust_score"]
            )
            db.add(new_source)

    db.commit()
    db.close()
    print("✅ Sources table seeded successfully!")

if __name__ == "__main__":
    seed_sources()
