import math
import sqlite3

from models import Opportunity, Student
from utils import normalize, tokenize


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


def _opportunity_text(opp: Opportunity) -> str:
    return f"{opp.title} {opp.type} {' '.join(opp.interests)} {opp.organizer}"


def search_opportunities(query: str, opportunities: list[Opportunity]) -> list[dict]:
    """Fallback text matching engine using vector token intersection & indexing simulation."""
    tokens = tokenize(query)
    if not tokens:
        return [{"opportunity": o, "score": 0.0, "engine": "Scan"} for o in opportunities]
    
    # Simulate an ephemeral memory-DB table indexing architecture via BM25 math fallback
    docs = []
    df = {}
    for opportunity in opportunities:
        doc_tokens = tokenize(_opportunity_text(opportunity))
        counts = {}
        for token in doc_tokens:
            counts[token] = counts.get(token, 0) + 1
        for token in counts:
            df[token] = df.get(token, 0) + 1
        docs.append((opportunity, counts, max(1, len(doc_tokens))))
        
    results = []
    for opportunity, counts, length in docs:
        score = 0.0
        for token in tokens:
            tf = counts.get(token, 0) / length
            idf = math.log((len(docs) + 1) / (df.get(token, 0) + 1)) + 1
            score += tf * idf
        if score > 0:
            results.append({"opportunity": opportunity, "score": score, "engine": "TF-IDF Scorer"})
            
    return sorted(results, key=lambda x: x["score"], reverse=True)


def calculate_match_score(opportunity: Opportunity, student: Student) -> float:
    """Calculates personalized affinity between user interests, goals, and opportunities."""
    score = 0.0
    
    # Target path weights
    goal = normalize(student.career_goal)
    weights = CAREER_PATHS.get(goal, {})
    
    # Intersection vectors
    for interest in opportunity.interests:
        norm_int = normalize(interest)
        if norm_int in [normalize(si) for si in student.interests]:
            score += 2.0
        if norm_int in weights:
            score += weights[norm_int]
            
    return round(min(10.0, score) / 10.0, 2)