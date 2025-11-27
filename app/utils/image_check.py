import os
from serpapi import GoogleSearch
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def check_image_provenance(image_url: str) -> dict:
    """
    Checks if an image has been used before (reverse image search).
    Returns:
        {
            "is_recycled": bool,
            "first_seen_date": datetime | None,
            "status": str, # 'original', 'recycled', 'unknown'
            "score_modifier": float
        }
    """
    if not SERPAPI_API_KEY or not image_url:
        return None

    try:
        params = {
            "engine": "google_lens",
            "url": image_url,
            "api_key": SERPAPI_API_KEY
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "visual_matches" not in results:
            return {"status": "unknown", "score_modifier": 0.0}
            
        matches = results["visual_matches"]
        if not matches:
            return {"status": "original", "score_modifier": 0.1} # Slight boost for original content
            
        # Check for old dates in visual matches
        # Note: SerpApi results for Google Lens are tricky with dates. 
        # We look for "X years ago" or specific date strings in the snippet/source.
        
        is_recycled = False
        oldest_date = None
        
        # Simple heuristic: if we find many matches from trusted news sites from the past, it's recycled.
        # For now, we'll just check if there are matches that are clearly NOT from today/yesterday.
        # This is a simplification as parsing dates from snippets is hard without structured data.
        
        # A safer heuristic for "fake news" detection:
        # If the image appears in "Fact Check" results or "Debunking" sites.
        
        # Let's try to find explicit date indicators in snippets
        current_year = datetime.now().year
        
        for match in matches[:10]: # Check top 10 matches
            title = match.get("title", "").lower()
            source = match.get("source", "").lower()
            
            # If we see a year that is not current year, it's likely old
            # Regex for 2010-2024 (excluding current year if possible, but let's just look for < current_year)
            years = re.findall(r"20[1-2][0-9]", title + " " + source)
            for year in years:
                if int(year) < current_year:
                    is_recycled = True
                    # We found an old year
                    return {
                        "is_recycled": True,
                        "status": "recycled",
                        "score_modifier": -0.8, # Heavy penalty for recycled images
                        "reason": f"Image found in content from {year}"
                    }
                    
        # If no old dates found, but many matches exist, it might just be viral today.
        # We return neutral if no definitive "old" signal found.
        return {
            "is_recycled": False,
            "status": "viral_or_original",
            "score_modifier": 0.0
        }

    except Exception as e:
        print(f"❌ Image Check Error: {e}")
        return None
