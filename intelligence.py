import re
import math

from models import Opportunity, Student


CAREER_PATHS = {
    "software engineer": {
        "coding": 3.0, "algorithms": 2.4, "web development": 2.0,
        "ai": 1.3, "data science": 1.0, "problem solving": 2.0, "engineering": 1.2,
    },
    "cybersecurity analyst": {
        "cybersecurity": 3.0, "coding": 2.0, "problem solving": 1.8,
        "defence tech": 1.6, "algorithms": 1.2, "ai": 0.8,
    },
    "data analyst": {
        "data science": 3.0, "ai": 2.0, "coding": 1.7, "math": 1.6,
        "research": 1.3, "business": 1.2, "public good": 0.8,
    }
}


def normalise(text: str) -> str:
    """Lowercase, strip, and sanitize string tokens."""
    return text.strip().lower()


def tokenise(text: str) -> list[str]:
    """Regex split text into alphabetic search terms."""
    return [t for t in re.findall(r'[a-z0-9]+', text.lower()) if len(t) > 1]


def search_opportunities(query: str, opportunities: list[Opportunity]) -> list[dict]:
    """Fallback text matching engine using vector token intersection & indexing simulation.
    - Calculates a word's relevance by multiplying its frequency in a document by its rarity across all documents
    - Includes BM25 (Best Matching 25), a probabilistic ranking function used by search engines to score and rank documents based on their relevance to a search query
    """
    tokens = tokenise(query)
    if not tokens:
        return [{"opportunity": o, "score": 0.0, "engine": "Scan"} for o in opportunities]
    
    #  Simulate an ephemeral memory-DB table indexing architecture via BM25 math fallback
    docs = []
    document_freq = {}
    for opportunity in opportunities:
        doc_tokens = tokenise(str(opportunity))
        counts = {}
        for token in doc_tokens:
            counts[token] = counts.get(token, 0) + 1
        for token in counts:
            document_freq[token] = document_freq.get(token, 0) + 1
        docs.append((opportunity, counts, max(1, len(doc_tokens))))
        
    results = []
    for opportunity, counts, length in docs:
        score = 0.0
        for token in tokens:
            tf = counts.get(token, 0) / length
            idf = math.log((len(docs) + 1) / (document_freq.get(token, 0) + 1)) + 1
            score += tf * idf
        if score > 0:
            results.append({"opportunity": opportunity, "score": score, "engine": "TF-IDF Scorer"})
            
    return sorted(results, key=lambda x: x["score"], reverse=True)


#  DELETE THIS
def calculate_match_score(opportunity: Opportunity, student: Student) -> float:
    """Calculates personalized affinity between user interests, goals, and opportunities."""
    score = 0.0
    
    # Target path weights
    goal = normalise(student.career_goal)
    weights = CAREER_PATHS.get(goal, {})
    
    # Intersection vectors
    for interest in opportunity.interests:
        norm_int = normalise(interest)
        if norm_int in [normalise(si) for si in student.interests]:
            score += 2.0
        if norm_int in weights:
            score += weights[norm_int]
            
    return round(min(10.0, score) / 10.0, 2)