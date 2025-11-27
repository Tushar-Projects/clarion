import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def configure_genai():
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY not set")
        return False
    genai.configure(api_key=GEMINI_API_KEY)
    return True

def analyze_content_with_llm(title: str, text: str = "") -> dict:
    """
    Analyzes the post content for sensationalism, logical fallacies, and overall credibility.
    Returns a dictionary with scores and reasoning.
    """
    if not configure_genai():
        return None

    model = genai.GenerativeModel('gemini-2.0-flash')

    prompt = f"""
    Analyze the following news/social media post for credibility.
    
    Title: "{title}"
    Content Snippet: "{text[:500]}"

    Evaluate the following:
    1. Sensationalism Score (0.0 to 1.0): How clickbaity, emotional, or exaggerated is the language? (1.0 = extremely sensationalist)
    2. Logical Fallacies: List any detected fallacies (e.g., ad hominem, straw man, slippery slope).
    3. Credibility Rating (0.0 to 1.0): Based ONLY on the internal logic and tone, how credible does this sound? (1.0 = highly credible, neutral tone).
    4. Reasoning: Brief explanation.

    Return the result as a valid JSON object with keys: "sensationalism_score", "logical_fallacies" (list of strings), "credibility_rating", "reasoning".
    Do not include markdown formatting like ```json. Just the raw JSON string.
    """

    try:
        response = model.generate_content(prompt)
        # Clean up potential markdown formatting
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned_text)
        return result
    except Exception as e:
        print(f"❌ LLM Analysis Error: {e}")
        return None

def classify_comments_batch(comments: list[str]) -> dict:
    """
    Classifies a batch of comments into categories: Refuting, Supporting, Questioning, Neutral.
    Returns a dictionary mapping comment index to classification.
    """
    if not configure_genai() or not comments:
        return {}

    model = genai.GenerativeModel('gemini-2.0-flash')

    # Limit batch size to avoid token limits
    batch_comments = comments[:20] 
    
    prompt = f"""
    Classify the following comments regarding a post into one of these categories:
    - "refuting": Debunking, calling it fake, providing counter-evidence.
    - "supporting": Agreeing, confirming, saying it's true.
    - "questioning": Asking for source, skeptical but not sure.
    - "neutral": Jokes, irrelevant, or unclear.

    Comments:
    {json.dumps(batch_comments)}

    Return a JSON list of strings corresponding to the classification of each comment in order.
    Example: ["refuting", "neutral", "supporting"]
    Do not include markdown formatting.
    """

    try:
        response = model.generate_content(prompt)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        classifications = json.loads(cleaned_text)
        
        # Map back to original indices (assuming order is preserved)
        return {i: cls for i, cls in enumerate(classifications)}
    except Exception as e:
        print(f"❌ LLM Comment Classification Error: {e}")
        return {}
