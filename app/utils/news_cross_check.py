import os
from newsapi import NewsApiClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Whitelist of high-trust domains
TRUSTED_DOMAINS = [
    "reuters.com",
    "apnews.com",
    "bbc.co.uk",
    "bbc.com",
    "npr.org",
    "pbs.org",
    "wsj.com",
    "bloomberg.com",
    "nytimes.com",
    "washingtonpost.com",
    "theguardian.com",
    "aljazeera.com",
    "dw.com",
    "france24.com",
    "ndtv.com",
    "indiatoday.in",
    "timesofindia.indiatimes.com",
    "thehindu.com",
    "indianexpress.com",
    "hindustantimes.com",
    "cnn.com",
    "foxnews.com",
    "usatoday.com"
]

def check_breaking_news(query: str) -> dict:
    """
    Checks if a breaking news topic is reported by trusted sources.
    Returns:
        {
            "match_count": int,
            "sources": list[str],
            "is_corroborated": bool,
            "score_modifier": float
        }
    """
    if not NEWS_API_KEY:
        print("⚠️ NEWS_API_KEY not set")
        return None

    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        
        # Search for the query
        # Clean query: take first 4 words to avoid overly specific searches
        # Ideally, we would use NLP to extract entities, but for now, simple truncation
        search_query = " ".join(query.split()[:4])
        print(f"📰 Searching NewsAPI for: '{search_query}'")
        
        response = newsapi.get_everything(
            q=search_query,
            language='en',
            sort_by='relevancy',
            page_size=20
        )
        
        print(f"📰 NewsAPI Status: {response.get('status')} | Total Results: {response.get('totalResults')}")

        if response['status'] != 'ok':
            return None
            
        matches = []
        for article in response['articles']:
            source_name = article['source']['name'].lower()
            url = article['url']
            
            # Check if source is in trusted list (by domain or name)
            is_trusted = any(domain in url for domain in TRUSTED_DOMAINS)
            
            if is_trusted:
                matches.append(article['source']['name'])
        
        unique_trusted_sources = list(set(matches))
        match_count = len(unique_trusted_sources)
        print(f"📰 Trusted Matches: {match_count} | Sources: {unique_trusted_sources}")
        
        # Scoring Logic
        score_modifier = 0.0
        is_corroborated = False
        
        if match_count >= 3:
            score_modifier = 0.4  # Strong corroboration
            is_corroborated = True
        elif match_count >= 1:
            score_modifier = 0.2  # Weak corroboration
            is_corroborated = True
        else:
            # If it claims to be breaking news but NO trusted source has it -> penalty
            # (We assume the caller only calls this for "breaking" or "news" posts)
            score_modifier = -0.2 
            
        return {
            "match_count": match_count,
            "sources": unique_trusted_sources,
            "is_corroborated": is_corroborated,
            "score_modifier": score_modifier
        }

    except Exception as e:
        print(f"❌ News API Error: {e}")
        return None
