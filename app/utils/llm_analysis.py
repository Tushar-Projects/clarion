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

def analyze_content_with_llm(title: str, text: str = "", comments: list[str] = None) -> dict:
    """
    Analyzes the post content for sensationalism, logical fallacies, and overall credibility.
    ALSO classifies comments in the same call to save API requests.
    Returns a dictionary with scores, reasoning, and comment classifications.
    """
    if not configure_genai():
        return None

    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    
    # Prepare comments snippet
    comments_snippet = ""
    if comments:
        # Limit to first 10 comments to save tokens
        batch_comments = comments[:10]
        comments_snippet = f"""
        User Comments to Classify:
        {json.dumps(batch_comments)}
        """

    prompt = f"""
    Analyze the following news/social media post for credibility and classify the provided user comments.
    
    Title: "{title}"
    Content Snippet: "{text[:500]}"
    {comments_snippet}

    Task 1: Evaluate the Post
    1. Sensationalism Score (0.0 to 1.0): How clickbaity/emotional? (1.0 = high)
    2. Logical Fallacies: List detected fallacies.
    3. Credibility Rating (0.0 to 1.0): How credible does the content sound? (1.0 = high)
    4. Reasoning: Brief explanation.

    Task 2: Classify Comments (if provided)
    Classify each comment into one of: "refuting", "supporting", "questioning", "neutral".
    Return a list of strings matching the order of input comments.

    Return a SINGLE JSON object with keys:
    - "sensationalism_score" (float)
    - "logical_fallacies" (list of strings)
    - "credibility_rating" (float)
    - "reasoning" (string)
    - "comment_classifications" (list of strings, or empty list if no comments)

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
